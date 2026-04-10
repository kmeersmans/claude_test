"""SQLite-backed score storage for both LLM and human evaluations."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCORES_DIR = Path(__file__).resolve().parent.parent / "scores"
DB_PATH = SCORES_DIR / "scores.db"


def _get_connection() -> sqlite3.Connection:
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            judge_type  TEXT NOT NULL,          -- 'llm' or 'human'
            user_id     TEXT NOT NULL,          -- model name for LLM, person ID for human
            document    TEXT NOT NULL,          -- PDF filename
            criterion_id TEXT NOT NULL,
            score       INTEGER NOT NULL,
            justification TEXT,                 -- LLM justification or optional human comment
            created_at  TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def save_scores(
    judge_type: str,
    user_id: str,
    document: str,
    evaluations: list[dict],
) -> None:
    """Persist a batch of evaluation scores.

    Args:
        judge_type: 'llm' or 'human'.
        user_id: Identifier for the judge (model name or person).
        document: PDF filename that was evaluated.
        evaluations: List of dicts with keys: criterion_id, score, justification (optional).
    """
    conn = _get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.executemany(
        """
        INSERT INTO scores (judge_type, user_id, document, criterion_id, score, justification, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                judge_type,
                user_id,
                document,
                e["criterion_id"],
                e["score"],
                e.get("justification", ""),
                now,
            )
            for e in evaluations
        ],
    )
    conn.commit()
    conn.close()


def get_scores(
    document: str | None = None,
    judge_type: str | None = None,
) -> list[dict]:
    """Retrieve scores, optionally filtered by document and/or judge type.

    Returns:
        List of score dicts.
    """
    conn = _get_connection()
    query = "SELECT * FROM scores WHERE 1=1"
    params: list = []
    if document:
        query += " AND document = ?"
        params.append(document)
    if judge_type:
        query += " AND judge_type = ?"
        params.append(judge_type)
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
