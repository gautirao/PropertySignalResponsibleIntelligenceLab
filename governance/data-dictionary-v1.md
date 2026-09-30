# Data Dictionary v1 — ps-dataset-20260930-v001-processed

Companion to `governance/data-card-v1.md`. Describes every field retained
in the processed dataset (`data/processed/ps-dataset-20260930-v001-processed/`),
its unit, source table, transformation, and null semantics. The
machine-readable equivalent lives at
`data/processed/ps-dataset-20260930-v001-processed/schema.json`; this file
is the human-readable version, structured for review.

1,735 rows. Every field below has a documented research purpose — nothing
is retained just because the source table happened to have the column.

| Field | Unit / type | Source | Transformation | Null semantics |
|---|---|---|---|---|
| `research_id` | string | `property_listings.id` | `sha256(id)[:16]` | Never null. Pseudonymous, not anonymous: not reversible to the production id from this dataset alone, but anyone holding production ids can recompute the same hash and re-link a row — see `governance/data-card-v1.md`. |
| `snapshot_id` | string | (generated) | constant | Never null; identifies which raw snapshot this row was derived from. |
| `property_type` | categorical | `property_listings.property_type` | none | Never null. `apartment` \| `villa` \| `house` in this cohort. |
| `listing_family` | categorical | `property_listings.listing_family` | none | Never null; constant `RESIDENTIAL` by cohort construction. |
| `advertised_price_paise` | int64, paise (1/100 INR) | `property_listings.price_paise` | renamed from `price_paise`; rows with `price_status != 'NUMERIC'` or `price_paise IS NULL` were **excluded from this dataset**, not imputed | Never null in this dataset by construction. **This is an advertised/listing price, not a verified completed transaction price.** |
| `built_area_sqft` | float, sqft | `property_listings.built_area` + `built_area_unit` | unit-normalised; the single `sqm`-denominated row converted at 1 sqm = 10.7639104167 sqft | Never null in this cohort (0% missing in the raw snapshot). |
| `bedrooms` | int | `property_listings.bedrooms` | none | Never null in this cohort. |
| `bathrooms` | int, nullable | `property_listings.bathrooms` | none | ~33.7% null. Missing means not recorded by the lister/import, not zero bathrooms — do not impute 0. |
| `property_age` | string, nullable | `property_listings.property_age` | none | ~53.7% null. Free-text-ish categorical age band as stored; not independently verified. |
| `facing` | string, nullable | `property_listings.facing` | none | ~39.0% null. |
| `latitude_rounded` | float, degrees, 2dp | `property_listings.latitude` | rounded to 2 decimal places (~1.1 km grid) | Never null in this cohort. Coarsened for privacy — see limitations in the Data Card. Exact coordinates exist only in the gitignored raw payload. |
| `longitude_rounded` | float, degrees, 2dp | `property_listings.longitude` | rounded to 2 decimal places | Same treatment as `latitude_rounded`. |
| `canonical_area_key` | string | `areas.area_key` (via `property_listings.area_key`) | none | Never null; canonical Area identity, not free-text locality. |
| `canonical_area_name` | string | `areas.name` | none | Never null. |
| `canonical_city_name` | string | `cities.name` | none | Never null; constant `Bangalore` by cohort construction. |
| `provenance_seller_type` | categorical | `property_listings.seller_type` | renamed with `provenance_` prefix | Never null; constant `dealer` for 100% of this cohort — **context, not a usable predictive feature in this snapshot** (no variation to learn from). |
| `provenance_trust_tier` | categorical | `property_listings.trust_tier` | renamed with `provenance_` prefix | Never null; constant `D` for 100% of this cohort — same caveat as `provenance_seller_type`. |
| `provenance_created_at` | timestamp, UTC | `property_listings.created_at` | renamed with `provenance_` prefix | Never null; **all rows share one bulk-load timestamp** (2026-07-02T20:27:06.444759Z) — not an organic listing-creation time, do not use as a listing-age feature. |
| `provenance_updated_at` | timestamp, UTC | `property_listings.updated_at` | renamed with `provenance_` prefix | Never null; spans a few hours after `provenance_created_at` (bulk-load + resolution pass), not organic update activity. |

## Retained-in-raw-only, not in processed

These fields exist in `data/raw/ps-dataset-20260930-v001/` (for
traceability, or because dropping them at export time would have lost
information needed to decide the transformation) but are **not** in the
processed dataset:

| Field | Why raw-only |
|---|---|
| `id`, `listing_number` | Production keys; replaced by a pseudonymous `research_id` so this dataset alone cannot be used to look up production — see `governance/data-card-v1.md` for what this does and doesn't protect against. |
| `price`, `price_unit`, `price_status` | Superseded by `advertised_price_paise` once the price-availability filter is applied. |
| `status`, `listing_purpose`, `is_valid`, `is_duplicate`, `archived_at` | Constant by cohort construction (`LIVE` / `sale` / `true` / `false` / `NULL`) — no information content once the cohort is fixed. |
| `area_sqft`, `super_built_area`, `super_built_area_unit` | 100% null for this cohort. |
| `floor_number`, `total_floors`, `furnishing_status` | 100% null for this cohort. |
| `quality_score` | Never computed for this cohort (100% null). |
| `area_label` | Free-text locality; `canonical_area_key`/`canonical_area_name` is the documented preferred identity (issue #2: "do not rely on free-text locality when a canonical Area identity exists"). |

## Never extracted at all (excluded at the export step, never touched production beyond a schema inspection)

`contact_info`, `contact_phone`, `title`, `description`, `parsed_data`,
`created_by`/`updated_by`/`reviewed_by`/`status_changed_by_actor_id`,
`rejection_reason`, `status_reason_note`, `rera_number`, `khata_number`,
`property_tax_pid`, `survey_number`, `video_url`, `search_vector`, `geog`,
`boundary`. See `tools/dataset/export_snapshot.py` for the exact `SELECT`
list this corresponds to.
