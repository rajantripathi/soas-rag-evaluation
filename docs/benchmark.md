# Benchmark

## Purpose
This 400-row pilot benchmark evaluates culturally grounded retrieval in English and Uzbek. It is designed to measure whether relevant source documents are retrieved for questions that depend on local institutional, historical, and cultural knowledge. It does not measure generated-answer quality.

## Languages and Domains
- English
- Uzbek

Domains:
- governance
- history
- institutions
- culture

## Evaluation Sets
- `manual_eval_v2`: 200 examples, balanced as 25 items per language-domain cell
- `manual_eval_v4`: 400 examples, balanced as 50 items per language-domain cell

`manual_eval_v4` preserves the `manual_eval_v2` benchmark and adds deterministic alternate phrasings to test stability under modest question variation.

## Public Retrieval-Only Schema

Each public evaluation item includes:

- `id`
- `language`
- `domain`
- `question`
- `cultural_specificity`
- `answerable`
- `source_doc_ids`
- `source_title`
- `difficulty`
- `quality_flag`

This schema supports direct retrieval recall analysis against intended source documents.
Reference-answer fields used in internal QA work are excluded from the public branch pending source and licence clearance. Template-generated questions, domain mismatches, and incomplete quality flags are known pilot limitations.
