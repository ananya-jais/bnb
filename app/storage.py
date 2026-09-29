"""
SQLite-backed store. All functions read/write veritrace.db via
app.db.get_conn() — nothing here is in-memory, so data survives
restarts and is shared correctly between uvicorn and standalone
scripts like seed_demo.py.
"""

from typing import Optional
import uuid
import json

from app.db import get_conn, init_db  # noqa: F401  (init_db re-exported for convenience)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


# ---- content ----

def save_content(content_id: str, filename: str, sha256: str, perceptual_hash: Optional[str], filepath: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO content (content_id, filename, sha256, perceptual_hash, filepath) VALUES (?, ?, ?, ?, ?)",
            (content_id, filename, sha256, perceptual_hash, filepath)
        )
        conn.commit()


def get_content(content_id: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM content WHERE content_id = ?", (content_id,)).fetchone()
        return dict(row) if row else None


def get_file_path(content_id: str) -> Optional[str]:
    record = get_content(content_id)
    return record.get("filepath") if record else None


def find_content_ids_by_sha256(sha256: str) -> list:
    with get_conn() as conn:
        rows = conn.execute("SELECT content_id FROM content WHERE sha256 = ?", (sha256,)).fetchall()
        return [r["content_id"] for r in rows]


# ---- analysis ----

def save_analysis(analysis_id: str, data: dict):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO analysis (analysis_id, data) VALUES (?, ?)",
            (analysis_id, json.dumps(data))
        )
        conn.commit()


def get_analysis(analysis_id: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT data FROM analysis WHERE analysis_id = ?", (analysis_id,)).fetchone()
        return json.loads(row["data"]) if row else None


# ---- provenance ----

def register_provenance(content_id: str, creator: str, signature: Optional[str], timestamp: str):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO provenance (content_id, creator, signature, timestamp, parent_chain)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(content_id) DO UPDATE SET creator=excluded.creator,
                   signature=excluded.signature, timestamp=excluded.timestamp""",
            (content_id, creator, signature, timestamp, json.dumps([]))
        )
        conn.commit()


def get_provenance(content_id: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM provenance WHERE content_id = ?", (content_id,)).fetchone()
        if not row:
            return None
        record = dict(row)
        record["parent_chain"] = json.loads(record["parent_chain"])
        return record


def link_edit(child_content_id: str, parent_content_id: str, edit_type: str):
    with get_conn() as conn:
        row = conn.execute("SELECT parent_chain FROM provenance WHERE content_id = ?", (child_content_id,)).fetchone()
        chain = json.loads(row["parent_chain"]) if row else []
        chain.append({"parent": parent_content_id, "edit_type": edit_type})

        conn.execute(
            """INSERT INTO provenance (content_id, creator, signature, timestamp, parent_chain)
               VALUES (?, NULL, NULL, NULL, ?)
               ON CONFLICT(content_id) DO UPDATE SET parent_chain=excluded.parent_chain""",
            (child_content_id, json.dumps(chain))
        )
        conn.commit()

def get_all_content_with_phash(exclude_id: str = None) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT content_id, perceptual_hash FROM content WHERE perceptual_hash IS NOT NULL"
        ).fetchall()
        return [dict(r) for r in rows if r["content_id"] != exclude_id]