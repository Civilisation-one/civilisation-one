"""Versioned SHA-256 commitments for arbitrary research-artifact bytes.

The Solidity anchor contract stores the resulting bytes32 verbatim. SHA-256 is
not Ethereum's keccak256; no on-chain hashing or JSON canonicalization occurs.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from pathlib import Path

DOMAIN = b"civilisation.one/artifact/v1\x00"
SCHEMA = "civilisation.one/artifact-receipt/v1"
_DIGEST = re.compile(r"0x[0-9a-f]{64}\Z")
_CHUNK_SIZE = 1024 * 1024


def commitment(path: str | Path) -> tuple[str, int]:
    """Return (0x-prefixed digest, byte count) from exact file bytes.

    Hash input = UTF-8 domain above (including its terminal NUL) || file bytes.
    File paths, timestamps, and noncanonical JSON encodings are not hashed.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise ValueError(f"Artifact is not a regular file: {file_path}")
    digest = hashlib.sha256(DOMAIN)
    size = 0
    with file_path.open("rb") as source:
        for chunk in iter(lambda: source.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
            size += len(chunk)
    return "0x" + digest.hexdigest(), size


def make_receipt(path: str | Path) -> dict[str, str | int]:
    """Describe a commitment without embedding a private file path or bytes."""
    digest, size = commitment(path)
    return {
        "schema": SCHEMA,
        "algorithm": "sha256",
        "digest": digest,
        "size_bytes": size,
    }


def verify_receipt(path: str | Path, receipt: object) -> bool:
    """Reject malformed receipts; return False for valid but mismatched ones."""
    if not isinstance(receipt, dict) or set(receipt) != {
        "schema", "algorithm", "digest", "size_bytes"
    }:
        raise ValueError("Invalid receipt fields")
    if receipt["schema"] != SCHEMA or receipt["algorithm"] != "sha256":
        raise ValueError("Unsupported receipt schema or algorithm")
    if not isinstance(receipt["digest"], str) or not _DIGEST.fullmatch(receipt["digest"]):
        raise ValueError("Invalid bytes32 digest")
    if type(receipt["size_bytes"]) is not int or receipt["size_bytes"] < 0:
        raise ValueError("Invalid artifact size")
    digest, size = commitment(path)
    return size == receipt["size_bytes"] and hmac.compare_digest(digest, receipt["digest"])


def load_receipt(path: str | Path) -> object:
    """Read a JSON receipt; structural checks happen in verify_receipt."""
    with Path(path).open("r", encoding="utf-8") as source:
        return json.load(source)
