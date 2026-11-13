import json
import sqlite3
from pathlib import Path
from typing import Any


def _connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database_path: Path) -> None:
    with _connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT NOT NULL DEFAULT 'default',
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(messages)")}
        if "profile_id" not in columns:
            connection.execute(
                "ALTER TABLE messages ADD COLUMN profile_id TEXT NOT NULL DEFAULT 'default'"
            )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_messages_profile_conversation
            ON messages(profile_id, conversation_id, id)
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(profile_id, content)
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_memories_profile ON memories(profile_id, id)"
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS health_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT NOT NULL,
                entry_type TEXT NOT NULL CHECK(entry_type IN
                    ('food', 'workout', 'weight', 'measurement', 'activity', 'note')),
                data_json TEXT NOT NULL,
                logged_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_health_entries_profile_time "
            "ON health_entries(profile_id, logged_at DESC, id DESC)"
        )


def save_message(
    database_path: Path,
    conversation_id: str,
    role: str,
    content: str,
    profile_id: str = "default",
) -> None:
    if role not in {"user", "assistant"}:
        raise ValueError("Unsupported message role.")
    with _connect(database_path) as connection:
        connection.execute(
            "INSERT INTO messages (profile_id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
            (profile_id, conversation_id, role, content),
        )


def get_history(
    database_path: Path,
    conversation_id: str,
    limit: int = 20,
    profile_id: str = "default",
) -> list[dict[str, Any]]:
    with _connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT role, content FROM messages
            WHERE profile_id = ? AND conversation_id = ?
            ORDER BY id DESC LIMIT ?
            """,
            (profile_id, conversation_id, limit),
        ).fetchall()
    return [dict(row) for row in reversed(rows)]


def save_memory(database_path: Path, profile_id: str, content: str) -> bool:
    cleaned = content.strip()
    if not cleaned:
        raise ValueError("Memory content cannot be empty.")
    with _connect(database_path) as connection:
        cursor = connection.execute(
            "INSERT OR IGNORE INTO memories (profile_id, content) VALUES (?, ?)",
            (profile_id, cleaned),
        )
        return cursor.rowcount > 0


def get_memories(
    database_path: Path,
    profile_id: str,
    limit: int = 30,
) -> list[dict[str, Any]]:
    with _connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT id, content, created_at FROM memories
            WHERE profile_id = ?
            ORDER BY id DESC LIMIT ?
            """,
            (profile_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_memory(database_path: Path, profile_id: str, memory_id: int) -> bool:
    with _connect(database_path) as connection:
        cursor = connection.execute(
            "DELETE FROM memories WHERE profile_id = ? AND id = ?",
            (profile_id, memory_id),
        )
        return cursor.rowcount > 0


HEALTH_ENTRY_TYPES = {"food", "workout", "weight", "measurement", "activity", "note"}


def save_health_entry(
    database_path: Path,
    profile_id: str,
    entry_type: str,
    data: dict[str, Any],
    logged_at: str | None = None,
) -> int:
    """Save one owner-scoped structured health log; this does not infer completion."""
    if entry_type not in HEALTH_ENTRY_TYPES:
        raise ValueError("Unsupported health entry type.")
    if not isinstance(data, dict) or not data:
        raise ValueError("Health entry data must be a non-empty object.")
    serialized = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    with _connect(database_path) as connection:
        cursor = connection.execute(
            "INSERT INTO health_entries (profile_id, entry_type, data_json, logged_at) "
            "VALUES (?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))",
            (profile_id, entry_type, serialized, logged_at),
        )
        return int(cursor.lastrowid)


def get_health_entries(
    database_path: Path,
    profile_id: str,
    limit: int = 50,
    entry_type: str | None = None,
) -> list[dict[str, Any]]:
    safe_limit = max(1, min(int(limit), 200))
    with _connect(database_path) as connection:
        if entry_type is None:
            rows = connection.execute(
                "SELECT id, entry_type, data_json, logged_at, created_at "
                "FROM health_entries WHERE profile_id = ? "
                "ORDER BY logged_at DESC, id DESC LIMIT ?",
                (profile_id, safe_limit),
            ).fetchall()
        else:
            if entry_type not in HEALTH_ENTRY_TYPES:
                raise ValueError("Unsupported health entry type.")
            rows = connection.execute(
                "SELECT id, entry_type, data_json, logged_at, created_at "
                "FROM health_entries WHERE profile_id = ? AND entry_type = ? "
                "ORDER BY logged_at DESC, id DESC LIMIT ?",
                (profile_id, entry_type, safe_limit),
            ).fetchall()
    return [
        {
            "id": row["id"],
            "entry_type": row["entry_type"],
            "logged_at": row["logged_at"],
            "created_at": row["created_at"],
            "data": json.loads(row["data_json"]),
        }
        for row in rows
    ]
