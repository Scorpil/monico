from dataclasses import dataclass
import uuid
import psycopg2
from monico.core.storage import (
    StorageInterface,
    StorageSetupException,
    StorageConnectionException,
    MonitorAlreadyExistsException,
    MonitorNotFoundException,
    MonitorSortingOrder,
)
from monico.core.monitor import Monitor
from monico.core.task import Task, TaskStatus
from monico.core.probe import Probe, ProbeResponseError
from monico.storage.common import TableConfig


class PgStorage(StorageInterface):
    """
    PostgreSQL storage implementation for monico.
    """

    tables: dict
    service_uri: str
    conn: psycopg2.extensions.connection

    def __init__(self, service_uri: str, prefix: str = "monico"):
        self.tables = TableConfig(
            monitors=prefix + "_monitors",
            tasks=prefix + "_tasks",
            probes=prefix + "_probes",
        )
        self.service_uri = service_uri

    def connect(self) -> None:
        try:
            self.conn = psycopg2.connect(self.service_uri)
            query_sql = "SELECT VERSION()"
            cur = self.conn.cursor()
            cur.execute(query_sql)
            _ = cur.fetchone()[0]
            cur.close()
        except psycopg2.OperationalError as e:
            raise StorageConnectionException(
                f"Could not connect to PostgreSQL storage backend: {e}"
            )

    def disconnect(self):
        self.conn.close()

    def setup(self, force=False):
        if force:
            self.teardown()

        cur = self.conn.cursor()
        try:
            cur.execute(
                f"""
                CREATE TABLE {self.tables.monitors} (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    interval INT NOT NULL,
                    body_regexp TEXT NULL,
                    last_task_at INT NULL,
                    last_probe_at INT NULL,
                    created_at INT DEFAULT EXTRACT(EPOCH FROM NOW())
                );
                CREATE INDEX {self.tables.monitors}_last_probe_at_idx
                    ON {self.tables.monitors} (last_probe_at);
                CREATE INDEX {self.tables.monitors}_created_at_idx
                    ON {self.tables.monitors} (created_at);
            """
            )
            cur.execute(
                f"""
                CREATE TYPE {self.tables.tasks}_status AS ENUM (%s, %s, %s, %s, %s);
                CREATE TABLE {self.tables.tasks} (
                    id TEXT PRIMARY KEY,
                    timestamp INT NOT NULL,
                    fk_monitor TEXT NOT NULL,
                    status {self.tables.tasks}_status NOT NULL,
                    locked_at INT NULL,
                    locked_by TEXT NULL,
                    completed_at INT NULL,
                    CONSTRAINT fk_monitor
                        FOREIGN KEY(fk_monitor)
                            REFERENCES {self.tables.monitors}(id) ON DELETE CASCADE
                );
                CREATE INDEX {self.tables.tasks}_fk_monitor_idx
                    ON {self.tables.tasks} (fk_monitor);
            """,
                (
                    TaskStatus.PENDING.value,
                    TaskStatus.RUNNING.value,
                    TaskStatus.COMPLETED.value,
                    TaskStatus.ABANDONED.value,
                    TaskStatus.FAILED.value,
                ),
            )
            cur.execute(
                f"""
                CREATE TYPE {self.tables.probes}_response_error AS ENUM (%s, %s);
                CREATE TABLE {self.tables.probes} (
                    id TEXT PRIMARY KEY,
                    timestamp INT NOT NULL,
                    fk_monitor TEXT NOT NULL,
                    fk_task TEXT NULL,
                    response_time FLOAT NULL,
                    response_code INT NULL,
                    response_error {self.tables.probes}_response_error NULL,
                    content_match TEXT NULL,
                    CONSTRAINT fk_monitor
                        FOREIGN KEY(fk_monitor)
                            REFERENCES {self.tables.monitors}(id)
                                ON DELETE CASCADE,
                    CONSTRAINT fk_task
                        FOREIGN KEY(fk_task)
                            REFERENCES {self.tables.tasks}(id)
                                ON DELETE SET NULL
                );
                CREATE INDEX {self.tables.probes}_timestamp_idx
                    ON {self.tables.probes} (timestamp);
                CREATE INDEX {self.tables.probes}_fk_monitor_idx
                    ON {self.tables.probes} (fk_monitor);
            """,
                (
                    ProbeResponseError.TIMEOUT.value,
                    ProbeResponseError.CONNECTION_ERROR.value,
                ),
            )
            cur.close()
            self.conn.commit()
        except psycopg2.errors.DuplicateTable as e:
            self.conn.rollback()
            raise StorageSetupException("Storage already initialized")

    def teardown(self):
        cur = self.conn.cursor()
        cur.execute(
            f"""
            DROP TABLE IF EXISTS {self.tables.probes};
            DROP TYPE IF EXISTS {self.tables.probes}_response_error;
            DROP TABLE IF EXISTS {self.tables.tasks};
            DROP TYPE IF EXISTS {self.tables.tasks}_status;
            DROP TABLE IF EXISTS {self.tables.monitors};
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
                f"INSERT INTO {self.tables.monitors} (id, name, endpoint, interval, body_regexp) VALUES (%s, %s, %s, %s, %s)",
                (
                    monitor.id,
                    monitor.name,
                    monitor.endpoint,
                    monitor.interval,
                    monitor.body_regexp,
                ),
            )
            self.conn.commit()
            return Monitor(
                monitor.id,
                monitor.name,
                monitor.endpoint,
                monitor.interval,
                monitor.body_regexp,
            )
        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            raise MonitorAlreadyExistsException(
                f'Monitor with ID "{monitor.id}" already exists'
            )
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def list_monitors(
        self, sort: MonitorSortingOrder = MonitorSortingOrder.CREATED_AT_ASC
    ):
        cur = self.conn.cursor()

        sort_postfix_map = {
            MonitorSortingOrder.CREATED_AT_ASC: "created_at ASC",
            MonitorSortingOrder.LAST_TASK_AT_DESC: "last_task_at DESC",
        }

        cur.execute(
            f"SELECT id, name, endpoint, interval, body_regexp, last_task_at, last_probe_at FROM {self.tables.monitors} ORDER BY {sort_postfix_map[sort]}",
        )
        rows = cur.fetchall()
        cur.close()
        return [Monitor(*row) for row in rows]

    def read_monitor(self, id):
        cur = self.conn.cursor()
        cur.execute(
            f"SELECT id, name, endpoint, interval, body_regexp, last_task_at, last_probe_at FROM {self.tables.monitors} WHERE id = %s",
            (id,),
        )
        row = cur.fetchone()
        if not row:
            raise MonitorNotFoundException(f'Monitor with ID "{id}" not found')
        cur.close()
        return Monitor(*row)

    def delete_monitor(self, id):
        cur = self.conn.cursor()
        try:
            monitor = self.read_monitor(id)
            cur.execute(f"DELETE FROM {self.tables.monitors} WHERE id = %s", (id,))
            cur.close()
            self.conn.commit()
            return monitor
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def create_task(self, task: Task):
        cur = self.conn.cursor()
        try:
            cur.execute(
                f"INSERT INTO {self.tables.tasks} (id, timestamp, fk_monitor, status) VALUES (%s, %s, %s, %s)",
                (task.id, task.timestamp, task.monitor_id, task.status.value),
            )
            cur.execute(
                f"UPDATE {self.tables.monitors} SET last_task_at = %s WHERE id = %s",
                (task.timestamp, task.monitor_id),
            )
            self.conn.commit()
            return task
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def lock_tasks(self, worker_id: str, batch_size: int) -> [Task]:
        cur = self.conn.cursor()
        try:
            cur.execute(
                f"""
                UPDATE {self.tables.tasks} SET status = %s, locked_at = EXTRACT(EPOCH FROM NOW()), locked_by = %s
                WHERE id IN (
                    SELECT id FROM {self.tables.tasks}
                    WHERE status = %s
                    ORDER BY timestamp ASC
                    LIMIT %s
                )
                RETURNING id, timestamp, fk_monitor, status, locked_at, locked_by, completed_at;
                """,
                (
                    TaskStatus.RUNNING.value,
                    worker_id,
                    TaskStatus.PENDING.value,
                    batch_size,
                ),
            )
            rows = cur.fetchall()
            self.conn.commit()
            return [Task(*row) for row in rows]
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def update_task(self, task: Task):
        cur = self.conn.cursor()
        try:
            cur.execute(
                f"""
                UPDATE {self.tables.tasks} SET
                    status = %s,
                    completed_at = %s
                WHERE id = %s
                """,
                (task.status.value, task.completed_at, task.id),
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def record_probe(self, probe: Probe):
        cur = self.conn.cursor()
        try:
            # record probe data
            cur.execute(
                f"""
                INSERT INTO {self.tables.probes} (id, timestamp, fk_monitor, fk_task, response_time, response_code, response_error, content_match)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    probe.id,
                    probe.timestamp,
                    probe.monitor_id,
                    probe.task_id,
                    probe.response_time,
                    probe.response_code,
                    probe.response_error.value if probe.response_error else None,
                    probe.content_match,
                ),
            )

            # update last probe timestamp on monitor
            cur.execute(
                f"""
                UPDATE {self.tables.monitors} SET last_probe_at = %s WHERE id = %s
            """,
                (probe.timestamp, probe.monitor_id),
            )

            # recording a probe means the task is completed
            cur.execute(
                f"""
                UPDATE {self.tables.tasks} SET status = %s WHERE id = %s
            """,
                (TaskStatus.COMPLETED.value, probe.task_id),
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def list_probes(self, monitor_id: str, limit: int = 10) -> [Probe]:
        cur = self.conn.cursor()
        cur.execute(
            f"""
            SELECT id, timestamp, fk_monitor, fk_task, response_time, response_code, response_error, content_match
            FROM {self.tables.probes}
            WHERE fk_monitor = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """,
            (monitor_id, limit),
        )
        rows = cur.fetchall()
        cur.close()
        return [Probe(*row) for row in rows]
