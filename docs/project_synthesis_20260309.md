# English-Uzbek Retrieval Evaluation: Project Synthesis

## Project Scope
This project built a reproducible multilingual RAG evaluation pipeline on Isambard for English and Uzbek, with a primary focus on culturally grounded retrieval quality. The experimental sequence covered:

- no-retrieval baseline
- vector RAG baseline
- chunking variations
- multilingual embedding comparison
- corpus supplement experiments
- hybrid lexical plus vector retrieval
- benchmark expansion from `manual_eval_v2` to `manual_eval_v4`

The central validated result is that targeted Uzbek corpus supplementation increased retrieval recall from 39% to 98% (59 percentage points; *p* < 0.001; Cohen's *d* = 2.91). The compared embedding models differed by 7.5 percentage points overall (Cohen's *d* = 0.31). These results concern this retrieval setting and not generated-answer quality.

## Experimental Summary
Two benchmark phases were used:

- `manual_eval_v2`: 200 items, balanced at 25 items per language-domain cell
- `manual_eval_v4`: 400 items, balanced at 50 items per language-domain cell

Results from these two phases should be compared within phase, not across phase, because `manual_eval_v4` doubles the benchmark size and includes alternate phrasings.

## Unified Summary Table
| Phase | Condition | Corpus | Retrieval | Overall Recall@k | English Recall@k | Uzbek Recall@k |
| --- | --- | --- | --- | ---: | ---: | ---: |
| v2 | none | baseline | no retrieval | 0.0000 | 0.0000 | 0.0000 |
| v2 | vector baseline | baseline | simple vector | 0.4900 | 0.6100 | 0.3700 |
| v2 | chunk small | baseline, 256/64 | simple vector | 0.4850 | 0.6200 | 0.3500 |
| v2 | chunk smaller | baseline, 128/32 | simple vector | 0.4850 | 0.6200 | 0.3500 |
| v2 | e5 large | baseline | multilingual-e5-large | 0.5100 | 0.6300 | 0.3900 |
| v2 | mpnet | baseline | multilingual mpnet | 0.4350 | 0.6200 | 0.2500 |
| v2 | supplement v1 | baseline + manual Uzbek supplement | multilingual-e5-large | 0.7150 | 0.6300 | 0.8000 |
| v2 | supplement v2 | baseline + structured Uzbek supplement | multilingual-e5-large | 0.8050 | 0.6300 | 0.9800 |
| v4 | best vector | supplement v2 corpus | multilingual-e5-large | 0.7950 | 0.6300 | 0.9600 |
| v4 | BM25 only | supplement v2 corpus | BM25 | 0.6700 | 0.6200 | 0.7200 |
| v4 | hybrid | supplement v2 corpus | BM25 + multilingual-e5-large | 0.7950 | 0.6300 | 0.9600 |

## Table 1: Baseline vs Supplement Improvements
`manual_eval_v2`

| Condition | Overall Recall@k | English | Uzbek |
| --- | ---: | ---: | ---: |
| baseline vector | 0.5100 | 0.6300 | 0.3900 |
| supplement v1 | 0.7150 | 0.6300 | 0.8000 |
| supplement v2 | 0.8050 | 0.6300 | 0.9800 |

Interpretation:

- English stayed flat across supplement conditions.
- Uzbek improved sharply as culturally grounded Uzbek source coverage increased.
- Corpus supplementation produced the largest observed gain in this experiment sequence.

## Table 2: Language Comparison Under Best Setup
`manual_eval_v4`, supplement v2 corpus, `intfloat/multilingual-e5-large`, grounded prompt

| Language | Recall@k |
| --- | ---: |
| English | 0.6300 |
| Uzbek | 0.9600 |

Interpretation:

- Under the final setup, Uzbek outperformed English because the supplement work directly targeted Uzbek corpus gaps.
- English remained constrained by thinner source coverage in history and institutions.

## Table 3: Domain Comparison Under Best Setup
`manual_eval_v4`, supplement v2 corpus, `intfloat/multilingual-e5-large`, grounded prompt

| Language | Governance | History | Institutions | Culture |
| --- | ---: | ---: | ---: | ---: |
| English | 0.8000 | 0.4000 | 0.3200 | 1.0000 |
| Uzbek | 0.9800 | 0.9600 | 0.9600 | 0.9400 |

Interpretation:

- Before supplementation, Uzbek history and institutions were the weakest domains.
- After supplement v2, Uzbek recall was strong across all four domains.
- The remaining bottlenecks shifted toward English history and institutions rather than Uzbek.

## Why Culturally Grounded Knowledge Sources Matter
Culturally grounded AI systems depend on what knowledge is actually available to retrieve. In this project, weak retrieval was not primarily caused by chunk size, prompt style, or model architecture. It was usually caused by the absence of relevant local source documents in the retrieval corpus.

This matters for culturally grounded AI because:

- communities are often underrepresented in large generic corpora
- institutional and historical knowledge is frequently sparse or uneven across languages
- retrieval systems cannot ground answers in documents that are not present
- model improvements cannot fully compensate for missing or weakly represented knowledge sources

In practical terms, this means that culturally grounded performance is partly a corpus construction problem, not only a model selection problem.

## Comparison of Corpus and Retrieval Interventions
Several comparisons converged on the same conclusion:

1. Chunking changes had little or no effect on the hardest Uzbek domains.
2. Embedding changes produced only modest gains.
3. Hybrid retrieval matched vector retrieval but did not exceed it.
4. Corpus supplements produced the largest observed improvements in this setting.

The strongest evidence came from the corpus gap analysis:

- low-recall Uzbek history and institutions examples usually corresponded to missing gold documents in the baseline corpus
- once those documents were added through targeted supplements, recall increased substantially
- supplement v2, built from structured Uzbek Wikipedia rows, generalized the improvement beyond the earlier manual patch and solved the remaining culture gap

This is the clearest signal in the project: retrieval quality improved when the corpus contained the right culturally grounded documents.

## Why Chunking, Embeddings, and Hybrid Retrieval Had Smaller Effects
These factors mattered, but not nearly as much as source coverage:

- Chunking: smaller chunks did not improve Uzbek history or institutions in the baseline corpus because the core documents were still missing.
- Embeddings: `intfloat/multilingual-e5-large` was the best of the tested embedding models, but it could only provide modest gains when the corpus lacked the target material.
- Hybrid retrieval: BM25 added lexical matching, but once the culturally grounded corpus was expanded, vector retrieval already recovered most relevant documents. Hybrid therefore matched vector retrieval rather than surpassing it.

Taken together, these results suggest an order of operations for multilingual RAG research:

1. fix corpus coverage
2. then optimize retrieval modeling
3. then optimize prompting and generation

## Main Contribution
The main contribution is a controlled comparison showing that source coverage was an important retrieval constraint in this English-Uzbek evaluation setting.

More specifically, the project shows that:

- a multilingual RAG system can appear weak on culturally grounded evaluation because the relevant local documents are missing
- targeted supplementary corpora can improve retrieval quality without changing the overall pipeline
- once coverage improves, additional model-side changes produce smaller marginal gains

This reframes part of the multilingual AI problem from “which model should we use?” to “which knowledge sources are actually represented?”

## Future Research Directions
1. Expand culturally grounded corpora

- extend the supplementary corpus approach to broader Uzbek institutional, historical, legal, and cultural sources
- add more systematically curated English sources for the weaker English domains
- compare curated local corpora against generic web-derived corpora for grounding quality

2. Cross-language knowledge evaluation

- test whether equivalent concepts are equally retrievable across English and Uzbek
- measure asymmetries where one language has stronger source coverage than the other
- evaluate whether multilingual systems preserve culturally specific meaning when the same topic is represented unevenly across languages

## Conclusion
Across the reported experiments, the largest observed retrieval gain came from adding missing Uzbek source material. The 59-percentage-point gain was approximately 7.9 times the 7.5-point gain observed from embedding-model variation; this is a ratio of absolute recall gains, not Cohen's *d* values.

For workshop or concept-note framing, the project supports a clear claim:

**In this English-Uzbek evaluation setting, corpus coverage merited explicit testing alongside model and retrieval choices.**
