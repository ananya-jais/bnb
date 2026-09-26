import json
from pathlib import Path

from web3 import Web3

from app.schemas import ProvenanceResult


RPC_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

ABI_PATH = Path(__file__).resolve().parent / "Provenance.json"

with open(ABI_PATH, "r", encoding="utf-8") as f:
    ABI = json.load(f)["abi"]

web3 = Web3(Web3.HTTPProvider(RPC_URL))

contract = web3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=ABI,
)


def check_provenance(content_id: str) -> ProvenanceResult:
    try:
        content = contract.functions.getContent(content_id).call()

        return ProvenanceResult(
            provenance_found=True,
            original_content_id=content[0],
            creator=content[3],
            timestamp=str(content[4]),
            edit_type=content[6],
            blockchain_verified=True,
            parent_chain=[content[5]] if content[5] else [],
        )

    except Exception:
        return ProvenanceResult(
            provenance_found=False,
            blockchain_verified=False,
        )
    