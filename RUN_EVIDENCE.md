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

## Independently verified cross-run corrective memory

- **Proof workflow:** [Run 40260928759](https://github.com/AMMARICA1791/bioreason/actions/runs/40260928759), **success** on 2026-10-26 UTC.
- **Exact cache restored:** `bioreason-corrective-memory-v1-40259626692-1`, saved by an earlier successful model-backed council run.
- **Log proof:** `Cache hit for restore-key`, `Cache restored successfully`, and `PASS: persisted council corrective memory restored from a prior GitHub Actions run`.
- **State read:** `completed_cycles: 1`; issue code `missing_source_anchor` was present.
- **Evidence artifact:** [persisted-council-memory-proof, artifact 12623982891](https://github.com/AMMARICA1791/bioreason/actions/runs/40260928759/artifacts/12623982891).

This establishes **cross-run persistence and successful retrieval** of an allowlisted corrective lesson without manual transfer. It does **not** establish model-weight learning, independent long-term scientific improvement, or that GitHub's cache will never expire.

## Evidence-coherence correction: first live evaluation

- **Workflow:** [run 40262396660](https://github.com/AMMARICA1791/bioreason/actions/runs/40262396660) — GitHub Actions success, 2026-10-26 UTC.
- **Source:** 10 actual Europe PMC records, 2 providing abstract text.
- **Model work:** 8 initial role inferences plus 16 more discussion responses, in two complete rounds.
- **Source quality gate:** both Inventor proposals were **held for independent review** due to missing usable record citations. No tentative research question was released from this run.
- **Memory continuity:** previous count of 3 completed cycles was restored; this cycle saved a fourth.
- **Evidence artifact:** [model-council output 12625277025](https://github.com/AMMARICA1791/bioreason/actions/runs/40262396660/artifacts/12625277025), including candidate screens, exact reasons, dialogue, and saved lessons.
- **Post-run correction:** the Inventor is now instructed to ask a concrete sourced testable question or abstain, and the independent screen refuses outputs that do not contain a question.
- **Offline regression status:** [40 software tests and 10 synthetic positive/negative cases passed](https://github.com/AMMARICA1791/bioreason/actions/runs/40263193884) across Python 3.10–3.13.

An abstention can be safer than a fabricated connection, but withholding two proposals **does not demonstrate that a scientific hypothesis was successfully repaired**. The 10 synthetic cases are regression checks, not blinded biomedical expertise or general clinical accuracy.

## Focused-source quality experiment (2026-10-26)

- **Problem observed:** [live council run 40263193759](https://github.com/AMMARICA1791/bioreason/actions/runs/40263193759) completed technically, but both Inventor turns were held for `unassessed_biomedical_topics`. Inspection of the saved discussion showed a broad catalogue question — "What are some applications of AI and machine learning in healthcare?" — with an indiscriminate list of ten real study identifiers, not a testable hypothesis.
- **Source correction:** [focused verification run 40314598414](https://github.com/AMMARICA1791/bioreason/actions/runs/40314598414) successfully collected **nine** distinct, traceable papers centered on cervical cancer research and AI, using live Europe PMC, with a controlled date-window extension only when necessary. Full bibliography archived as a workflow artifact.
- **Scientific-quality correction:** the screening gate now holds non-falsifiable catalogue questions and proposals that cite more than three disparate source records. The reference regression cases still distinguish candidate questions from unsupported inter-disease bridges.
- **Engineering proof:** [Python tests 40314464085](https://github.com/AMMARICA1791/bioreason/actions/runs/40314464085) succeeded on Python 3.10–3.13 with **46 tests**. The ten existing synthetic scientific regression cases remain successful.
- **Crucial limit:** real Qwen performance on the **new focused corpus** was not yet confirmed at the time these corrections were made. Passing tests and retrieving coherent records are not proof of scientific hypothesis quality.

## Predeclared peer-critique versus solo control

- **Protocol:** [EVALUATION_PROTOCOL.md](EVALUATION_PROTOCOL.md) documents the six-rule proxy rubric and negative-result rules **before** interpreting any solo-versus-council model run.
- **Implementation:** `src/bioreason/comparison.py` records the actual text and identical mechanical screening of a solo Inventor response, first-round Inventor response, and final revised Inventor response using the same source bibliography and model. It explicitly discloses that inference budgets and contexts are unequal, so causal scientific improvement cannot be inferred.
- **Integrity:** `scripts/evaluate_run.py` independently recomputes the saved comparison from the actual responses and verifies both hash-linked message traces. Manipulated output or fabricated model call counts fail.
- **Root cause discovered from the earlier real council artifact:** `recent_dialogue_from_other_agents` included only four recent turns. The second-round Inventor consequently did **not** receive the prior-round Critic's objection because that turn had scrolled out of the window.
- **Correction:** `src/bioreason/deliberation.py` now passes the **actual previous Critic objection**, Validator feedback, the scientific gate's specific blocking reasons, and a directly retrieved candidate record as `mandatory_revision_feedback` to Inventor. Records are for scrutiny; source IDs are not automatically appended, and unsupported proposals stay on hold.
- **Engineering proof:** [run 40316840840](https://github.com/AMMARICA1791/bioreason/actions/runs/40316840840) passed **57** offline tests on Python 3.10–3.13, including direct Critic-to-Inventor transmission, refusal to launder missing citations, tampered-score checks, and honest negative comparisons. The ten synthetic regression cases also passed.

**No scientific improvement is established by these tests.** A paired, actual-model run must separately report whether the revised council proposal improves on the solo answer and the first-round council answer.

## First actual Qwen solo-versus-council experiment: negative result

- **Run:** [40316126789](https://github.com/AMMARICA1791/bioreason/actions/runs/40316126789) — completed successfully on 2026-10-26 UTC.
- **Data:** the same nine real, focused Europe PMC cervical-cancer AI papers and the same Qwen 0.5B model for all candidates.
- **Generation:** one solo Inventor response and 24 council inference turns; comparison integrity check passed.
- **Proposals:** the solo model asked whether AI screening and diagnostic algorithms could improve diagnostic accuracy compared with traditional methods. The first and last council Inventor proposals instead asked whether deep learning on Pap smear images could improve cervical cancer screening accuracy; the second proposal was essentially unchanged.
- **Evidence problem:** none of the three candidate texts cited an exact provided record ID, so all three were `hold_for_independent_review`.
- **Recorded proxy metric:** solo `4/6`, first council `3/6`, final council `3/6`; solo-to-final difference `-1`. Therefore **no council advantage was observed**.
- **Metric defect discovered during review:** the initial proxy implementation awarded a topic-grounding point when any retrieved record matched the subject, even if the answer did not cite it. This violated the written criterion. The code was corrected to require the cited ID itself to cover the topic. Re-evaluation of these exact three texts produces **solo `3/6`, council first `2/6`, council final `2/6`**, preserving the negative `-1` difference. [The corrected implementation and 58 offline tests](https://github.com/AMMARICA1791/bioreason/actions/runs/40317199847) were confirmed successful.
- **Archived source evidence:** [original full model and comparison artifact 12646753546](https://github.com/AMMARICA1791/bioreason/actions/runs/40316126789/artifacts/12646753546). The original run artifact is retained **without alteration**; this disclosure explicitly documents the subsequent scorer correction.

This **negative first measurement** cannot be treated as a general proof of council inferiority, just as an isolated positive score would not establish scientific usefulness. Neither the solo nor council generated independently validated scientific conclusions. The missing Critic-to-Inventor handoff was subsequently repaired in code and tested, but a later **real model experiment** is necessary to determine whether that correction improves outcomes.

## Critic audit and observed template-copying regression (2026-10-26)

- **Actual model:** [Run 40319089691](https://github.com/AMMARICA1791/bioreason/actions/runs/40319089691) succeeded with nine live focused Europe PMC papers, the same local Qwen/Qwen2.5-0.5B-Instruct, one solo turn, and 24 council turns.
- **Observed outcome:** under the then-current rubric, the solo and council-first/final answers each scored **2/6**; the final proposal was held for independent review. No agent advantage or scientific improvement was demonstrated.
- **Root cause documented from [unaltered artifact 12649165247](https://github.com/AMMARICA1791/bioreason/actions/runs/40319089691/artifacts/12649165247):** the small model copied the prompt template literally — for example `Could [specific method] improve [measurable endpoint] versus [baseline]?` — rather than supplying an actual research method or source ID.
- **Revisions, not retroactive reinterpretation:** removed literal answer templates from the model's instructions. The evidence screen now separately blocks `unresolved_template_placeholders`; this error is also an allowlisted corrective lesson for later runs.
- **Responsible uncertainty:** clear `ABSTAIN: insufficient evidence` outputs are now recorded as abstentions rather than penalized for missing research citations, while fake DOI claims hidden after `ABSTAIN` remain blocked.
- **Verified deterministic tests:** [run 40320357391](https://github.com/AMMARICA1791/bioreason/actions/runs/40320357391) passed **71 offline tests** on Python 3.10–3.13 plus the ten existing synthetic research-gate cases.

**Limitation:** the full local-model inference cycle using the *post-template* instructions is a distinct experiment. The code and tests prove that invalid copied templates are rejected; they do not establish whether a small model can reliably originate stronger source-grounded questions.

## Actual model regression and no-downgrade review-lead selection (2026-10-26)

- **Verified real-model run:** [40320610137](https://github.com/AMMARICA1791/bioreason/actions/runs/40320610137) completed successfully after prompt-template cleanup, using Qwen2.5-0.5B, nine traceable Europe PMC records, one solo Inventor turn and 24 council turns.
- **Original output:** the solo model included the legitimate source ID `42380812` in its cervical-cancer screening question. Both the first and revised council Inventor questions **omitted every exact source ID**, even after Critic objections. The two proposals were therefore held under `missing_record_citation`.
- **Recorded metric at that revision:** solo **5/6**, council-first **2/6**, council-final **2/6**; council-minus-solo **-3**. Critic separately produced two explicit objections, but this did not cause an improved Inventor answer. No scientific improvement is proven.
- **Subsequent scoring correction:** a plural form, `detection rates`, was wrongly missed by the measurable-endpoint regex. The current rubric recognizes both `detection rate` and `detection rates`. When replaying the **unaltered actual Qwen answers**, this changes the proxy scores to **6/6 solo, 3/6 first council, 3/6 final council**, preserving the negative delta **-3**. [Regression test](tests/test_comparison.py) stores the exact model transcripts and verifies this recalculation. This is a *post-run metric bug correction*, not a newly successful scientific experiment.
- **Safety correction:** the newly implemented `comparison.selection` policy retains the solo answer as a **tentative human-review-only lead** whenever the final council response is held or does not strictly exceed the solo answer's evidence proxy. It chooses the council only for a better, screened final answer; selects nothing if both are held. It never labels any candidate scientifically validated, automatically publishes a medical conclusion, or rewrites the original council trace.
- **Integrity:** `scripts/evaluate_run.py` recomputes the selected human-review lead independently from the saved full texts and source set and rejects tampering with the selected source.
- **Source artifact:** [Full original model dialogue and bibliography](https://github.com/AMMARICA1791/bioreason/actions/runs/40320610137/artifacts/12649466534).

**Interpretation:** The first fully source-linked solo reply outperformed the council under this limited format/evidence rubric. Retaining a better independently screened solo question prevents a loss of review-lead quality; **it does not make the eight-role council scientifically better**. Proper expert-labelled and equal-budget evaluation remains outstanding.

## Earlier independent proof

The preceding [run 40258295368](https://github.com/AMMARICA1791/bioreason/actions/runs/40258295368) proved live retrieval of 10 Europe PMC records and actual model output for Analyst, Inventor, and Critic before the eight-role extension.

Research-only prototype; do not use it for diagnosis, treatment, or claims of scientific discovery.
