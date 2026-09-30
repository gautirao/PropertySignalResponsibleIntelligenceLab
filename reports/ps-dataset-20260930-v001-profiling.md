# Profiling report: ps-dataset-20260930-v001 (Bangalore residential-for-sale cohort)

**Dataset version:** `ps-dataset-20260930-v001` (raw), derived processed
dataset `ps-dataset-20260930-v001-processed`.
**Produced by:** read-only queries against the PropertySignal production
Supabase/PostgreSQL database, prior to freezing the export predicate (per
issue #2's PLAN_REVIEW step). No credential values appear below.
**Purpose:** justify the cohort predicate and document missingness before
freezing the snapshot — evidence, not assumption.

## 1. Canonical geography resolution

`cities` has one Bangalore row (`id=1`, `slug='bangalore'`, `is_active=true`)
with 497 `areas` rows pointing to it. Joining `property_listings.area_key
-> areas -> cities` and filtering to Bangalore (any status/purpose) gives
**4,722** rows.

Two join-completeness caveats, checked and found immaterial for this
cohort:
- 2,561 `property_listings` rows database-wide have `area_key IS NULL`
  (can't be attributed to any city via this join) — none of these can be
  Bangalore candidates missed by the join, since they have no area at all.
- Exactly 1 row database-wide has a non-null `area_key` with no matching
  `areas` row (an orphaned area_key) — negligible, not investigated
  further for this issue.

## 2. Eligibility filter, step by step (Bangalore rows only)

| Filter (cumulative) | Row count |
|---|---|
| city = Bangalore | 4,722 |
| + `listing_purpose = 'sale'` | 2,128 |
| + `status = 'LIVE'` | 2,128 |
| + `archived_at IS NULL` | 2,128 |
| + `is_duplicate = false` | 2,128 |
| + `is_valid = true` | 2,128 |

`status`/`archived_at`/`is_duplicate`/`is_valid` are no-ops on top of
`listing_purpose = 'sale'` for Bangalore in the current database — every
Bangalore sale row is already `LIVE`, non-archived, non-duplicate, and
valid. That may not remain true as production data changes; the filters
stay in the export predicate regardless, since the contract is defined by
the issue, not by what happens to be a no-op today.

For contrast, Bangalore `listing_purpose = 'rent'` (any status) is 2,594
rows — not part of this cohort.

## 3. Residential vs. commercial split, and the legacy-`listing_family` check

| `property_type` | `listing_family` | Count |
|---|---|---|
| apartment | RESIDENTIAL | 1,589 |
| commercial_land | COMMERCIAL | 216 |
| commercial | COMMERCIAL | 103 |
| villa | RESIDENTIAL | 76 |
| house | RESIDENTIAL | 72 |
| commercial_building | COMMERCIAL | 64 |
| warehouse | COMMERCIAL | 8 |

Total: 2,128 (matches step 2). `listing_family` is **never NULL** for any
of these 2,128 rows, and `property_type` maps to `listing_family` with no
disagreement — there are no legacy rows in this cohort needing a separate
inclusion/exclusion rule. (Database-wide, 164 `property_listings` rows do
have `listing_family IS NULL`, but none of them are in this Bangalore
sale/LIVE/valid/non-duplicate/non-archived population.)

**Residential subset = `listing_family = 'RESIDENTIAL'` → 1,737 rows**
(apartment 1,589 + villa 76 + house 72). No `residential_plot` or `land`
property types appear in this cohort (those exist system-wide, but not
among Bangalore sale/LIVE listings).

## 4. Canonical Area distribution (residential cohort, top 15 of ~70+ areas)

| Area | Count |
|---|---|
| Whitefield | 99 |
| Electronic City | 85 |
| K R Puram | 58 |
| Varthur | 56 |
| Thanisandra | 47 |
| Yelahanka | 42 |
| Sarjapur | 39 |
| JP Nagar | 37 |
| Begur | 35 |
| Sahakara Nagar | 32 |
| RR Nagar | 31 |
| Horamavu | 29 |
| Koramangala | 27 |
| Balagere | 25 |
| HSR Layout | 25 |

No single Area dominates the cohort (max share ≈ 5.7%); the long tail
extends to areas with a handful of listings each.

## 5. Missingness (residential cohort, N = 1,737)

| Field | Missing | % |
|---|---|---|
| `price_paise` | 2 | 0.1% |
| `area_sqft` | 1,737 | 100% |
| `built_area` | 0 | 0% |
| `super_built_area` | 1,737 | 100% |
| `latitude` / `longitude` | 0 | 0% |
| `bedrooms` | 0 | 0% |
| `bathrooms` | 586 | 33.7% |
| `property_age` | 934 | 53.8% |
| `facing` | 679 (≈39.1%) | 39.1% |
| `floor_number` / `total_floors` | 1,737 | 100% |
| `furnishing_status` | 1,737 | 100% |
| `quality_score` | 1,737 | 100% |

Residential listings in this cohort record area via `built_area`, not
`area_sqft` (the latter is used elsewhere, e.g. for land parcels — it is
100% populated for `commercial_land`, not shown here). `built_area_unit`
is `sqft` for 1,736 rows and `sqm` for 1 row.

`listing_residential_unit_details` (the typed detail table that also
carries `floor_number`/`total_floors`) has **zero** rows matching any
listing in this cohort — the enrichment table is simply not populated for
these listings, not merely missing individual values.

**Enrichment tables with zero coverage for this cohort:** `listing_amenities`,
`listing_location_features`, `listing_pois`, and `listing_verification_dimension`
(no `VERIFIED` badges) all return 0 matching rows. These are excluded from
the v1 export because there is nothing to export, not because they were
judged unnecessary — document as unavailable, not silently omit as if
evaluated and rejected.

## 6. Price-target anomaly (the 2 dropped rows)

Both rows with `price_paise IS NULL` have `price_status = 'NUMERIC'` (not
`'ON_REQUEST'` or similar) — i.e. the status flag claims a numeric price
exists, but no value is stored. This is a **data-quality inconsistency**,
not a legitimate "price on request" case. The processed dataset's target
filter (`price_status == 'NUMERIC' AND price_paise IS NOT NULL`) excludes
them and the preparation manifest records the count, so the exclusion is
auditable rather than silent.

Price distribution among the 1,735 rows with a usable target (advertised
price, INR, derived from `price_paise`):

| Statistic | Value (INR) |
|---|---|
| Min | ₹21,69,441 |
| Median | ₹1,31,25,373 |
| Mean | ₹1,87,92,815 |
| Max | ₹70,00,00,000 |

This is **advertised/listing price**, not verified completed transaction
price — see `governance/data-card-v1.md`.

## 7. Provenance / representativeness caveat (load-bearing)

This is the most important finding from profiling, and it shapes how this
dataset should and should not be used:

- All 1,737 residential-cohort rows share **one** `created_at` timestamp:
  `2026-07-02T20:27:06.444759Z`. `updated_at` spans the same day into the
  next (359 distinct values, up to `2026-07-03T02:06:00.911357Z`) —
  consistent with a bulk load followed by an automated area-resolution
  pass, not organic, independently-timed listing creation.
- `first_published_at` is NULL for all 1,737 rows.
- `seller_type` is `'dealer'` and `trust_tier` is `'D'` for 100% of rows —
  constants, not a real distribution.
- `quality_score` was never computed (NULL for all rows).
- Database-wide, `raw_post_id` is NULL for all 8,086 `property_listings`
  rows, and the `raw_posts` table (which would hold the original scraped
  feed post a listing was parsed from) has **zero** rows.

Together, these indicate the current production database's Bangalore
residential-for-sale data was populated by a bulk import/seed process
rather than through PropertySignal's normal organic listing-intake
pipeline. This dataset is a real production extract — not synthetic, not
fixture data — but it is **not** representative of naturally-arriving
listing volume, seasonality, seller-type mix, or trust/quality
distribution. Any finding about "how listings arrive over time",
"seller-type effects", or "trust-tier effects" drawn from this snapshot
would be an artefact of the load process, not a property of the real
listing population, and must not be reported as if it were.

## 8. What this justifies

- The cohort predicate in `tools/dataset/export_snapshot.py` (Bangalore,
  `listing_family='RESIDENTIAL'`, `listing_purpose='sale'`, `status='LIVE'`,
  `archived_at IS NULL`, `is_duplicate=false`, `is_valid=true`) is safe to
  freeze: it has no legacy-`listing_family`-NULL ambiguity to resolve.
- `built_area` (not `area_sqft`) is the correct raw area field for this
  cohort.
- The 2-row price anomaly is excluded from the modelling-ready processed
  dataset, with the exclusion counted and documented rather than hidden.
- Amenities/POIs/verification enrichment is correctly absent from v1 — not
  a bug in the export.
- The bulk-load provenance caveat must appear in the Data Card's
  limitations section, not just in this report.
