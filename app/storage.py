"""
Dead-simple in-memory store so the team can build against a stable
interface from Day 1. Swap the dict internals for SQLite/Postgres
later — nothing in the routers needs to change if you keep these
function signatures.
"""

from typing import Dict, Optional
import uuid

_content_store: Dict[str, dict] = {}
_analysis_store: Dict[str, dict] = {}
_provenance_store: Dict[str, dict] = {}


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def save_content(content_id: str, filename: str, sha256: str, perceptual_hash: Optional[str], filepath: str):
    _content_store[content_id] = {
        "content_id": content_id,
        "filename": filename,
        "sha256": sha256,
        "perceptual_hash": perceptual_hash,
        "filepath": filepath,
    }


def get_content(content_id: str) -> Optional[dict]:
    return _content_store.get(content_id)


def save_analysis(analysis_id: str, data: dict):
    _analysis_store[analysis_id] = data


def get_analysis(analysis_id: str) -> Optional[dict]:
    return _analysis_store.get(analysis_id)


def register_provenance(content_id: str, creator: str, signature: Optional[str], timestamp: str):
    _provenance_store[content_id] = {
        "content_id": content_id,
        "creator": creator,
        "signature": signature,
        "timestamp": timestamp,
        "parent_chain": [],
    }


def get_provenance(content_id: str) -> Optional[dict]:
    return _provenance_store.get(content_id)


def link_edit(child_content_id: str, parent_content_id: str, edit_type: str):
    record = _provenance_store.setdefault(child_content_id, {
        "content_id": child_content_id,
        "creator": None,
        "signature": None,
        "timestamp": None,
        "parent_chain": [],
    })
    record["parent_chain"].append({"parent": parent_content_id, "edit_type": edit_type})