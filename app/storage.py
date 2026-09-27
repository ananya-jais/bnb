"""
SQLite-backed store. Function signatures are identical to the old
in-memory version — routers and services don't need any changes.
"""

from typing import Optional
import uuid
import json

from app.db import get_conn


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