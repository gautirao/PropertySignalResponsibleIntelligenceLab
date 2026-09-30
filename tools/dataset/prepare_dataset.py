#!/usr/bin/env python3
"""Prepare the processed research dataset from a `data/raw/` snapshot.

This script has NO production database access and must never gain any —
see `governance/research-principles.md` (principle 1) and
`tools/dataset/README.md`. It only reads the raw snapshot CSV written by
`tools/dataset/export_snapshot.py` and writes a cleaned, minimised,
research-ready dataset to `data/processed/`.

Transformations applied (see governance/data-dictionary-v1.md for the
full field-by-field rationale):
  - drops the production `id` / `listing_number` and replaces them with a
    deterministic, non-reversible `research_id` (sha256 of the production
    id, truncated) so the processed dataset cannot be trivially joined
    back to production;
  - requires a usable advertised-price target
    (`price_status == 'NUMERIC' AND price_paise IS NOT NULL`) — rows that
    fail this are dropped and counted, not silently ignored;
  - renames `price_paise` -> `advertised_price_paise` (never "market
    value" / "sale price" — see issue #2 target-semantics requirement);
  - normalises `built_area` (+ unit) into a single `built_area_sqft`;
  - coarsens latitude/longitude to 2 decimal places (~1.1 km grid) rather
    than dropping location, because canonical Area is the primary location
    signal and exact coordinates are a quasi-identifier at listing level;
  - drops columns that are 100% null for this cohort
    (`area_sqft`, `super_built_area(+unit)`, `floor_number`,
    `total_floors`, `furnishing_status`, `quality_score`) rather than
    carrying dead columns into modelling code;
  - keeps `seller_type` / `trust_tier` / `created_at` / `updated_at` as
    `provenance_*` columns — explicitly NOT default predictive features,
    because in this cohort they are constant or bulk-load artefacts, not a
    natural distribution (see the profiling report).

Run:
    python3 tools/dataset/prepare_dataset.py
"""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from _common import REPO_ROOT, SNAPSHOT_ID, get_git_sha, sha256_file

RAW_DIR = REPO_ROOT / "data" / "raw" / SNAPSHOT_ID
RAW_PAYLOAD = RAW_DIR / "payload" / "property_listings_bangalore_residential_sale.csv"

PROCESSED_ID = f"{SNAPSHOT_ID}-processed"
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / PROCESSED_ID
PROCESSED_PAYLOAD = PROCESSED_DIR / "payload" / "bangalore_residential_sale_processed.csv"

SQM_TO_SQFT = 10.7639104167


def research_id(production_id: str) -> str:
    return hashlib.sha256(production_id.encode("utf-8")).hexdigest()[:16]


def built_area_to_sqft(row) -> float:
    if pd.isna(row["built_area"]):
        return None
    unit_value = row["built_area_unit"]
    unit = "" if pd.isna(unit_value) else str(unit_value).strip().lower()
    if unit == "sqft":
        return float(row["built_area"])
    if unit == "sqm":
        return float(row["built_area"]) * SQM_TO_SQFT
    raise ValueError(f"Unrecognised built_area_unit: {unit_value!r} — inspect before extending this mapping.")


def main():
    if not RAW_PAYLOAD.exists():
        raise SystemExit(
            f"Raw snapshot not found at {RAW_PAYLOAD}. "
            "Run tools/dataset/export_snapshot.py first (requires SUPABASE_* credentials)."
        )

    raw = pd.read_csv(RAW_PAYLOAD, dtype={"id": str})
    raw_row_count = len(raw)

    # --- target availability: require a genuinely usable advertised price ---
    price_ok = (raw["price_status"] == "NUMERIC") & raw["price_paise"].notna()
    dropped_price = raw[~price_ok]
    df = raw[price_ok].copy()

    df["research_id"] = df["id"].map(research_id)
    df["advertised_price_paise"] = df["price_paise"].astype("int64")
    df["built_area_sqft"] = df.apply(built_area_to_sqft, axis=1)
    df["latitude_rounded"] = df["latitude"].round(2)
    df["longitude_rounded"] = df["longitude"].round(2)
    df["provenance_seller_type"] = df["seller_type"]
    df["provenance_trust_tier"] = df["trust_tier"]
    df["provenance_created_at"] = df["created_at"]
    df["provenance_updated_at"] = df["updated_at"]
    df["canonical_area_key"] = df["area_key"]
    df["canonical_area_name"] = df["canonical_area_name"]
    df["canonical_city_name"] = df["canonical_city_name"]
    df["snapshot_id"] = SNAPSHOT_ID

    processed_columns = [
        "research_id",
        "snapshot_id",
        "property_type",
        "listing_family",
        "advertised_price_paise",
        "built_area_sqft",
        "bedrooms",
        "bathrooms",
        "property_age",
        "facing",
        "latitude_rounded",
        "longitude_rounded",
        "canonical_area_key",
        "canonical_area_name",
        "canonical_city_name",
        "provenance_seller_type",
        "provenance_trust_tier",
        "provenance_created_at",
        "provenance_updated_at",
    ]
    processed = df[processed_columns].sort_values("research_id").reset_index(drop=True)

    PROCESSED_PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(PROCESSED_PAYLOAD, index=False)

    checksum = sha256_file(PROCESSED_PAYLOAD)
    processed_at = datetime.now(timezone.utc)

    manifest_path = PROCESSED_DIR / "manifest.yaml"
    manifest = f"""# Auto-generated by tools/dataset/prepare_dataset.py — do not hand-edit values.
processed_id: {PROCESSED_ID}
derived_from:
  raw_snapshot_id: {SNAPSHOT_ID}
  raw_manifest: data/raw/{SNAPSHOT_ID}/manifest.yaml
preparation:
  processed_at_utc: "{processed_at.isoformat()}"
  code_commit_sha: {get_git_sha()}
  transformations:
    - "require price_status == 'NUMERIC' AND price_paise IS NOT NULL (target availability)"
    - "drop production id/listing_number, add deterministic research_id (sha256(id)[:16])"
    - "rename price_paise -> advertised_price_paise"
    - "normalise built_area(+unit) -> built_area_sqft (sqm converted at 1 sqm = 10.7639104167 sqft)"
    - "round latitude/longitude to 2 decimal places (~1.1km grid)"
    - "drop always-null columns for this cohort: area_sqft, super_built_area(+unit), floor_number, total_floors, furnishing_status, quality_score"
    - "carry seller_type/trust_tier/created_at/updated_at as provenance_* context columns, not default features"
counts:
  raw_row_count: {raw_row_count}
  dropped_missing_price_target: {len(dropped_price)}
  processed_row_count: {len(processed)}
  processed_field_count: {len(processed_columns)}
payload:
  path: payload/bangalore_residential_sale_processed.csv
  format: csv
  sha256: {checksum}
"""
    manifest_path.write_text(manifest)

    print(f"Raw rows: {raw_row_count}; dropped (no usable price target): {len(dropped_price)}; processed rows: {len(processed)}")
    print(f"Wrote {PROCESSED_PAYLOAD.relative_to(REPO_ROOT)}")
    print(f"Manifest: {manifest_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
