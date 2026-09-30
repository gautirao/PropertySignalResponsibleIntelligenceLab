# tools/dataset/

The dedicated, minimal export/preparation tooling for issue #2. This is
the **only** place in this repository permitted to hold a production
database connection or production credentials — see
`governance/research-principles.md` (principle 1) and the top-level
`README.md`'s production-connection boundary.

## The two scripts, and why they're separate

```text
export_snapshot.py   → the ONLY script with production DB access.
                        Read-only connection, fails loudly if SUPABASE_*
                        env vars are missing, writes data/raw/<snapshot>/
                        and nothing else. No cleaning, no modelling.

prepare_dataset.py   → NO production DB access, ever. Reads a data/raw/
                        snapshot already on disk and writes a cleaned,
                        minimised, research-ready data/processed/<snapshot>/.
```

Keeping them separate means a bug or change in the cleaning/preparation
logic can never accidentally gain a production connection, and every
experiment downstream can point at a `git diff` of `prepare_dataset.py`
to see exactly what transformation produced the dataset it's using.

## Run

```bash
# 1. dedicated export — requires repository-root .env with
#    SUPABASE_DB_HOST, SUPABASE_DB_PORT, SUPABASE_DB_NAME,
#    SUPABASE_DB_USER, SUPABASE_DB_PASSWORD (never committed)
python3 tools/dataset/export_snapshot.py

# 2. preparation — no credentials needed, reads the raw snapshot from disk
python3 tools/dataset/prepare_dataset.py
```

Both scripts are idempotent for a given cohort definition: re-running
`export_snapshot.py` re-extracts the same predicate against whatever
production looks like at that moment (counts may differ if production
data changed — compare `manifest.yaml` files, don't assume staleness is a
bug) and overwrites the same payload path; re-running
`prepare_dataset.py` re-derives the processed dataset from whatever raw
payload is currently on disk.

## Rules this tooling exists to enforce

- No credential value is ever printed, logged, or written to any file
  these scripts produce (manifests, schema files, stdout). Only *names*
  of missing required variables are printed, never values.
- `export_snapshot.py` uses a read-only database session
  (`conn.set_session(readonly=True)`) as a second line of defence beyond
  the credentials' own scope.
- `export_snapshot.py` fails immediately (non-zero exit, before
  connecting) if any required `SUPABASE_*` variable is missing — it must
  never silently fall back to another data source.
- `prepare_dataset.py` must never import `psycopg2` or open a database
  connection. If a future change to this file needs production data, that
  data belongs in `export_snapshot.py` instead.
- Nothing under `experiments/`, `research/`, or `demo/` may import from
  this directory's database-connecting code; they consume only the
  versioned snapshots these scripts produce.
