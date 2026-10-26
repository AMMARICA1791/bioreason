# BioReason

**Evidence-linked biomedical literature triage — experimental prototype v0.2**

BioReason is a public, source-available research prototype that turns bibliographic metadata into traceable, explicitly *unvalidated* research questions. It is **not** a scientific discovery engine, a clinical tool, or a validated autonomous multi-agent system.

## Problem and scope

Biomedical literature is dispersed across publications and databases. BioReason explores a narrow, auditable baseline for literature triage. Multi-agent approaches to scientific research already exist; BioReason does not claim to have invented the approach. Its immediate contribution is a reproducible, deterministic pipeline whose outputs and limitations can be inspected.

## Implemented pipeline

| Role | Current behavior |
| --- | --- |
| Scout | Fetches up to 25 Europe PMC metadata records, or reads local JSON |
| Analyst | Counts repeated words in **titles**, not full-text findings |
| Inventor | Poses a tentative question from repeated title terms |
| Critic | Flags title-only inference, causal uncertainty, and missing DOIs |
| Validator | Counts records with source and ID; **does not verify findings** |
| Builder | Records pipeline execution |
| Auditor | Records that limitations were reported |
| Coordinator | Combines results into JSON |

**Architecture disclosure:** The default CLI executes eight bounded deterministic agent roles with hash-linked handoffs and an explicit audit. An opt-in GitHub Actions workflow can give **each of the eight roles its own inference turn on the same locally loaded Qwen model**, chaining proposals through the council. The roles are not eight separately hosted or trained models. Deterministic validation gates remain in force; model suggestions never establish scientific facts. Scheduled runs now include two additional full-eight-role deliberation rounds and a bounded record of correctable errors carried between successful runs via GitHub Actions cache. This is **prompt-level procedural adaptation**, not model training or proven accuracy improvement. Scientific validation and continuous real-time monitoring remain unimplemented.

## Run

Python 3.10+; deterministic mode has no runtime third-party dependencies. The separate optional local-model workflow installs PyTorch and Transformers on GitHub Actions.

```bash
PYTHONPATH=src python -m bioreason 'CRISPR AND cancer' --limit 10
PYTHONPATH=src python -m bioreason 'example query' --input examples/papers.json
PYTHONPATH=src python -m unittest discover -s tests -v
```

The online command requires Europe PMC access. Offline fixtures and unit tests require no network. The repository currently has **57 offline tests**, including biomedical cross-topic regression tests, source/DOI checks, eight-role inference-adapter coverage, discussion chaining, and safe memory replay; GitHub Actions has executed the Python 3.10–3.13 test matrix successfully. Passing software tests does **not** establish scientific accuracy.

Input: JSON array of objects with `title`, `id`, `source`, `doi`, optionally `year`. Output: JSON printed to stdout. Example records are synthetic.

## Council dialogue and corrective memory

The [model-backed council workflow](.github/workflows/model-council.yml) first executes all eight roles on ten live Europe PMC bibliographic records, then conducts **two further conversation rounds** in which all eight roles respond to recent colleagues' replies. The complete dialogue uses hash-linked messages and is exported as a GitHub Actions artifact.

After each reply, deterministic checks flag three narrowly defined **process issues**: missing source identifiers in roles expected to cite records, DOI values absent from the retrieved records, and verbatim unchanged revisions. Only those issue **codes** are carried into later prompts as corrective lessons; model-generated prose is never stored as trusted future instructions. A JSON lessons file is restored and saved using GitHub Actions cache after successful cycles. Cache data may be evicted; every run additionally publishes the state in its artifact. Improvement in scientific quality is **not** assumed or claimed, and this procedure does **not** update Qwen weights.

## Scientific quality correction

A model-generated cross-topic proposal previously linked cervical cancer
diagnosis to glaucoma retinal photographs without joint source evidence.
BioReason now applies an independent **evidence-coherence screening gate**
to every Inventor reply, passes blocking reasons to reviewers, and holds
unsupported links for human scientific assessment. Europe PMC core records
provide bounded abstract excerpts where available. A set of ten synthetic
positive/negative regression cases exercises both the false-release and
over-hold paths (10/10 cases passed in [GitHub Actions](https://github.com/AMMARICA1791/bioreason/actions/runs/40263193884)); this is **not** a measure of clinical accuracy.

See [Scientific Quality Gate](SCIENTIFIC_QUALITY_GATE.md) for scope,
limitations, counterexamples, and the future blinded benchmark.

## Focused literature and falsifiable proposals

The current quality pilot draws a **single coherent biomedical topic** (cervical
cancer plus AI research) from Europe PMC. If the 2026 date window has too few
traceable records, the collector extends the date window to 2025–2026 rather
than combining unrelated medical specialties or inventing evidence.

[Focused-source proof](https://github.com/AMMARICA1791/bioreason/actions/runs/40314598414)
retrieved **nine relevant live records**. This validates retrieval coherence,
not scientific causality. The Inventor must pose a narrow research question
supported by at most three actually supplied source identifiers, or abstain.
Catalogue-style questions about general AI applications are held by the
independent quality gate.

## Direct test of whether peer critique adds value

[The predeclared experiment](EVALUATION_PROTOCOL.md) compares one Qwen
Inventor reply without peers to the first and last council Inventor replies
on the **same live bibliography and model**. [A separate verification
script](scripts/evaluate_run.py) independently recomputes all proxy scores
from the archived, hash-linked trace and **reports regressions as well as
improvements**. It never labels machine-readable formatting as scientific
truth; the multi-agent arm uses more inference than the solo arm.

An actual prior-council trace revealed that the rolling four-message window
dropped the Critic's earlier objection before Inventor's revision. The
[deliberation logic](src/bioreason/deliberation.py) now delivers the actual
earlier objection, validation feedback and exact blocking reasons **directly**
to Inventor for a new attempt. Sources are suggested for review rather than
silently inserted into the model's answer. The regression is tested.

## Evidence and provenance

| Claim | Supporting reference | Not established |
| --- | --- | --- |
| Europe PMC provides a literature search API | [1] | BioReason scientific accuracy |
| OpenAlex provides scholarly metadata APIs | [2] | An implemented OpenAlex integration |
| Agent-based workflows are used in biological research | [3] | BioReason originality or effectiveness |
| Multi-agent bioinformatics is an active research field | [4] | Commercial demand |

### References

1. Europe PMC, *RESTful Web Service*: https://europepmc.org/RestfulWebService
2. OpenAlex, *API documentation*: https://docs.openalex.org/
3. *A multi-agent system for automating scientific discovery*, Nature (2026): https://doi.org/10.1038/s41586-026-10652-y
4. *The next paradigm in bioinformatics: a review of multi-agent systems and foundational models for end-to-end scientific discovery*, Briefings in Bioinformatics (2026): https://doi.org/10.1093/bib/bbag245

These are background references, **not BioReason experimental results**. Bibliographic links and publication details should be independently checked before relying on them in a scientific publication.

## Known limitations

- Title co-occurrence is a weak signal, not a mechanism, causal relationship, or discovery.
- No full-text review, study-quality assessment, retraction checks, or patent/novelty search.
- A DOI can be absent from a valid record. Source plus ID indicates traceability, not scientific correctness.
- No measured performance, accuracy, customer demand, time savings, or financial return.
- Online retrieval depends on the Europe PMC API and network availability.
- Current implementation is a baseline, not a production research assistant.

## Evaluation roadmap — proposed, not completed

1. Freeze a dated, DOI-linked bibliography and predefined research questions.
2. Obtain blinded independent assessments of relevance, traceability, and unsupported claims.
3. Compare manual review, this deterministic baseline, a single-model approach, and a genuine multi-agent implementation using the same source set.
4. Publish prompts, datasets, code revisions, costs, timing, failures, and negative results.
5. Consider commercial pilots only after researchers demonstrate utility or willingness to pay.

## Status and governance

**Implemented:** Europe PMC metadata retrieval, offline JSON input, executable eight-role deterministic council, two rounds of multi-agent discussion, allowlisted corrective memory, hash-linked message trace, audit checks, unit tests, and scheduled GitHub Actions runs. A separate CPU workflow runs an openly available local Qwen model and archives the model outputs alongside the handoff record. [Verified live-data + three model-backed roles run](https://github.com/AMMARICA1791/bioreason/actions/runs/40258295368).

**Optional model-backed reasoning:** All eight roles support per-role model suggestions through an explicitly configured OpenAI-compatible endpoint. No credentials are bundled; opt-in remote calls require `BIOREASON_MODEL_ENDPOINT`, `BIOREASON_MODEL_NAME`, and optionally `BIOREASON_MODEL_API_KEY`. Send only metadata appropriate for a trusted endpoint. Alternatively, the GitHub Actions [local model council](https://github.com/AMMARICA1791/bioreason/actions/workflows/model-council.yml) uses CPU-only Qwen without a paid API key and attempts real Europe PMC collection. The offline deterministic CLI is the default. **Not implemented:** separately hosted autonomous models, full-text verification, scientific originality/patent review, a product service, billing, or proved commercial usefulness. The `--legacy` flag retains the original flat pipeline.

Research use only. Do not use generated questions for diagnosis, treatment, laboratory safety, or claims of novelty. Contributions should include reproducible cases, citations, and counterexamples.

**License:** not selected. This repository is publicly readable but is **not licensed for redistribution or reuse** until a license is explicitly added.
