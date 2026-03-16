from __future__ import annotations

import sqlite3
from pathlib import Path

from llm_gateway.models import LedgerRecord


SCHEMA = """
CREATE TABLE IF NOT EXISTS request_ledger (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  task_type TEXT NOT NULL,
  success INTEGER NOT NULL,
  fallback_depth INTEGER NOT NULL,
  latency_ms REAL NOT NULL,
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  estimated_cost_usd REAL NOT NULL,
  error TEXT,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_request_ledger_created_at ON request_ledger(created_at);
"""


class SQLiteLedger:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    def record(self, record: LedgerRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO request_ledger (
                  request_id, provider, model, task_type, success, fallback_depth,
                  latency_ms, input_tokens, output_tokens, estimated_cost_usd, error, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.request_id,
                    record.provider.value,
                    record.model,
                    record.task_type.value,
                    int(record.success),
                    record.fallback_depth,
                    record.latency_ms,
                    record.input_tokens,
                    record.output_tokens,
                    record.estimated_cost_usd,
                    record.error,
                    record.created_at.isoformat(),
                ),
            )

    def recent(self, limit: int = 100) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM request_ledger
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def summary(self) -> dict[str, float | int]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                  COUNT(*) AS total_requests,
                  COALESCE(SUM(success), 0) AS successes,
                  COALESCE(AVG(latency_ms), 0) AS avg_latency_ms,
                  COALESCE(SUM(estimated_cost_usd), 0) AS total_cost_usd,
                  COALESCE(AVG(fallback_depth), 0) AS avg_fallback_depth
                FROM request_ledger
                """
            ).fetchone()
        total = int(row["total_requests"])
        successes = int(row["successes"])
        return {
            "total_requests": total,
            "success_rate": round(successes / total * 100, 2) if total else 0,
            "avg_latency_ms": round(float(row["avg_latency_ms"]), 2),
            "total_cost_usd": round(float(row["total_cost_usd"]), 6),
            "avg_fallback_depth": round(float(row["avg_fallback_depth"]), 2),
        }

