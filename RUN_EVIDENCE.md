# Verified execution evidence — BioReason

This page records GitHub-hosted execution outcomes, not scientific validation or product claims.

## Live retrieval + eight model-backed council roles

- **Workflow:** [BioReason real model council proof, run 40258555382](https://github.com/AMMARICA1791/bioreason/actions/runs/40258555382)
- **Revision under test:** `8d2587f8cf8a821389a0494a23b3fa3f9898b1fa`
- **Date (UTC):** 2026-10-26
- **Conclusion:** GitHub Actions **success**
- **Tests:** 21 offline tests passed before inference.
- **Input:** 10 records returned by the live Europe PMC search API.
- **Actual local inference:** Qwen/Qwen2.5-0.5B-Instruct generated nonempty suggestions for **Scout, Analyst, Inventor, Critic, Validator, Builder, Auditor, Coordinator**.
- **Council verification:** Eight roles present; hash-linked handoff chain verified; deterministic workflow audit passed.
- **Saved artifact:** [real-model-council-evidence, artifact 12623423579](https://github.com/AMMARICA1791/bioreason/actions/runs/40258555382/artifacts/12623423579), including the bibliography, model candidates, and complete handoff trace.

The run log includes:

```text
Live records received: 10
PASS: live Europe PMC records: 10
PASS: actual local model generated outputs for all eight roles: Scout, Analyst, Inventor, Critic, Validator, Builder, Auditor, Coordinator
PASS: eight-role council, verified handoff chain; findings unvalidated
```

## Reproducibility and scope

Eight distinct **model inference turns** were executed using **one shared, locally loaded model**, with individual role prompts and chained context. This is **not** eight separately deployed or trained models. The automatic schedule is requested every six hours through GitHub Actions, but exact execution timing depends on GitHub scheduling availability. A scheduled workflow is not a continuously running background service.

Scientific findings, novelty, causality, clinical safety, patents, and research usefulness **were not validated**. This prototype currently analyzes bibliographic metadata, primarily titles, not full research papers. Deterministic record-traceability checks are not scientific peer review. Model-produced text is explicitly tagged as unverified.

The logs contain a non-blocking GitHub Actions Node.js deprecation warning from third-party workflow actions. It does not invalidate the successful run.

## Two-round, eight-role discussion with verified learning signals

- **Workflow:** [Run 40259589474](https://github.com/AMMARICA1791/bioreason/actions/runs/40259589474)
- **Revision:** `33f897d7064c4dd1335f56e1bdc3c3937bea8487`
- **Result:** completed successfully on 2026-10-26 UTC.
- **Evidence:** 27 offline unit tests passed; 10 genuine Europe PMC metadata records obtained; Qwen performed **24 model inference turns**: eight initial role turns and **16 additional discussion turns in two rounds**.
- **Discussion trace:** second hash-linked conversation chain verified and archived in [artifact 12624097777](https://github.com/AMMARICA1791/bioreason/actions/runs/40259589474/artifacts/12624097777).
- **Observed procedural issues:** the deterministic `missing_source_anchor` rule flagged four responses in round one and one in round two. This is a within-run change in one citation-related signal, **not** a demonstrated increase in scientific correctness.
- **Lessons recorded:** `{"code":"missing_source_anchor","count":5}`. A copy of the verified initial state is stored in [the corrective-memory seed](.bioreason_state/lessons.json). Subsequent successful scheduled runs are configured to restore, extend and save such lessons via GitHub Actions cache.
- **Safety:** model prose is archived as tentative; the reusable memory accepts only predeclared issue codes, never arbitrary model instructions. The model's weights do not change.

This section establishes real peer-message exchange and within-run feedback. **Cross-run cache restoration remains a separate check** until a subsequent workflow log confirms a nonzero restored-cycle count.

## Earlier independent proof

The preceding [run 40258295368](https://github.com/AMMARICA1791/bioreason/actions/runs/40258295368) proved live retrieval of 10 Europe PMC records and actual model output for Analyst, Inventor, and Critic before the eight-role extension.

Research-only prototype; do not use it for diagnosis, treatment, or claims of scientific discovery.
