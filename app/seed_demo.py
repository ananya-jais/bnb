# app/seed_demo.py — run with: python -m app.seed_demo <content_id> <creator_name>
import sys
from app.db import DB_PATH
from app.services.blockchain_service import register_on_chain
from app import storage

def main():
    if len(sys.argv) != 3:
        print("Usage: python -m app.seed_demo <content_id> <creator_name>")
        sys.exit(1)

    content_id, creator = sys.argv[1], sys.argv[2]
    print(f"Using DB: {DB_PATH}")

    content = storage.get_content(content_id)
    if content is None:
        print(f"Error: '{content_id}' not found in {DB_PATH}. "
              f"Check you're running this from the same folder as uvicorn.")
        sys.exit(1)

    tx = register_on_chain(content_id, content["sha256"], content["perceptual_hash"], creator)
    print(f"Registered {content_id} -> tx {tx}")

if __name__ == "__main__":
    main()