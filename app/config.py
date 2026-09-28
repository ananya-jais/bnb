import os

RPC_URL = os.getenv("ASTITVA_RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
ABI_PATH = os.getenv("ASTITVA_ABI_PATH", "app/contract_abi.json")