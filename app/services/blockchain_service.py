import json
import logging
from pathlib import Path
from datetime import datetime, timezone

from web3 import Web3

from app import storage
from app.schemas import ProvenanceResult

log = logging.getLogger("astitva.chain")

RPC_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
ABI_PATH = Path(__file__).resolve().parent / "Provenance.json"

with open(ABI_PATH, "r", encoding="utf-8") as f:
    _artifact = json.load(f)
    _abi = _artifact["abi"] if isinstance(_artifact, dict) and "abi" in _artifact else _artifact

w3 = Web3(Web3.HTTPProvider(RPC_URL))
web3 = w3  # alias for compatibility with code that imports `web3` instead of `w3`

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=_abi,
)


def is_chain_up() -> bool:
    try:
        return w3.is_connected()
    except Exception:
        return False


def contract_deployed() -> bool:
    try:
        return len(w3.eth.get_code(contract.address)) > 0
    except Exception:
        return False


def _components(fn_name: str):
    for item in _abi:
        if item.get("type") == "function" and item["name"] == fn_name:
            outputs = item.get("outputs", [])
            if outputs and outputs[0].get("components"):
                return outputs[0]["components"]
    return []


def _to_dict(fn_name: str, raw) -> dict:
    comps = _components(fn_name)
    if not comps:
        return {}
    return {c["name"]: v for c, v in zip(comps, raw)}


def _iso(ts):
    try:
        ts = int(ts)
        if ts > 0:
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    except Exception:
        pass
    return None


def _send(fn) -> str:
    accounts = w3.eth.accounts
    sender = accounts[0] if accounts else None
    tx_hash = fn.transact({"from": sender})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt.transactionHash.hex()


# ---- writes ----

def register_on_chain(content_id: str, sha256: str, phash, creator: str) -> str:
    return _send(contract.functions.registerContent(
        content_id, sha256, phash or "", creator, "", ""
    ))


def add_edit_on_chain(content_id: str, sha256: str, phash, creator: str,
                       parent_id: str, edit_type: str) -> str:
    return _send(contract.functions.addEdit(
        content_id, sha256, phash or "", creator, parent_id, edit_type
    ))


# ---- reads ----

def get_history(content_id: str) -> list:
    raw = contract.functions.getProvenance(content_id).call()
    return [_to_dict("getProvenance", r) for r in raw]


def check_provenance(content_id: str) -> ProvenanceResult:
    not_found = ProvenanceResult(provenance_found=False, blockchain_verified=False)

    content = storage.get_content(content_id)
    if content is None:
        return not_found

    try:
        rec = _to_dict("getContent", contract.functions.getContent(content_id).call())
        if not rec.get("contentId"):
            return not_found
        verified = contract.functions.verifyContent(content_id, content["sha256"]).call()
        chain = get_history(content_id)
    except Exception as e:
        log.warning("Chain lookup failed for %s: %s", content_id, e)
        return not_found

    ids = [r.get("contentId") for r in chain]
    last = chain[-1] if chain else rec

    return ProvenanceResult(
        provenance_found=True,
        original_content_id=ids[0] if ids else content_id,
        creator=rec.get("creatorId"),
        timestamp=_iso(rec.get("timestamp")),
        edit_type=last.get("editType") or "none",
        blockchain_verified=bool(verified),
        parent_chain=ids,
    )