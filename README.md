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

**Architecture disclosure:** The default CLI now executes eight bounded, deterministic software-agent roles with explicit, hash-linked message handoffs, an audit result, and tamper-detection tests. **These are not independently reasoning LLM agents**. No autonomous self-learning, experimentation, continuous background execution, or scientific verification is implemented.

## Run

Python 3.10+; no runtime third-party dependencies.

```bash
PYTHONPATH=src python -m bioreason 'CRISPR AND cancer' --limit 10
PYTHONPATH=src python -m bioreason 'example query' --input examples/papers.json
PYTHONPATH=src python -m unittest discover -s tests -v
```

The online command requires Europe PMC access. Offline fixtures and unit tests require no network. The repository defines **sixteen offline unit tests**. A prior local prototype passed five tests; the published six-test suite has not yet been independently verified in GitHub Actions. Passing software tests would not establish scientific accuracy.

Input: JSON array of objects with `title`, `id`, `source`, `doi`, optionally `year`. Output: JSON printed to stdout. Example records are synthetic.

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

**Implemented:** Europe PMC metadata retrieval, offline JSON input, executable deterministic eight-role council, hash-linked message trace, audit checks, unit tests.

**Optional model-backed reasoning:** Analyst, Inventor and Critic can call an explicitly configured OpenAI-compatible chat-completions endpoint. This is **opt-in** and unverified model output; no API keys or model endpoints are bundled. For example, set `BIOREASON_MODEL_ENDPOINT`, `BIOREASON_MODEL_NAME`, and optionally `BIOREASON_MODEL_API_KEY`, then run `PYTHONPATH=src python -m bioreason 'protein folding' --input examples/papers.json --model-roles Analyst,Inventor,Critic`. Only use a trusted endpoint; research metadata will be sent to it. Offline deterministic mode is the default. **Not implemented:** autonomous hosted agents, cross-paper scientific synthesis, live monitoring, full-text verification, hosted service, billing. The `--legacy` CLI flag retains the original flat pipeline. The `--legacy` CLI flag retains the original flat pipeline.

Research use only. Do not use generated questions for diagnosis, treatment, laboratory safety, or claims of novelty. Contributions should include reproducible cases, citations, and counterexamples.

**License:** not selected. This repository is publicly readable but is **not licensed for redistribution or reuse** until a license is explicitly added.
