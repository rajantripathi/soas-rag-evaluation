# Audit Summary

## Top Findings

- The most common failure cause in the v2 retrieval-failure report is domain/template misclassification, but the single dominant systems-level root cause is still corpus absence in the baseline index, especially for Uzbek items where all 10 misses collapse onto the same hub documents ([failure taxonomy](failure_taxonomy_20260309.md)).
- Several benchmark items are structurally invalid because their domain template does not match the entity at all, including `en_20`, `en_61`, `en_62`, `uz_71`, `uz_78`, `uz_82`, `uz_83`, and `uz_89` ([dataset quality audit](dataset_quality_audit_20260309.md)).
- v4 gold-answer rewriting improves many noisy v1 answers, but some rewritten answers are over-compressed and less specific than the originals ([dataset quality audit](dataset_quality_audit_20260309.md)).
- The current evaluation setup conflates retrieval success with answer-generation artifacts because the stub generator emits only the first sentence while scoring relies on token overlap ([dataset quality audit](dataset_quality_audit_20260309.md)).
- v5 adds deterministic `source_title`, `difficulty`, and `quality_flag` fields so the dataset becomes more auditable and known bad items remain traceable rather than silently mixed into the clean set ([v5 enrichment specification](v5_enrichment_spec_20260309.md)).

## Failure Causes

Ranked by frequency in the failure taxonomy:

1. `domain_misclassification` (`6`)
2. `corpus_gap` (`5`)
3. `question_quality` (`1`)
4. `entity_mismatch` (`0`)
5. `retriever_confusion` (`0`)

The single most common root cause at the benchmark-design level is bad domain/template assignment for a subset of items, but the single most important retrieval-system cause is corpus absence in the baseline corpus.

## Benchmark Validity Risks

- Wrongly assigned domains create semantically broken questions and make failure counts look like retriever weakness when the benchmark item itself is malformed.
- Gold answers with Wikipedia navigation artifacts or raw page dumps weaken answer-quality evaluation and make overlap-based scoring unreliable.
- The current metric stack mixes retrieval evaluation with stub-generation artifacts, so some "incorrect grounded answers" are not clean retrieval failures.
- English source IDs are readable titles while Uzbek source IDs are opaque numbers, which reduces auditability and makes external review uneven across languages.

## Urgent Fixes (Before Publication)

- Remove, relabel, or quarantine misclassified items such as `en_61`, `uz_71`, `uz_78`, `uz_82`, `uz_83`, and `uz_89`.
- Clean or replace gold answers that still reflect Wikipedia navigation artifacts or page-template residue.
- Add a direct methodological note stating that retrieval evaluation (`recall@k`) and answer evaluation are separate, especially when using the stub generator.
- Resolve Uzbek `source_doc_ids` to readable titles so external reviewers can inspect failures without Isambard-only corpus lookups.

## Non-Urgent Improvements (Later Versions)

- Add `evidence_text` with corpus-backed human-verified extraction.
- Add verified `source_url` fields.
- Expand to a third language or broader domain coverage.
- Add an LLM-as-judge or human-judged answer-evaluation layer.
- Create deliberately paired cross-lingual items instead of trying to retrofit pairings onto non-parallel English and Uzbek halves.
