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


def read_manifest_checksum(manifest_path: Path) -> str:
    """Extract the recorded payload sha256 from a hand-rolled manifest.yaml.

    Each manifest has exactly one `sha256: <hex>` line under `payload:`.
    Not a general YAML parser — good enough for this repo's own generated
    manifest shape, and avoids adding a YAML dependency for one field.
    """
    for line in manifest_path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("sha256:"):
            return stripped.split("sha256:", 1)[1].strip()
    raise ValueError(f"No 'sha256:' line found in {manifest_path}")


def snapshot_action(manifest_path: Path, payload_path: Path, allow_overwrite: bool) -> str:
    """Decide what an export/prepare script should do given existing state.

    Snapshots are immutable once taken (see data/raw/README.md and
    research/experiment-conventions.md: "never reuse a dataset version
    for a different snapshot"), but a committed manifest with no local
    payload (e.g. a fresh clone) must still be reproducible — see
    issue #2's Definition of Done. Returns one of:

    - "create"    — no manifest exists yet for this id, or the caller
                     passed --allow-overwrite (pre-finalisation iteration
                     only): do a full fresh extraction and (re)write both
                     the payload and the manifest.
    - "verify"     — manifest and payload both already exist: this
                      snapshot is finalised and materialised. The caller
                      must only verify the existing payload's checksum
                      against the committed manifest, never rewrite
                      either file.
    - "reproduce"  — manifest exists but the payload is missing: the
                      caller must regenerate the payload to a temporary
                      path, compare its checksum against the committed
                      manifest, and only install it (never rewrite the
                      manifest) if the checksum matches. A mismatch means
                      the source data has changed since this snapshot was
                      taken and it can no longer be reproduced — that is
                      a hard failure, not something to paper over by
                      rewriting the manifest to match new data.
    """
    if allow_overwrite or not manifest_path.exists():
        return "create"
    if payload_path.exists():
        return "verify"
    return "reproduce"
