import hashlib


def create_hash(data: str) -> str:
    sha256_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
    return sha256_hash


def verify_hash(data: str, hash_to_verify: str) -> bool:
    new_hash = create_hash(data)
    return new_hash == hash_to_verify
