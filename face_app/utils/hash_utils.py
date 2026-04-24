"""Perceptual hashing utilities for image deduplication."""

from __future__ import annotations

import hashlib
from pathlib import Path

import imagehash
from PIL import Image as PilImage


def file_sha256(path: str | Path) -> str:
    """Return the hex SHA-256 digest of a file's raw bytes.

    Used to detect byte-identical duplicates before doing any image processing.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def perceptual_hash(path: str | Path) -> str:
    """Return the perceptual hash (pHash) of an image as a hex string.

    Two images with a Hamming distance ≤ 10 between their pHashes are
    considered near-duplicates (visually identical at different resolutions
    or with minor edits).
    """
    with PilImage.open(path) as img:
        return str(imagehash.phash(img))


def hamming_distance(hash_a: str, hash_b: str) -> int:
    """Compute the bit-level Hamming distance between two pHash hex strings."""
    h_a = imagehash.hex_to_hash(hash_a)
    h_b = imagehash.hex_to_hash(hash_b)
    return int(h_a - h_b)


def are_near_duplicates(hash_a: str, hash_b: str, threshold: int = 10) -> bool:
    """Return True if two pHash strings are within *threshold* Hamming bits."""
    return hamming_distance(hash_a, hash_b) <= threshold
