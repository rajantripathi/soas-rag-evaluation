# Concept Note

## Title
Culturally Grounded Multilingual RAG Evaluation for Global South Knowledge

## Motivation
Multilingual AI systems are often evaluated using broad, generic benchmarks that underrepresent the kinds of culturally specific knowledge needed for socially useful deployment. This is especially limiting for Global South settings, where historically important, institutionally specific, and culturally grounded knowledge may be thinly represented in large general-purpose corpora. In such settings, poor model performance is often interpreted as a limitation of model architecture, embedding quality, or prompting strategy. This project investigates a different hypothesis: that retrieval failures in culturally grounded multilingual QA are driven primarily by missing or weakly represented knowledge sources.

The project focuses on English and Uzbek and asks a practical research question: when a multilingual RAG system fails on culturally grounded questions, is the main bottleneck model choice or corpus coverage? This question matters because it changes the design priorities for multilingual AI systems. If the dominant bottleneck is corpus coverage, then improving culturally grounded AI requires better knowledge curation and source representation, not only better models.

## Benchmark Design
We built a reproducible evaluation pipeline on Isambard with config-driven preprocessing, indexing, evaluation, and reporting. The benchmark centers on culturally grounded questions in four domains:

- governance
- history
- institutions
- culture

The benchmark was bilingual from the start:

- English
- Uzbek

The initial manually curated benchmark, `manual_eval_v2`, contained 200 items balanced as 25 items per language-domain cell. This was later expanded to `manual_eval_v4`, a 400-item benchmark with 50 items per language-domain cell. The expanded version preserved the original 200 items and added deterministic alternate phrasings to test whether findings were stable under modest question variation.

Each example preserved a structured schema with:

- `id`
- `language`
- `domain`
- `question`
- `gold_answer`
- `cultural_specificity`
- `answerable`
- `source_doc_ids`

This design allowed retrieval recall to be evaluated directly against intended source documents rather than relying only on answer-text overlap.

## Experiment Sequence
The experimental program proceeded in stages.

First, we compared a no-retrieval baseline against vector retrieval and grounded prompting. Retrieval immediately improved answer grounding, but the language split revealed a substantial Uzbek gap, especially in history and institutions.

Second, we tested chunking variants. Smaller chunk sizes did not improve the hardest Uzbek cases. This suggested that the main issue was not passage segmentation.

Third, we compared multilingual embeddings. `intfloat/multilingual-e5-large` slightly outperformed the other tested models, but the gains were modest. The hardest Uzbek domains remained weak even with a stronger embedding model.

Fourth, we conducted corpus gap analysis. This proved decisive. Low-recall Uzbek examples in history and institutions largely corresponded to missing source documents in the baseline corpus. We then introduced two supplement conditions:

- supplement v1: a small targeted manual Uzbek supplement for history and institutions
- supplement v2: a broader structured Uzbek supplement extracted from saved Uzbek Wikipedia rows

These supplements produced by far the largest gains in retrieval recall.

Finally, we tested hybrid retrieval by combining BM25 with vector retrieval. BM25 alone underperformed vector retrieval, and hybrid retrieval matched but did not exceed the vector-only setup on the final expanded corpus.

## Main Finding
Across all experiments, the same pattern emerged: corpus coverage dominated model choice.

On `manual_eval_v2`, the baseline vector setup achieved:

- overall recall@k: `0.5100`
- English recall@k: `0.6300`
- Uzbek recall@k: `0.3900`

After supplement v1, recall rose to:

- overall: `0.7150`
- Uzbek: `0.8000`

After supplement v2, recall rose further to:

- overall: `0.8050`
- Uzbek: `0.9800`

Under the final `manual_eval_v4` best setup, recall@k was:

- overall: `0.7950`
- English: `0.6300`
- Uzbek: `0.9600`

The key point is not just that performance improved. It is how it improved. Chunking changes were small. Embedding changes were modest. Hybrid retrieval did not surpass vector retrieval. The decisive gains came from adding the culturally grounded documents that were absent from the baseline corpus.

## Implications
The project suggests that culturally grounded AI evaluation should foreground knowledge source coverage. A multilingual model cannot ground answers in documents that are not present. This is especially important for underrepresented languages and domains where institutional, historical, or cultural knowledge may not appear in generic retrieval corpora at sufficient density.

This has two implications for research and deployment.

First, multilingual RAG quality should be interpreted as a joint property of the model and the corpus. A weak retrieval result may reflect representational absence rather than modeling failure.

Second, culturally grounded AI systems may benefit most from targeted, reproducible local supplements. In this project, small and structured Uzbek supplements improved retrieval substantially without redesigning the rest of the pipeline.

## Proposed Next Steps
Two next directions are especially realistic.

1. Expand culturally grounded corpora beyond the current supplement set, including broader institutional, legal, and historical sources.
2. Extend cross-language evaluation to test whether equivalent knowledge is represented symmetrically across English and Uzbek.

## Summary
This project contributes a practical, reproducible multilingual RAG evaluation pipeline and a clear empirical result: culturally grounded retrieval quality depends first on culturally grounded knowledge source coverage. For Global South AI systems, corpus design is not a secondary implementation detail. It is a primary research variable.
