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

## Set up the environment

The interpreter version is pinned at the repository root (`.python-version`);
this directory's own dependencies are pinned in `requirements.txt`:

```bash
# from the repository root
pip install -r tools/dataset/requirements.txt
```

## Run

```bash
# 1. dedicated export — requires repository-root .env with
#    SUPABASE_DB_HOST, SUPABASE_DB_PORT, SUPABASE_DB_NAME,
#    SUPABASE_DB_USER, SUPABASE_DB_PASSWORD (never committed)
python3 tools/dataset/export_snapshot.py

# 2. preparation — no credentials needed, reads the raw snapshot from disk
python3 tools/dataset/prepare_dataset.py
```

## Snapshots are immutable — re-running does NOT overwrite by default

Both scripts refuse to run if a manifest already exists for the current
snapshot id (see `refuse_if_already_taken` in `_common.py`), because a
taken snapshot is a fixed, versioned artefact — see `data/raw/README.md`
and `research/experiment-conventions.md` ("never reuse a dataset version
for a different snapshot"). If you see that error:

- **You need a new snapshot of current production data** — bump
  `SNAPSHOT_ID` in `_common.py` to a new dated/versioned id (e.g.
  `ps-dataset-20261015-v002`) and re-run. Row counts may legitimately
  differ from an older snapshot if production data changed; that's
  expected, not a bug — compare `manifest.yaml` files rather than
  assuming the old one is simply stale.
- **You're iterating on this same snapshot before it's committed as
  final** (e.g. fixing a bug in this script during development, before
  the snapshot has been committed/merged) — re-run with
  `--allow-overwrite`. Never use this flag to replace an
  already-committed, finalised snapshot.

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
- **`prepare_dataset.py` must never import `psycopg2` or open a database
  connection.** This is a binding repository rule (see
  `governance/research-principles.md` principle 1), not something the
  language or this repo's tooling currently enforces mechanically — there
  is no test, lint rule, or CI check yet that would fail if a future edit
  violated it. Treat any change to `prepare_dataset.py` that touches
  connections or credentials as a rule violation to flag in review, not
  something a script will catch for you. If a future change genuinely
  needs production data, that data belongs in `export_snapshot.py`
  instead.
- Nothing under `experiments/`, `research/`, or `demo/` may import from
  this directory's database-connecting code; they consume only the
  versioned snapshots these scripts produce.
