# Research Principles

These are the rules every experiment in this lab must follow. They exist
to keep research safely separated from production, and to make findings
trustworthy enough to actually learn from. They are binding for
everything under `experiments/`, `research/`, and `data/` — not
suggestions.

## Data

1. **Never run experiments directly against the production database.**
   All experiments, notebooks, and analysis code read from a versioned
   snapshot under `data/raw/` (or a derivative in `data/processed/`),
   never a live connection to PropertySignal's production systems. This
   applies without exception to anything that does modelling, analysis,
   or experiment logic.

   The one deliberate exception is **dedicated export tooling**
   (introduced in issue #2): a small, separate piece of code whose only
   job is a read-only, credentialed extraction from production, written
   out immediately as a versioned snapshot. Its credentials are supplied
   externally at run time (e.g. an environment variable) and must never
   be committed to this repository. It must not contain, call, or be
   called by any experiment, modelling, or analysis code — its output
   (the snapshot) is the only thing that crosses that boundary. There is
   no production credential or connection string committed anywhere in
   this repository, and there must never be one.
2. **Use versioned snapshots.** Every dataset used in an experiment has
   an explicit version identifier (see
   `research/experiment-conventions.md`). "I used the data" is not a
   valid description of an experiment's input — "I used
   `ps-dataset-20260930-v001`" is.
3. **Distinguish advertised/listing price from verified transaction
   price.** These are different quantities with different reliability.
   Any dataset, chart, or report must label which one it is using, and
   must not blend them without saying so.
4. **Do not infer protected characteristics from names, locations, or
   similar proxies.** No experiment may derive a protected
   characteristic (e.g. ethnicity, religion, nationality) from a name,
   postcode, neighbourhood, or other proxy variable. This applies even
   when the inference would be "for a good reason" (e.g. a fairness
   audit) — see principle 5 for how to do that safely instead.
5. **Synthetic protected/group attributes must be clearly labelled
   research-only.** Fairness experiments that need a protected
   attribute use an explicitly synthetic, clearly labelled attribute
   from `data/synthetic/` (e.g. a randomly assigned group label for
   testing a fairness metric), never a real attribute inferred from
   real user data. Synthetic attributes must never be merged with or
   presented as real user data.

## Experiment conduct

6. **Retain experiment configuration and random seeds.** Every
   experiment records enough to be re-run and get the same result:
   config, seed, library versions, dataset version, code commit. See
   `research/experiment-conventions.md` for the exact fields.
7. **Record negative/failed experiments rather than hiding them.** An
   experiment that didn't work, or that disproved a hypothesis, is
   still recorded with its result and a short note on why it's
   considered negative/failed. Silently deleting failed runs destroys
   information about what was already tried.
8. **Distinguish evidence, interpretation, and speculation.** Every
   report should make clear which of its claims are:
   - **evidence** — a number or observation produced by a specific
     experiment;
   - **interpretation** — a reasonable reading of that evidence;
   - **speculation** — a hypothesis not yet tested.
   Do not present speculation as if it were evidence.
9. **Make experiments reproducible.** Anyone with the same dataset
   snapshot, config, and seed should be able to reproduce the same
   result by checking out the recorded commit SHA and re-running.
10. **Do not treat explainability output as ground truth.** Methods
    like feature attribution describe what a model is doing, not
    necessarily *why* the real world works that way. Explanation output
    is evidence about the model, not evidence about the property
    market. Report it as such.

## Legal / property rules used in future experiments

11. **Any legal/property rule encoded in a later experiment (e.g. a
    neuro-symbolic rule about planning law, stamp duty, tenancy rights)
    must be either:**
    - **synthetic/educational** — clearly labelled as a simplified
      teaching example, not a real legal rule someone could rely on; or
    - **backed by an authoritative source** — cited to the specific
      regulation, statute, or official guidance it's drawn from.

    A rule with neither label is not permitted in this repository.

## Scope boundary

This lab is a **research and learning environment**. Nothing here is
production PropertySignal code, and no output from this lab is
production-ready advice for any real buyer, seller, lender, or legal
decision without a separate, explicit review process outside this
repository.
