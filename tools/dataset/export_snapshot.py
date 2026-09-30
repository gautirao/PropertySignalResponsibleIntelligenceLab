#!/usr/bin/env python3
"""Dedicated, read-only export of the Bangalore residential-for-sale cohort
from the PropertySignal production Supabase/PostgreSQL database.

This is the ONLY code in this repository permitted to hold a production
database connection or production credentials. It does no cleaning,
feature engineering, or modelling — it extracts a cohort, writes it to a
versioned `data/raw/` snapshot, and stops. See `tools/dataset/README.md`
and `governance/research-principles.md` (principle 1) for the boundary
this script exists to enforce.

Run:
    python3 tools/dataset/export_snapshot.py

Requires SUPABASE_DB_HOST, SUPABASE_DB_PORT, SUPABASE_DB_NAME,
SUPABASE_DB_USER, SUPABASE_DB_PASSWORD in the environment (e.g. from a
repository-root `.env`, loaded by the caller or by `--env-file`). Fails
loudly if any are missing. Never prints credential values.
"""
import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2

from _common import (
    REPO_ROOT,
    SNAPSHOT_ID,
    get_git_sha,
    read_manifest_checksum,
    sha256_file,
    snapshot_action,
)

SNAPSHOT_DIR = REPO_ROOT / "data" / "raw" / SNAPSHOT_ID
PAYLOAD_PATH = SNAPSHOT_DIR / "payload" / "property_listings_bangalore_residential_sale.csv"
MANIFEST_PATH = SNAPSHOT_DIR / "manifest.yaml"

REQUIRED_ENV_VARS = [
    "SUPABASE_DB_HOST",
    "SUPABASE_DB_PORT",
    "SUPABASE_DB_NAME",
    "SUPABASE_DB_USER",
    "SUPABASE_DB_PASSWORD",
]

# Bangalore residential-for-sale cohort, per issue #2 PLAN_REVIEW:
# canonical city = Bangalore via property_listings.area_key -> areas -> cities,
# status='LIVE', archived_at IS NULL, is_duplicate=false, is_valid=true,
# listing_purpose='sale', listing_family='RESIDENTIAL'.
COHORT_SQL = """
    select
        pl.id,
        pl.listing_number,
        pl.property_type,
        pl.listing_family,
        pl.listing_purpose,
        pl.status,
        pl.is_valid,
        pl.is_duplicate,
        pl.archived_at,
        pl.price,
        pl.price_unit,
        pl.price_paise,
        pl.price_status,
        pl.built_area,
        pl.built_area_unit,
        pl.area_sqft,
        pl.super_built_area,
        pl.super_built_area_unit,
        pl.bedrooms,
        pl.bathrooms,
        pl.floor_number,
        pl.total_floors,
        pl.property_age,
        pl.facing,
        pl.furnishing_status,
        pl.latitude,
        pl.longitude,
        pl.area_key,
        pl.area_label,
        a.name as canonical_area_name,
        c.name as canonical_city_name,
        pl.seller_type,
        pl.trust_tier,
        pl.quality_score,
        pl.created_at,
        pl.updated_at,
        pl.first_published_at,
        pl.last_live_at,
        pl.status_changed_at
    from property_listings pl
    join areas a on pl.area_key = a.area_key
    join cities c on a.city_id = c.id
    where lower(c.name) = 'bangalore'
      and pl.listing_purpose = 'sale'
      and pl.status = 'LIVE'
      and pl.archived_at is null
      and pl.is_duplicate = false
      and pl.is_valid = true
      and pl.listing_family = 'RESIDENTIAL'
    order by pl.id
"""

# Explicitly NOT selected, and must never be added without a documented
# research purpose and a matching Data Card update (see issue #2):
# contact_info, contact_phone, title, description, parsed_data,
# created_by, updated_by, reviewed_by, status_changed_by_actor_id,
# rejection_reason, status_reason_note, rera_number, khata_number,
# property_tax_pid, survey_number, video_url, search_vector, geog, boundary.


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(
            f"ERROR: required environment variable {name} is not set. "
            "Export aborted; no connection was attempted with partial credentials.",
            file=sys.stderr,
        )
        sys.exit(1)
    return value


def load_dotenv_if_present(env_file: Path) -> None:
    if not env_file.exists():
        return
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def connect_read_only():
    conn = psycopg2.connect(
        host=require_env("SUPABASE_DB_HOST"),
        port=require_env("SUPABASE_DB_PORT"),
        dbname=require_env("SUPABASE_DB_NAME"),
        user=require_env("SUPABASE_DB_USER"),
        password=require_env("SUPABASE_DB_PASSWORD"),
        sslmode="require",
        connect_timeout=15,
    )
    # Belt-and-braces: reject any write attempted through this connection,
    # even accidentally, at the database session level.
    conn.set_session(readonly=True, autocommit=True)
    return conn


def run_extraction():
    conn = connect_read_only()
    cur = conn.cursor()
    cur.execute(COHORT_SQL)
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return columns, rows


def write_payload_csv(path: Path, columns, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env-file",
        default=str(REPO_ROOT / ".env"),
        help="Path to a .env file to load SUPABASE_* variables from (default: repo-root .env). Never committed.",
    )
    parser.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="Overwrite this snapshot id's existing payload/manifest. Only for iterating "
        "before this snapshot is committed as final — never use on an already-finalised "
        "snapshot; take a new snapshot id instead.",
    )
    args = parser.parse_args()

    action = snapshot_action(MANIFEST_PATH, PAYLOAD_PATH, args.allow_overwrite)

    if action == "verify":
        actual = sha256_file(PAYLOAD_PATH)
        recorded = read_manifest_checksum(MANIFEST_PATH)
        if actual == recorded:
            print(
                f"Snapshot '{SNAPSHOT_ID}' already taken; existing payload checksum "
                "matches the committed manifest. Nothing to do."
            )
            return
        print(
            f"ERROR: {PAYLOAD_PATH} exists but its sha256 ({actual}) does not match "
            f"the checksum recorded in {MANIFEST_PATH} ({recorded}). The local payload "
            "may be corrupted or stale — delete it and re-run to reproduce it from "
            "the committed manifest, or investigate before proceeding. This script "
            "will not silently overwrite a mismatched payload.",
            file=sys.stderr,
        )
        sys.exit(1)

    load_dotenv_if_present(Path(args.env_file))
    for var in REQUIRED_ENV_VARS:
        require_env(var)  # fail loudly before connecting if anything is missing

    if action == "reproduce":
        # Manifest exists (this snapshot was already taken and committed)
        # but the payload isn't on disk (e.g. a fresh clone). Regenerate
        # it to a temp path and only install it if it reproduces the
        # exact committed checksum — never rewrite the manifest here.
        columns, rows = run_extraction()
        tmp_path = PAYLOAD_PATH.with_suffix(".tmp")
        write_payload_csv(tmp_path, columns, rows)
        actual = sha256_file(tmp_path)
        recorded = read_manifest_checksum(MANIFEST_PATH)
        if actual != recorded:
            tmp_path.unlink()
            print(
                f"ERROR: re-extracting snapshot '{SNAPSHOT_ID}' from production today "
                f"produced a payload with sha256 {actual}, which does not match the "
                f"checksum committed in {MANIFEST_PATH} ({recorded}). Production data "
                "has changed since this snapshot was taken, so it can no longer be "
                "reproduced byte-for-byte. Take a new snapshot id instead of trying to "
                "reproduce this one.",
                file=sys.stderr,
            )
            sys.exit(1)
        tmp_path.replace(PAYLOAD_PATH)
        print(
            f"Reproduced payload for snapshot '{SNAPSHOT_ID}' matches the committed "
            f"manifest checksum; installed at {PAYLOAD_PATH.relative_to(REPO_ROOT)}."
        )
        print("No credential values were printed.")
        return

    # action == "create": no manifest exists yet for this id, or
    # --allow-overwrite was passed for pre-finalisation iteration.
    extracted_at = datetime.now(timezone.utc)
    columns, rows = run_extraction()
    write_payload_csv(PAYLOAD_PATH, columns, rows)

    checksum = sha256_file(PAYLOAD_PATH)
    row_count = len(rows)
    field_count = len(columns)

    manifest = f"""# Auto-generated by tools/dataset/export_snapshot.py — do not hand-edit values.
snapshot_id: {SNAPSHOT_ID}
source:
  system: PropertySignal production Supabase/PostgreSQL
  tables:
    - public.property_listings
    - public.areas
    - public.cities
  connection: read-only (conn.set_session(readonly=True))
extraction:
  extracted_at_utc: "{extracted_at.isoformat()}"
  code_commit_sha: {get_git_sha()}
cohort:
  description: Bangalore residential listings for sale (LIVE, non-duplicate, valid, non-archived)
  predicate: >
    canonical city = Bangalore via property_listings.area_key -> areas -> cities,
    listing_purpose = 'sale', status = 'LIVE', archived_at IS NULL,
    is_duplicate = false, is_valid = true, listing_family = 'RESIDENTIAL'
  row_count: {row_count}
  field_count: {field_count}
payload:
  path: payload/property_listings_bangalore_residential_sale.csv
  format: csv
  sha256: {checksum}
exclusions:
  note: >
    contact_info, contact_phone, title, description, parsed_data, all actor/reviewer
    ids, rejection/status free text, rera_number, khata_number, property_tax_pid,
    survey_number, video_url, search_vector, geog, boundary are intentionally not
    selected by this export. See tools/dataset/export_snapshot.py COHORT_SQL comment.
"""
    MANIFEST_PATH.write_text(manifest)

    print(f"Wrote {row_count} rows x {field_count} fields to {PAYLOAD_PATH.relative_to(REPO_ROOT)}")
    print(f"Manifest: {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    print("No credential values were printed.")


if __name__ == "__main__":
    main()
