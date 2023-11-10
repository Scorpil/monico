import uuid
import psycopg2
from monic.core.storage import StorageInterface, StorageSetupException
from monic.core.monitor import Monitor


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

    def setup(self, force=False):
        if force:
            self.teardown()

        cur = self.conn.cursor()
        try:
            cur.execute(
                "CREATE TABLE monitors (id TEXT PRIMARY KEY, name TEXT, endpoint TEXT, interval INT)"
            )
            cur.close()
            self.conn.commit()
        except psycopg2.errors.DuplicateTable:
            raise StorageSetupException("Storage already initialized")

    def teardown(self):
        cur = self.conn.cursor()
        cur.execute("DROP TABLE IF EXISTS monitors")
        cur.close()
        self.conn.commit()

    def create_monitor(self, monitor):
        if not monitor.id:
            monitor.id = str(uuid.uuid4())
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO monitors (id, name, endpoint, interval) VALUES (%s, %s, %s, %s)",
            (monitor.id, monitor.name, monitor.endpoint, monitor.interval),
        )
        self.conn.commit()
        return Monitor(monitor.id, monitor.name, monitor.endpoint, monitor.interval)

    def list_monitors(self):
        return list(self.monitors.values())

    def read_monitor(self, id):
        return self.monitors[id]

    def update_monitor(self, monitor):
        self.monitors[monitor.id] = monitor
        return monitor

    def delete_monitor(self, id):
        del self.monitors[id]
