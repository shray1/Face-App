"""Recursive image file discovery."""

from __future__ import annotations

from pathlib import Path

# All image extensions the app can process.
_IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".heic"}
)


def scan_folder(folder_path: str | Path) -> list[Path]:
    """Walk *folder_path* recursively and return absolute paths to all image files.

    Hidden files and directories (names starting with ``'.'``) are skipped.

    Args:
        folder_path: Root directory to scan.

    Returns:
        Sorted list of absolute :class:`~pathlib.Path` objects for every
        discovered image file.
    """
    root = Path(folder_path).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    results: list[Path] = []

    for path in root.rglob("*"):
        # Skip anything inside a hidden directory or a hidden file itself.
        if any(part.startswith(".") for part in path.parts[len(root.parts):]):
            continue
        if path.is_file() and path.suffix.lower() in _IMAGE_EXTENSIONS:
            results.append(path.resolve())

    results.sort()
    return results
