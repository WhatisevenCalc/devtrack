# DevTrack - Development Activity Tracker
# Copyright (c) 2026 Ivan Timov. All rights reserved.
# Proprietary and confidential.

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager


class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            data_dir = Path.home() / ".devtrack"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "devtrack.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    window_title TEXT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duration_seconds INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_app_time 
                ON sessions(app_name, start_time)
            """)

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def start_session(self, app_name: str, window_title: str = "") -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                "INSERT INTO sessions (app_name, window_title, start_time) VALUES (?, ?, ?)",
                (app_name, window_title, datetime.now().isoformat())
            )
            return cursor.lastrowid

    def end_session(self, session_id: int):
        with self._conn() as conn:
            conn.execute("""
                UPDATE sessions 
                SET end_time = ?, duration_seconds = ?, is_active = 0
                WHERE id = ?
            """, (datetime.now().isoformat(), 
                  int((datetime.now() - datetime.fromisoformat(
                      conn.execute("SELECT start_time FROM sessions WHERE id = ?", (session_id,)).fetchone()["start_time"]
                  )).total_seconds()), session_id))

    def get_active_session(self, app_name: str):
        with self._conn() as conn:
            return conn.execute(
                "SELECT * FROM sessions WHERE app_name = ? AND is_active = 1 ORDER BY start_time DESC LIMIT 1",
                (app_name,)
            ).fetchone()

    def get_sessions(self, app_name: str = None, limit: int = 100):
        with self._conn() as conn:
            if app_name:
                return conn.execute(
                    "SELECT * FROM sessions WHERE app_name = ? ORDER BY start_time DESC LIMIT ?",
                    (app_name, limit)
                ).fetchall()
            return conn.execute(
                "SELECT * FROM sessions ORDER BY start_time DESC LIMIT ?",
                (limit,)
            ).fetchall()

    def get_total_time(self, app_name: str = None):
        with self._conn() as conn:
            if app_name:
                row = conn.execute(
                    "SELECT SUM(duration_seconds) as total FROM sessions WHERE app_name = ? AND is_active = 0",
                    (app_name,)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT SUM(duration_seconds) as total FROM sessions WHERE is_active = 0"
                ).fetchone()
            return row["total"] or 0

    def clear_sessions(self, app_name: str = None):
        with self._conn() as conn:
            if app_name:
                conn.execute("DELETE FROM sessions WHERE app_name = ?", (app_name,))
            else:
                conn.execute("DELETE FROM sessions")

    def get_setting(self, key: str, default: str = "") -> str:
        with self._conn() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )


db = Database()