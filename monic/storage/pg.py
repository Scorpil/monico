import uuid
import psycopg2
from monic.core.storage import (
    StorageInterface,
    StorageSetupException,
    MonitorAlreadyExistsException,
    MonitorNotFoundException,
)
from monic.core.monitor import Monitor
from monic.core.probe import ProbeResponseError


class PgStorage(StorageInterface):
    """
    Memory storage implementation for monic.
    Used for testing to avoid database dependencies.
    """

    service_uri: str
    conn: psycopg2.extensions.connection

    def __init__(self, service_uri: str):
        self.service_uri = service_uri

    def connect(self):
        self.conn = psycopg2.connect(self.service_uri)
        query_sql = "SELECT VERSION()"
        cur = self.conn.cursor()
        cur.execute(query_sql)
        version = cur.fetchone()[0]
        # TODO: DEBUG Log version
        cur.close()

    def disconnect(self):
        self.conn.close()

    def setup(self, force=False):
        if force:
            self.teardown()

        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                CREATE TABLE monitors (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    interval INT NOT NULL,
                    last_probe_at INT NULL,
                    created_at INT DEFAULT EXTRACT(EPOCH FROM NOW())
                );
                CREATE INDEX last_probe_at_idx ON monitors (last_probe_at);
                CREATE INDEX created_at_idx ON monitors (created_at);
            """
            )
            cur.execute(
                """
                CREATE TYPE probe_response_error AS ENUM (%s, %s);
                CREATE TABLE probes (
                    id TEXT PRIMARY KEY,
                    timestamp INT NOT NULL,
                    fk_monitor TEXT NOT NULL,
                    response_time FLOAT NULL,
                    response_code INT NULL,
                    response_error probe_response_error NULL,
                    content_match TEXT NULL,
                    CONSTRAINT fk_monitor
                        FOREIGN KEY(fk_monitor)
                            REFERENCES monitors(id)
                );
                CREATE INDEX timestamp_idx ON probes (timestamp);
            """,
                (
                    ProbeResponseError.TIMEOUT.value,
                    ProbeResponseError.CONNECTION_ERROR.value,
                ),
            )
            cur.execute(
                """
                CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'done', 'error');
                CREATE TABLE tasks (
                    id TEXT PRIMARY KEY,
                    fk_monitor TEXT NOT NULL,
                    status task_status NOT NULL,
                    locked_at INT NULL,
                    CONSTRAINT fk_monitor
                        FOREIGN KEY(fk_monitor)
                            REFERENCES monitors(id)
                );
                CREATE INDEX fk_monitor_idx ON tasks (fk_monitor);
            """
            )
            cur.close()
            self.conn.commit()
        except psycopg2.errors.DuplicateTable:
            raise StorageSetupException("Storage already initialized")

    def teardown(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            DROP TABLE IF EXISTS tasks;
            DROP TYPE IF EXISTS task_status;
            DROP TABLE IF EXISTS probes;
            DROP TYPE IF EXISTS probe_response_error;
            DROP TABLE IF EXISTS monitors;
        """
        )
        cur.close()
        self.conn.commit()

    def create_monitor(self, monitor):
        if not monitor.id:
            monitor.id = str(uuid.uuid4())
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO monitors (id, name, endpoint, interval) VALUES (%s, %s, %s, %s)",
                (monitor.id, monitor.name, monitor.endpoint, monitor.interval),
            )
            self.conn.commit()
        except psycopg2.errors.UniqueViolation:
            raise MonitorAlreadyExistsException(
                f'Monitor with ID "{monitor.id}" already exists'
            )
        return Monitor(monitor.id, monitor.name, monitor.endpoint, monitor.interval)

    def list_monitors(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, endpoint, interval, last_probe_at FROM monitors")
        rows = cur.fetchall()
        cur.close()
        return [Monitor(*row) for row in rows]

    def read_monitor(self, id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, name, endpoint, interval FROM monitors WHERE id = %s", (id,)
        )
        row = cur.fetchone()
        if not row:
            raise MonitorNotFoundException(f'Monitor with ID "{id}" not found')
        cur.close()
        return Monitor(*row)

    def update_monitor(self, monitor):
        self.monitors[monitor.id] = monitor
        return monitor

    def delete_monitor(self, id):
        cur = self.conn.cursor()
        monitor = self.read_monitor(id)
        cur.execute("DELETE FROM monitors WHERE id = %s", (id,))
        self.conn.commit()
        cur.close()
        return monitor

    def create_task(self, monitor_id: str):
        pass

    def record_probe(self, probe):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO probes (id, timestamp, fk_monitor, response_time, response_code, response_error, content_match)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            (
                probe.id,
                probe.timestamp,
                probe.monitor_id,
                probe.response_time,
                probe.response_code,
                probe.response_error,
                probe.content_match,
            ),
        )
        cur.execute(
            """
            UPDATE monitors SET last_probe_at = %s WHERE id = %s
        """,
            (probe.timestamp, probe.monitor_id),
        )
        self.conn.commit()
        cur.close()
