import hashlib


def compute_hash(image_bytes_list: list[bytes]) -> str:
    """Compute SHA-256 of concatenated image bytes for cache key."""
    combined = b"".join(image_bytes_list)
    return hashlib.sha256(combined).hexdigest()
