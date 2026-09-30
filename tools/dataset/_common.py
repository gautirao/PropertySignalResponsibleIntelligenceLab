"""Shared helpers for tools/dataset/ scripts.

No production-DB-connecting code belongs here — this module is imported
by both export_snapshot.py (production access) and prepare_dataset.py (no
production access, ever), so anything here is available to both.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The raw snapshot id this whole issue-#2 pipeline currently targets.
# Snapshots are immutable once taken (see data/raw/README.md and
# research/experiment-conventions.md: "never reuse a dataset version for
# a different snapshot"). To take a new extraction, bump this to a new
# dated/versioned id (e.g. ps-dataset-20261015-v002) instead of
# overwriting this one.
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


def refuse_if_already_taken(manifest_path: Path, snapshot_id: str, allow_overwrite: bool) -> None:
    """Enforce snapshot immutability: refuse to silently overwrite a
    manifest that already exists for this snapshot id.

    `--allow-overwrite` exists only for iterating on this snapshot before
    it is committed/finalised (e.g. re-running after a bugfix during this
    same PR). It must never be used to replace an already-committed,
    finalised snapshot — take a new versioned snapshot id instead.
    """
    if manifest_path.exists() and not allow_overwrite:
        print(
            f"ERROR: {manifest_path} already exists for snapshot '{snapshot_id}'. "
            "Snapshots are immutable once taken — see data/raw/README.md and "
            "research/experiment-conventions.md ('never reuse a dataset version "
            "for a different snapshot'). To take a new extraction, bump the "
            "snapshot id in tools/dataset/_common.py to a new version. "
            "If you are only iterating on this snapshot before it is committed "
            "as final, re-run with --allow-overwrite.",
            file=sys.stderr,
        )
        sys.exit(1)
