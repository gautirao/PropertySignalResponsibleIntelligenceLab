"""Shared helpers for tools/dataset/ scripts.

No production-DB-connecting code belongs here — this module is imported
by both export_snapshot.py (production access) and prepare_dataset.py (no
production access, ever), so anything here is available to both.
"""
import hashlib
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The raw snapshot id this whole issue-#2 pipeline currently targets.
# Bump this (and re-run export_snapshot.py) to cut a new dated snapshot.
SNAPSHOT_ID = "ps-dataset-20260930-v001"


def get_git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
