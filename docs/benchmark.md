# Benchmark

## Purpose
This benchmark evaluates culturally grounded retrieval for multilingual RAG with an emphasis on English and Uzbek. It is designed to measure how access to relevant source documents affects answer grounding and retrieval quality for questions that depend on local institutional, historical, and cultural knowledge.

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

## Example Schema
Each evaluation item includes:

- `id`
- `language`
- `domain`
- `question`
- `gold_answer`
- `cultural_specificity`
- `answerable`
- `source_doc_ids`

This schema supports direct retrieval recall analysis against intended source documents.
