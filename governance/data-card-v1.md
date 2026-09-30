# Data Card v1 — ps-dataset-20260930-v001

**Dataset:** `ps-dataset-20260930-v001` (raw) →
`ps-dataset-20260930-v001-processed` (processed, modelling-ready).
**Created:** 2026-09-30. **Owner:** this lab (issue #2).
**Companion documents:** `governance/data-dictionary-v1.md` (field-level
detail), `reports/ps-dataset-20260930-v001-profiling.md` (the profiling
evidence this card's claims are based on).

## 1. What this is

A snapshot of **Bangalore residential listings for sale**, extracted
read-only from the PropertySignal production Supabase/PostgreSQL database
on 2026-09-30, via the dedicated exporter
(`tools/dataset/export_snapshot.py`) — the only code in this repository
permitted to connect to production. See
`data/raw/ps-dataset-20260930-v001/manifest.yaml` for the exact
extraction timestamp, code commit SHA, and payload checksum.

- Raw rows: 1,737.
- Processed (modelling-ready) rows: 1,735 (2 rows dropped — see §5).
- Source tables: `public.property_listings`, `public.areas`,
  `public.cities`.
- Cohort predicate: canonical city = Bangalore (via
  `property_listings.area_key -> areas -> cities`),
  `listing_family = 'RESIDENTIAL'`, `listing_purpose = 'sale'`,
  `status = 'LIVE'`, `archived_at IS NULL`, `is_duplicate = false`,
  `is_valid = true`.

## 2. Provenance

Production Supabase/PostgreSQL → read-only, credentialed extraction
(`tools/dataset/export_snapshot.py`) → versioned raw snapshot
(`data/raw/ps-dataset-20260930-v001/`) → local, no-DB-access preparation
(`tools/dataset/prepare_dataset.py`) → versioned processed dataset
(`data/processed/ps-dataset-20260930-v001-processed/`). No step after the
export script ever touches production again. See the top-level
`README.md`'s production-connection boundary and
`governance/research-principles.md` principle 1.

## 3. Intended uses

- MSc Applied AI coursework and PropertySignal-internal learning: baseline
  price-style modelling, explainability, counterfactuals, fairness
  auditing, neuro-symbolic rule checking, and OOD/safety experiments
  against a real-feeling (but not production-served) listing dataset.
- Studying *advertised* price behaviour and its relationship to listing
  attributes — not studying market value.

## 4. Prohibited / non-intended uses

- Generating real valuations, lending decisions, or legal advice for any
  actual buyer, seller, lender, or lawyer.
- Feeding directly into a production PropertySignal feature without a
  separate, explicit review process outside this repository.
- Treating `advertised_price_paise` as market value, transaction price,
  or sale price (see §6).
- Inferring protected characteristics from `canonical_area_key` /
  `canonical_area_name` or coordinates — see
  `governance/research-principles.md` principle 4.
- Drawing conclusions about **how listings arrive over time**,
  **seller-type effects**, or **trust-tier effects** from this snapshot —
  see §7; the load process makes these artefacts of ingestion, not signal.
- Re-identifying a listing or seller from `research_id`,
  `latitude_rounded`/`longitude_rounded`, or any combination of retained
  fields — see §8.

## 5. Target semantics

The target column is **`advertised_price_paise`**: the listing's
advertised/asking price, in paise, as stored in
`property_listings.price_paise`. It is deliberately **not** named
`market_value`, `property_value`, `sale_price`, or `transaction_price`.

> **`advertised_price_paise` ≠ verified completed transaction price.**
> This dataset contains no authoritative record of what any property
> actually sold for. It records what the listing asked for. Treat any
> model trained on this target as predicting *asking* price, and label
> every downstream chart, report, or claim accordingly.

Two raw rows had `price_status = 'NUMERIC'` with `price_paise IS NULL` —
a data-quality inconsistency, not a legitimate "price on request" case
(see profiling report §6). They were excluded from the processed dataset
rather than imputed; the exclusion is counted in
`data/processed/ps-dataset-20260930-v001-processed/manifest.yaml`.

## 6. Fields and minimisation

Full field-by-field documentation is in
`governance/data-dictionary-v1.md`. Summary of what was deliberately
excluded and why:

- **Direct identifiers**, never extracted at all: `contact_info`,
  `contact_phone`, names, `title`, `description`, `parsed_data`, all
  actor/reviewer ids, free-text rejection/status notes, `rera_number`,
  `khata_number`, `property_tax_pid`, `survey_number`, `video_url`.
- **Production keys** (`id`, `listing_number`) are in the raw snapshot
  only (for traceability) and replaced in the processed dataset by a
  non-reversible `research_id` (`sha256(id)[:16]`), so the processed
  dataset cannot be trivially joined back to production.
- **Exact coordinates** are treated as a quasi-identifier: the raw
  snapshot (gitignored, not distributed) carries exact `latitude`/
  `longitude`; the processed dataset carries only `latitude_rounded`/
  `longitude_rounded` (2 decimal places, ~1.1 km grid), and
  `canonical_area_key`/`canonical_area_name` is the documented primary
  location signal. A future experiment that genuinely needs finer
  resolution must request and justify it explicitly, not default to it.
- **Always-null-for-this-cohort fields** (`area_sqft`, `super_built_area`,
  `floor_number`, `total_floors`, `furnishing_status`, `quality_score`)
  are documented as absent, not silently dropped as if evaluated and
  found unnecessary.
- **Enrichment tables** (`listing_amenities`, `listing_location_features`,
  `listing_pois`, `listing_verification_dimension`) have **zero** rows for
  this cohort — genuinely unavailable in the current production data for
  this cohort, not a scope decision. Re-check when preparing a future
  snapshot; this may change as PropertySignal's data improves.

## 7. Known biases and limitations — provenance / representativeness

**This is the most important limitation in this Data Card.** Profiling
(§7 of the profiling report) found that all 1,737 residential-cohort rows
share a single `created_at` timestamp (2026-07-02T20:27:06 UTC),
`first_published_at` is NULL for all of them, `seller_type` is
`'dealer'` and `trust_tier` is `'D'` for 100% of rows, `quality_score` was
never computed, and `raw_post_id` is NULL for all 8,086
`property_listings` rows database-wide (`raw_posts` itself is empty).

This indicates the current production database's Bangalore
residential-for-sale data arrived via a **bulk import/seed process**, not
PropertySignal's normal organic listing-intake pipeline. Concretely, this
means:

- The dataset is a genuine production extract — not synthetic, not a
  fixture — but its temporal, seller-type, and trust-tier distribution is
  an artefact of one load event, not a sample of how listings naturally
  arrive.
- Any "listing volume over time," "seller-type effect," or "trust-tier
  effect" finding drawn from this snapshot would describe the import
  process, not the real listing population, and must be labelled
  **speculation, not evidence**, if reported at all (see
  `governance/research-principles.md` principle 8).
- Area coverage is broad (no single canonical Area exceeds ~6% of the
  cohort) but skewed toward outer-ring/IT-corridor areas (Whitefield,
  Electronic City, K R Puram, Varthur) — consistent with where
  apartment-heavy bulk listing data tends to concentrate, not
  independently verified as representative of Bangalore's residential
  market as a whole.
- Meaningful missingness remains even after minimisation:
  `bathrooms` ~33.7% null, `property_age` ~53.7% null, `facing` ~39.0%
  null. Models trained on this data must handle these nulls explicitly
  (e.g. a missingness indicator), not assume completeness.
- **De-identified is not anonymous.** Rounded coordinates plus canonical
  Area plus `built_area_sqft`/bedrooms/bathrooms can still be a narrow
  enough combination to be distinguishing for a specific listing in a
  sparse Area — this dataset should be handled with the same care as
  other sensitive research data (see R11 in
  `governance/risk-register.md`), not described as anonymous.

## 8. Reproducibility

Given authorised `SUPABASE_*` credentials in a local `.env`:

```bash
python3 tools/dataset/export_snapshot.py   # writes data/raw/ps-dataset-20260930-v001/
python3 tools/dataset/prepare_dataset.py   # writes data/processed/ps-dataset-20260930-v001-processed/
```

Both steps record their code commit SHA, extraction/processing timestamp,
row/field counts, and a SHA-256 checksum of the payload in their
respective `manifest.yaml`. No experiment, notebook, or analysis code
needs — or is permitted — production access; everything downstream
consumes `data/processed/ps-dataset-20260930-v001-processed/` only.

## 9. What I learned

Written for future-me revising MSc material, not just for this repo:

- **A dataset's provenance can contradict its own metadata.** `price_status`
  claiming `'NUMERIC'` while `price_paise` is NULL, and a `created_at`
  column that looks organic but is a single bulk-load timestamp, are both
  cases where trusting a field's *name* instead of checking its *actual
  distribution* would have silently produced a misleading dataset.
  Profiling before freezing a cohort isn't a formality — it's what caught
  both.
- **Representativeness is a claim, not a property.** This dataset is real
  production data, correctly extracted and minimised, and *still* not
  representative of organic listing behaviour, because of how it got into
  the database in the first place. "Real data" and "representative data"
  are different claims, and conflating them would have let a
  seller-type or timing "finding" through that was actually about the
  import script.
- **De-identification and minimisation are not the same as anonymisation.**
  Removing `contact_info`/`contact_phone`/names and coarsening coordinates
  materially reduces risk, but the combination of rounded location +
  structural attributes can still narrow to a small set of real listings.
  Calling this "anonymous" would have been a false comfort; calling it
  "minimised, still sensitive" is the honest claim.
- **Missingness has to be looked at before it's designed around.**
  `area_sqft` being 100% null for residential listings (while
  `built_area` is 100% populated) wasn't guessable from the schema alone
  — the schema has both columns and nothing tells you which one is
  actually used for which property family without querying real data.
- **Separating the export step from the preparation step is a real
  control, not ceremony.** Because `prepare_dataset.py` cannot import
  `psycopg2` or hold a connection, a future change to cleaning/feature
  logic literally cannot regain production access by accident — the
  boundary is enforced by what the file is allowed to import, not just by
  a comment saying not to.
- **Reproducibility needs a counted, not silent, definition of "dropped."**
  The 2-row price anomaly could have been silently filtered by a `dropna()`
  and nobody would have noticed. Recording the count in the manifest and
  the reason in this card is what makes the 1,737 → 1,735 transition
  auditable instead of just a smaller number appearing later.
