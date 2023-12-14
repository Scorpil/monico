import os
import uuid
import sqlite3
from enum import Enum
from urllib.parse import urlparse
from dataclasses import dataclass
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
from monico.storage.common import TableConfig
from monico.core.probe import Probe, ProbeResponseError


class SqliteStorage(StorageInterface):
    """
    SQLite storage implementation for monico.
    """

    tables: TableConfig
    service_uri: str
    conn: sqlite3.Connection

    def __init__(self, service_uri: str, prefix: str = "monico") -> None:
        self.tables = TableConfig(
            monitors=prefix + "_monitors",
            tasks=prefix + "_tasks",
            probes=prefix + "_probes",
        )
        self.service_uri = service_uri

    def connect(self) -> None:
        try:
            sqlite_dir = os.path.dirname(urlparse(self.service_uri).path)
            if not os.path.exists(sqlite_dir):
                os.makedirs(sqlite_dir)

            sqlite_path = urlparse(self.service_uri).path
            self.conn = sqlite3.connect(sqlite_path)
        except sqlite3.Error as e:
            raise StorageConnectionException(
                f"Could not connect to SQLite storage backend: {e}"
            )

    def disconnect(self) -> None:
        self.conn.close()

    @staticmethod
    def _to_sqlite_enum(enum: Enum):
        enum_values = ", ".join(
            [f'"{item.value}"' for item in enum.__members__.values()]
        )
        return f"({enum_values})"

    def _create_table_monitors(self, cur: sqlite3.Cursor) -> None:
        cur.execute(
            f"""
            CREATE TABLE {self.tables.monitors} (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                interval INTEGER NOT NULL,
                body_regexp TEXT NULL,
                last_task_at INT NULL,
                last_probe_at INT NULL,
                created_at INT DEFAULT CURRENT_TIMESTAMP
            );"""
        )
        cur.execute(
            f"""
            CREATE INDEX {self.tables.monitors}_last_probe_at_idx
                ON {self.tables.monitors} (last_probe_at);"""
        )
        cur.execute(
            f"""
            CREATE INDEX {self.tables.monitors}_created_at_idx
                ON {self.tables.monitors} (created_at);"""
        )

    def _create_table_tasks(self, cur: sqlite3.Cursor) -> None:
        cur.execute(
            f"""
            CREATE TABLE {self.tables.tasks} (
                id TEXT PRIMARY KEY,
                timestamp INTEGER NOT NULL,
                fk_monitor TEXT NOT NULL,
                status TEXT CHECK
                    (status IN {self._to_sqlite_enum(TaskStatus)})
                    NOT NULL,
                locked_at INTEGER NULL,
                locked_by TEXT NULL,
                completed_at INTEGER NULL,
                FOREIGN KEY(fk_monitor)
                    REFERENCES {self.tables.monitors}(id)
                        ON DELETE CASCADE
            );"""
        )
        cur.execute(
            f"""
            CREATE INDEX {self.tables.tasks}_fk_monitor_idx
                ON {self.tables.tasks} (fk_monitor);"""
        )

    def _create_table_probes(self, cur: sqlite3.Cursor) -> None:
        cur.execute(
            f"""
                CREATE TABLE {self.tables.probes} (
                    id TEXT PRIMARY KEY,
                    timestamp INTEGER NOT NULL,
                    fk_monitor TEXT NOT NULL,
                    fk_task TEXT NULL,
                    response_time FLOAT NULL,
                    response_code INTEGER NULL,
                    response_error TEXT
                        CHECK (response_error in
                            {self._to_sqlite_enum(ProbeResponseError)})
                        NULL,
                    content_match TEXT NULL,
                    FOREIGN KEY(fk_monitor)
                        REFERENCES {self.tables.monitors}(id)
                            ON DELETE CASCADE,
                    FOREIGN KEY(fk_task)
                        REFERENCES {self.tables.tasks}(id)
                            ON DELETE SET NULL
                )"""
        )

        cur.execute(
            f"""
            CREATE INDEX {self.tables.probes}_timestamp_idx
                ON {self.tables.probes} (timestamp);"""
        )
        cur.execute(
            f"""
            CREATE INDEX {self.tables.probes}_fk_monitor_idx
                    ON {self.tables.probes} (fk_monitor);"""
        )

    def setup(self, force=False):
        if force:
            self.teardown()
        cur = self.conn.cursor()
        try:
            self._create_table_monitors(cur)
            self._create_table_tasks(cur)
            self._create_table_probes(cur)
            cur.close()
            self.conn.commit()
        except sqlite3.OperationalError as e:
            raise StorageSetupException(f"Could not setup SQLite storage backend: {e}")

    def teardown(self):
        cur = self.conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS {self.tables.probes}")
        cur.execute(f"DROP TABLE IF EXISTS {self.tables.tasks}")
        cur.execute(f"DROP TABLE IF EXISTS {self.tables.monitors}")
        cur.close()
        self.conn.commit()

    def create_monitor(self, monitor: Monitor) -> Monitor:
        if not monitor.id:
            monitor.id = str(uuid.uuid4())
        cur = self.conn.cursor()
        try:
            cur.execute(
                f"""
                INSERT INTO {self.tables.monitors}
                    (id, name, endpoint, interval, body_regexp) VALUES
                    (:id, :name, :endpoint, :interval, :body_regexp)""",
                monitor.__dict__,
            )
            self.conn.commit()
            return Monitor(
                monitor.id,
                monitor.name,
                monitor.endpoint,
                monitor.interval,
                monitor.body_regexp,
            )
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise MonitorAlreadyExistsException(
                f"Monitor with ID {monitor.id} already exists"
            )
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def read_monitor(self, id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, name, endpoint, interval, body_regexp, last_task_at, last_probe_at "
            f"FROM {self.tables.monitors} WHERE id = :id",
            {"id": id},
        )
        row = cur.fetchone()
        if not row:
            raise MonitorNotFoundException(f'Monitor with ID "{id}" not found')
        cur.close()
        return Monitor(*row)

    def list_monitors(
        self, sort: MonitorSortingOrder = MonitorSortingOrder.CREATED_AT_ASC
    ):
        cur = self.conn.cursor()

        sort_postfix_map = {
            MonitorSortingOrder.CREATED_AT_ASC: "created_at ASC",
            MonitorSortingOrder.LAST_TASK_AT_DESC: "last_task_at DESC",
        }

        cur.execute(
            "SELECT id, name, endpoint, interval, body_regexp, last_task_at, last_probe_at "
            f"FROM {self.tables.monitors} ORDER BY {sort_postfix_map[sort]}",
        )
        rows = cur.fetchall()
        cur.close()
        return [Monitor(*row) for row in rows]

    def delete_monitor(self, id):
        cur = self.conn.cursor()
        try:
            monitor = self.read_monitor(id)
            cur.execute(
                f"DELETE FROM {self.tables.monitors} " "WHERE id = :id", {"id": id}
            )
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
                f"INSERT INTO {self.tables.tasks}"
                "(id, timestamp, fk_monitor, status) VALUES "
                "(:id, :timestamp, :fk_monitor, :status)",
                (task.id, task.timestamp, task.monitor_id, task.status.value),
            )
            cur.execute(
                f"UPDATE {self.tables.monitors} "
                "SET last_task_at = :last_task_at WHERE id = :id",
                {"last_task_at": task.timestamp, "id": task.monitor_id},
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
                UPDATE {self.tables.tasks} SET
                    status = :new_status,
                    locked_at = CURRENT_TIMESTAMP,
                    locked_by = :locked_by
                WHERE id IN (
                    SELECT id FROM {self.tables.tasks}
                    WHERE status = :status
                    ORDER BY timestamp ASC
                    LIMIT :limit
                )
                RETURNING id, timestamp, fk_monitor, status, locked_at, locked_by, completed_at;
                """,
                {
                    "new_status": TaskStatus.RUNNING.value,
                    "locked_by": worker_id,
                    "status": TaskStatus.PENDING.value,
                    "limit": batch_size,
                },
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
                    status = :status,
                    completed_at = :completed_at
                WHERE id = :id
                """,
                {
                    "status": task.status.value,
                    "completed_at": task.completed_at,
                    "id": task.id,
                },
            ),
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
                INSERT INTO {self.tables.probes} (
                    id, timestamp, fk_monitor, fk_task, response_time,
                    response_code, response_error, content_match
                )
                VALUES (
                    :id, :timestamp, :fk_monitor, :fk_task, :response_time,
                    :response_code, :response_error, :content_match
                )
            """,
                {
                    "id": probe.id,
                    "timestamp": probe.timestamp,
                    "fk_monitor": probe.monitor_id,
                    "fk_task": probe.task_id,
                    "response_time": probe.response_time,
                    "response_code": probe.response_code,
                    "response_error": probe.response_error.value
                    if probe.response_error
                    else None,
                    "content_match": probe.content_match,
                },
            )

            # update last probe timestamp on monitor
            cur.execute(
                f"""
                UPDATE {self.tables.monitors}
                SET last_probe_at = :last_probe_at WHERE id = :id
                """,
                {"last_probe_at": probe.timestamp, "id": probe.monitor_id},
            )

            # recording a probe means the task is completed
            cur.execute(
                f"""
                UPDATE {self.tables.tasks} SET status = :status WHERE id = :id
                """,
                {"status": TaskStatus.COMPLETED.value, "id": probe.task_id},
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
            SELECT
                id, timestamp, fk_monitor, fk_task, response_time,
                response_code, response_error, content_match
            FROM {self.tables.probes}
                WHERE fk_monitor = :fk_monitor
            ORDER BY timestamp DESC
            LIMIT :limit
        """,
            {"fk_monitor": monitor_id, "limit": limit},
        ),
        rows = cur.fetchall()
        cur.close()
        return [Probe(*row) for row in rows]
