# PropertySignal Responsible Intelligence Lab

## What this is, in plain language

This is a **learning and research environment** for exploring what
"responsible AI" actually means when applied to a real-feeling problem:
helping people understand property prices and property decisions.

It is **not** PropertySignal the product, and nothing here talks to
PropertySignal's production systems or production data. It is a place
to build, break, and study small experiments — a price-prediction model,
an explanation of that model's output, a check for unfair bias, a rule
that catches when the model shouldn't be trusted — and to write down
honestly what was learned each time, including when something didn't
work.

This lab exists because building a model that predicts prices accurately
is the *easy* part of AI in a domain like property. The hard part is
everything responsible-AI practice is actually about: who could be hurt
if the model is wrong, whose interests conflict, whether an explanation
can be trusted, whether the data is fit for purpose, and whether the
people building it can prove any of that rather than just assert it.
This repository is the place those questions get worked through,
deliberately, before any of it touches a real product.

## Why it exists

Three practical reasons:

1. **To build responsible-AI skills on a real-feeling problem**, as part
   of an MSc Applied AI programme, in a setting that's more honest than
   a toy dataset but safer than production.
2. **To de-risk PropertySignal**, by surfacing what could go wrong with
   AI-assisted property intelligence *before* anyone considers building
   it into the real product — in a sandbox where mistakes cost nothing.
3. **To produce a body of reproducible, well-documented experiments**
   that are useful as evidence, teaching material, and a portfolio of
   responsible-AI practice — not just a folder of notebooks nobody can
   re-run six months later.

## This is a research/learning environment, not production PropertySignal

Worth saying plainly, because it shapes every decision in this repo:

- No experiment here connects to a production database or production
  credentials. Ever. (See `governance/research-principles.md`.)
- No output from this lab is advice a real buyer, seller, lender, or
  lawyer should act on. Everything here is illustrative.
- Nothing here is a commitment that PropertySignal the product will ever
  build any of these features. This is where ideas get tested for
  soundness, not where product roadmap gets decided.

## How PropertySignal data becomes a research snapshot

Live production data never enters an experiment directly. Instead, a
**versioned snapshot** is taken at a point in time — an export, not a
connection — and everything downstream is built from that fixed,
dated snapshot:

```text
PropertySignal source data
        ↓  (extract — never a live connection)
versioned research snapshot        e.g. ps-dataset-20260930-v001
        ↓
experiments
├── baseline ML
├── explainability
├── counterfactuals
├── fairness
├── neuro-symbolic
└── safety / OOD
        ↓
evidence + reports
        ↓
governance / responsible-AI conclusions
        ↓
optional research demo
```

Each stage is a real folder in this repo:

| Pipeline stage | Folder |
|---|---|
| Versioned research snapshot | `data/raw/`, `data/processed/`, `data/synthetic/` |
| Experiments | `experiments/<topic>/` |
| Evidence + reports | `reports/` |
| Governance / conclusions | `governance/` |
| Conventions that tie it together | `research/experiment-conventions.md` |
| Optional research demo | `demo/` |

How a snapshot is actually produced, anonymised, and versioned is the
subject of **issue #2** — this issue only establishes the convention
(`research/experiment-conventions.md`) and the rule that it must always
be a snapshot, never a live connection
(`governance/research-principles.md`).

## How experiments flow: data → model → explanation/rules/fairness/safety → evidence

A typical experiment in this lab follows the pipeline above end to end
for one question at a time. For example: *"does a baseline price model
behave differently for otherwise-similar properties in different
areas?"*

1. Start from a versioned snapshot (`data/`).
2. Train or use a baseline model (`experiments/` — baseline ML is the
   entry point for the other topics below).
3. Apply one responsible-AI lens to that model:
   - **explainability** — why did the model produce this output?
   - **counterfactuals** — what would need to change for a different
     output?
   - **fairness** — does the model behave differently across groups?
   - **neuro-symbolic** — what happens when the model's output is
     checked against an explicit rule (e.g. a legal constraint)?
   - **safety / OOD** — does the model know when it's out of its depth?
4. Record the result as evidence (`reports/`), honestly, including if
   the result is negative.
5. If the result changes what's known about a risk, update
   `governance/risk-register.md` — move it from "hypothesised" to
   "measured," with the experiment ID as the citation.

## How this connects to MSc Applied AI topics

| Lab activity | Connects to |
|---|---|
| `experiments/explainability/` | Interpretable ML, XAI methods (e.g. SHAP-style attribution) |
| `experiments/counterfactuals/` | Counterfactual reasoning, recourse |
| `experiments/fairness/` | Algorithmic fairness metrics, bias auditing |
| `experiments/neuro_symbolic/` | Neuro-symbolic AI, hybrid rule/ML systems |
| `experiments/safety/` | OOD detection, model calibration, safe failure modes |
| `governance/` | AI governance, stakeholder analysis, risk assessment |
| `research/experiment-conventions.md` | Reproducible ML engineering practice |

This structure is designed so each later issue in this milestone maps
cleanly onto one MSc topic, with a working folder already waiting for it.

## What later issues will build

This issue (**#1**) only builds the foundation: structure, governance
documents, and conventions — no data, no model, no experiment results
yet. What comes next:

- **#2** — take a safe, versioned snapshot of PropertySignal data and
  produce a Data Card describing it (provenance, fields, known
  limitations, what it should and shouldn't be used for).
- **#3+** — baseline models, then explainability, counterfactuals,
  fairness, neuro-symbolic, and safety experiments built on top of that
  snapshot, each producing a report and, where relevant, updating the
  risk register.

## Things this lab is deliberately careful to keep separate

These distinctions come up constantly in responsible-AI work, and it's
easy to blur them without noticing. This lab tries hard not to:

```text
experiment       ≠ production feature
explanation      ≠ truth
correlation      ≠ causation
model confidence ≠ correctness
listing price    ≠ verified transaction price
```

If any report, experiment, or piece of code in this repo blurs one of
these, that's a bug in the research, not a minor wording issue — see
`governance/research-principles.md`.

## Repository structure

```text
data/            versioned research snapshots (raw, processed, synthetic)
experiments/     one subfolder per responsible-AI lens (see above)
research/        cross-experiment conventions and methodology notes
governance/      stakeholder map, risk register, research principles
reports/         written evidence and findings from experiments
demo/            optional end-to-end research demo (not a product)
```

Every folder has its own short `README.md` explaining what belongs there
and why — start there before adding anything.

## What I learned (building this foundation)

Written for future-me revising MSc material, not just for this repo:

- **Responsible AI is larger than model accuracy.** A model can be
  statistically accurate and still cause harm — through how it's
  explained, who it's biased against, or how confidently it's wrong.
  None of that shows up in an accuracy metric.
- **Harms should be considered before modelling, not after.** Building
  the stakeholder map and risk register *before* writing any model code
  changes what gets built and measured later — e.g. it's why fairness
  and safety experiments are first-class folders here, not an
  afterthought bolted on at the end.
- **Stakeholders can have conflicting interests.** A pricing signal that
  benefits developers (better site selection) could work against
  neighbourhoods (feedback loops that shift a local market). There's
  often no single "correct" answer — just trade-offs that need to be
  named honestly.
- **Reproducibility is part of responsible engineering, not a nice-to-have.**
  A finding that can't be reproduced (same snapshot, same seed, same
  config) isn't evidence — it's a claim. The experiment conventions
  exist to make every future finding checkable.
- **Data provenance and intended use matter as much as the data itself.**
  The same number (a "price") means something different depending on
  whether it's a listing price or a verified transaction price, and
  research built on the wrong one produces confidently wrong
  conclusions.
- **Responsible-AI controls are both technical and governance-based.**
  A calibration check is a technical control; a documented rule that
  nobody may infer protected characteristics from location is a
  governance control. Both are necessary — a lab (or a product) with
  only one kind of control has a gap.

## License / status

Research and learning artefacts only. No production code, no production
data, no production credentials. See `governance/research-principles.md`
for the rules everything in this repository must follow.
