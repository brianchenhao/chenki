from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


class PromptCache:
    """Local SQLite cache mapping prompt hashes to LLM response text."""

    def __init__(self, path: str | Path = "chenki_cache.db") -> None:
        self.path = str(path)
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt_cache (
                    prompt_hash  TEXT PRIMARY KEY,
                    response     TEXT NOT NULL,
                    created_at   TEXT NOT NULL,
                    last_hit_at  TEXT NOT NULL,
                    hit_count    INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_cache_created "
                "ON prompt_cache(created_at)"
            )

    def get(self, key: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT response FROM prompt_cache WHERE prompt_hash = ?",
                (key,),
            ).fetchone()
            return row[0] if row is not None else None

    def set(self, key: str, response: str) -> None:
        now = _utcnow_iso()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO prompt_cache
                    (prompt_hash, response, created_at, last_hit_at, hit_count)
                VALUES (?, ?, ?, ?, 0)
                """,
                (key, response, now, now),
            )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
