import imagehash
from PIL import Image

# Hamming distance threshold for "close enough to call it an edit".
# 0 = identical, 64 = completely different. 10 is a common starting point.
MATCH_THRESHOLD = 10


def compute_phash(file_path: str) -> str | None:
    """Returns a perceptual hash string for an image, or None for non-images/failures."""
    try:
        with Image.open(file_path) as img:
            return str(imagehash.phash(img))
    except Exception:
        return None  # video/audio/corrupt file — not supported yet


def hamming_distance(hash_a: str, hash_b: str) -> int:
    return imagehash.hex_to_hash(hash_a) - imagehash.hex_to_hash(hash_b)