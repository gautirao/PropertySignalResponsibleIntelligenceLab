# ps-dataset-20260930-v001-processed

Cleaned, minimised, research-ready version of
`data/raw/ps-dataset-20260930-v001/`, produced by
`tools/dataset/prepare_dataset.py` — a script with **no** production
database access.

## Reproduce

```bash
pip install -r tools/dataset/requirements.txt
# requires data/raw/ps-dataset-20260930-v001/payload/... to already exist
# (see data/raw/ps-dataset-20260930-v001/README.md); no SUPABASE_* vars needed here
python3 tools/dataset/prepare_dataset.py
```

This processed dataset is **immutable** in the same way as the raw
snapshot it's derived from: `prepare_dataset.py` refuses to overwrite an
already-taken `manifest.yaml`/payload for this processed id — see
`tools/dataset/README.md`. A fresh raw snapshot gets a new
`SNAPSHOT_ID`, which yields a new `PROCESSED_ID` derived from it
automatically.

## Row counts

- Raw snapshot: 1,737 rows (Bangalore residential-for-sale cohort).
- Dropped: 2 rows where `price_status == 'NUMERIC'` but `price_paise` was
  NULL — a data-quality inconsistency in the source data (not an
  "on request" price), so these rows have no usable advertised-price
  target and are excluded, not imputed.
- Processed: **1,735 rows**, 19 fields. See `schema.json` for every field.

## What changed relative to the raw snapshot

See `manifest.yaml` for the exact transformation list and
`schema.json` for field-by-field detail. In short:

- production `id` / `listing_number` replaced by a pseudonymous
  `research_id` (sha256 of the production id, truncated) — not reversible
  from this dataset alone, but recomputable by anyone who already holds
  production ids, so it removes casual/accidental linkage, not linkage by
  someone with the source data;
- `price_paise` renamed `advertised_price_paise` (never "market value" /
  "sale price" — see `governance/data-card-v1.md`);
- `built_area` (+ unit) normalised into a single `built_area_sqft`;
- latitude/longitude rounded to 2 decimal places (~1.1 km) — a privacy
  coarsening, not a modelling choice; canonical Area is the primary
  location signal;
- columns that are 100% null for this cohort dropped;
- `seller_type` / `trust_tier` / `created_at` / `updated_at` kept only as
  `provenance_*` columns, since in this cohort they are constant or a
  bulk-load artefact rather than a natural, informative distribution.

## Before using this in an experiment

Read `governance/data-card-v1.md` first. In particular:

- `advertised_price_paise` is an advertised/listing price, **not** a
  verified completed transaction price.
- This cohort was created in a small number of bulk-load batches on
  2026-07-02 (see `provenance_created_at`), not through organically-timed
  listings — it is not necessarily representative of "typical"
  PropertySignal listing activity or seasonality.
- `provenance_seller_type` and `provenance_trust_tier` do not vary in
  this snapshot; do not use them as predictive features expecting a
  signal that doesn't exist yet in this data.

## Layout

```text
ps-dataset-20260930-v001-processed/
├── README.md        (this file)
├── manifest.yaml     (derivation, transformations, counts, commit SHA, checksum)
├── schema.json       (field-by-field documentation)
└── payload/          (gitignored — the actual CSV)
```

See `data/processed/README.md` for the general convention.
