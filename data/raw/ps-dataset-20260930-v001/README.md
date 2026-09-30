# ps-dataset-20260930-v001 (raw)

First versioned research snapshot for issue #2: Bangalore residential
listings for sale, extracted read-only from the PropertySignal production
Supabase/PostgreSQL database by the dedicated exporter
(`tools/dataset/export_snapshot.py`).

## Reproduce

```bash
pip install -r tools/dataset/requirements.txt
# repository-root .env must contain SUPABASE_DB_HOST, SUPABASE_DB_PORT,
# SUPABASE_DB_NAME, SUPABASE_DB_USER, SUPABASE_DB_PASSWORD (never committed)
python3 tools/dataset/export_snapshot.py
```

This snapshot is **immutable**: `export_snapshot.py` refuses to overwrite
`payload/property_listings_bangalore_residential_sale.csv` or
`manifest.yaml` once they exist for this snapshot id — see
`tools/dataset/README.md`. Re-running the command above against an
already-taken snapshot is expected to fail with that immutability error;
that's working as intended, not a bug. A fresh extraction against
whatever production looks like today requires a **new** snapshot id
(bump `SNAPSHOT_ID` in `tools/dataset/_common.py`), so that a row-count
difference from changed production data is visible as a new, separately
versioned snapshot rather than a silent overwrite of this one.

## What this is

- Source: `public.property_listings` joined to `public.areas` and
  `public.cities`, via a **read-only** connection.
- Cohort predicate (see `manifest.yaml` and
  `tools/dataset/export_snapshot.py` for the exact SQL): canonical city =
  Bangalore (via `area_key -> areas -> cities`), `listing_purpose='sale'`,
  `status='LIVE'`, `archived_at IS NULL`, `is_duplicate=false`,
  `is_valid=true`, `listing_family='RESIDENTIAL'`.
- Row/field counts, extraction timestamp, code commit SHA, and a SHA-256
  checksum of the payload are recorded in `manifest.yaml`.
- Field-by-field provenance, type, and missingness notes are in
  `schema.json`.

## What this is not

- Not de-identified. Direct identifiers (`contact_info`, `contact_phone`,
  names, free text) were never selected by the export query in the first
  place — see the exclusion list in `export_snapshot.py` — but this raw
  snapshot still carries the production `id`/`listing_number` and exact
  latitude/longitude, and is treated as sensitive. De-identification and
  coordinate coarsening happen in the **processed** dataset
  (`data/processed/ps-dataset-20260930-v001-processed/`), not here.
- Not a random or representative sample of "PropertySignal listings" in
  general — see the profiling report
  (`reports/ps-dataset-20260930-v001-profiling.md`) for a load-bearing
  caveat: this cohort was created in a small number of bulk-load batches,
  not through organic, independently-timed user listings.

## Layout

```text
ps-dataset-20260930-v001/
├── README.md        (this file)
├── manifest.yaml     (provenance, predicate, counts, commit SHA, checksum)
├── schema.json       (field-by-field documentation)
└── payload/          (gitignored — the actual CSV extract)
```

See `data/raw/README.md` for the general convention this snapshot follows.
