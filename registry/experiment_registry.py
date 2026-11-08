"""
SQLite-backed registry for cultivation experiments.

Tracks experiment metadata, reactor assignments, and sensor coverage
per reactor. Includes duplicate detection: experiments claiming the
same reactors over overlapping dates with the same strain are flagged
for review before any merge or deletion.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Generator, Optional


@dataclass
class Experiment:
    experiment_id: str
    strain_name: str
    start_date: date
    end_date: date
    reactors: list[str] = field(default_factory=list)


@dataclass
class DuplicateCandidate:
    id_a: str
    id_b: str
    strain_name: str
    shared_reactors: list[str]


class ExperimentRegistry:
    """SQLite-backed registry for cultivation experiments."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        self._init_schema()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    strain_name   TEXT NOT NULL,
                    start_date    TEXT NOT NULL,
                    end_date      TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS experiment_reactors (
                    experiment_id TEXT NOT NULL
                        REFERENCES experiments(experiment_id) ON DELETE CASCADE,
                    reactor_id    TEXT NOT NULL,
                    PRIMARY KEY (experiment_id, reactor_id)
                );
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id            INTEGER PRIMARY KEY,
                    experiment_id TEXT NOT NULL
                        REFERENCES experiments(experiment_id) ON DELETE CASCADE,
                    reactor_id    TEXT NOT NULL,
                    timestamp     TEXT NOT NULL,
                    sensor_key    TEXT NOT NULL,
                    value         REAL
                );
                CREATE INDEX IF NOT EXISTS idx_readings_lookup
                    ON sensor_readings(experiment_id, reactor_id, sensor_key);
            """)

    def register(self, exp: Experiment) -> None:
        """Add an experiment. Raises if the ID already exists."""
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO experiments VALUES (?, ?, ?, ?)",
                (exp.experiment_id, exp.strain_name,
                 str(exp.start_date), str(exp.end_date)),
            )
            conn.executemany(
                "INSERT INTO experiment_reactors VALUES (?, ?)",
                [(exp.experiment_id, r) for r in exp.reactors],
            )

    def ingest_readings(
        self,
        experiment_id: str,
        reactor_id: str,
        sensor_key: str,
        timestamps: list,
        values: list[Optional[float]],
    ) -> int:
        """Bulk-insert cleaned sensor readings. Returns row count."""
        rows = [
            (experiment_id, reactor_id, str(ts), sensor_key, v)
            for ts, v in zip(timestamps, values)
            if v is not None
        ]
        with self._connect() as conn:
            conn.executemany(
                "INSERT INTO sensor_readings "
                "(experiment_id, reactor_id, timestamp, sensor_key, value) "
                "VALUES (?, ?, ?, ?, ?)",
                rows,
            )
        return len(rows)

    def find_duplicate_candidates(self) -> list[DuplicateCandidate]:
        """Return pairs of experiments that likely represent the same run.

        Two experiments are candidates if they share at least one reactor,
        the same strain name, and overlapping date ranges.
        """
        query = """
            SELECT a.experiment_id              AS id_a,
                   b.experiment_id              AS id_b,
                   a.strain_name,
                   GROUP_CONCAT(ar.reactor_id)  AS shared_reactors
            FROM experiments a
            JOIN experiments b
                ON  b.experiment_id > a.experiment_id
                AND a.strain_name   = b.strain_name
                AND a.start_date   <= b.end_date
                AND a.end_date     >= b.start_date
            JOIN experiment_reactors ar ON ar.experiment_id = a.experiment_id
            JOIN experiment_reactors br
                ON  br.experiment_id = b.experiment_id
                AND br.reactor_id    = ar.reactor_id
            GROUP BY a.experiment_id, b.experiment_id
        """
        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
        return [
            DuplicateCandidate(
                id_a=r["id_a"], id_b=r["id_b"],
                strain_name=r["strain_name"],
                shared_reactors=r["shared_reactors"].split(","),
            )
            for r in rows
        ]

    def sensor_coverage(self, experiment_id: str) -> dict[str, dict[str, int]]:
        """Return {reactor_id: {sensor_key: row_count}} for one experiment."""
        query = """
            SELECT reactor_id, sensor_key, COUNT(*) AS n
            FROM sensor_readings
            WHERE experiment_id = ?
            GROUP BY reactor_id, sensor_key
            ORDER BY reactor_id, sensor_key
        """
        with self._connect() as conn:
            rows = conn.execute(query, (experiment_id,)).fetchall()
        coverage: dict[str, dict[str, int]] = {}
        for row in rows:
            coverage.setdefault(row["reactor_id"], {})[row["sensor_key"]] = row["n"]
        return coverage
