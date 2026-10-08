# Title Evidence and Retrieval in an English-Uzbek Pilot: A Frozen-Corpus Sensitivity Analysis

**Rajan Prasad Tripathi** **[co-authors to be confirmed]**

AI² Lab, American University of Technology, Uzbekistan; Centre for AI Futures, SOAS University of London

**Status:** Draft for co-author review, generated from verified repository metrics. Not yet posted or peer reviewed.

## Abstract

Retrieval benchmarks for under-resourced languages are often built around article titles, which can let a retriever succeed by matching the named entity rather than the content. We examine this in an English-Uzbek pilot with 100 English and 96 Uzbek frozen Wikipedia target articles and 1,000 random background articles per language. 89 of 100 English and 96 of 96 Uzbek original questions contain their target's title. We compare four passage representations, including title masking with a fixed-window control, applied to every candidate. With the title-prefixed passages of the original pilot, multilingual E5-small (mE5-small) places the target in the top three for every question in both languages. Masking each article's own title lowers its Hit@3 to 92.0% for English and 79.2% for Uzbek; BM25 falls to 75.0% and 40.6%. The Uzbek drop exceeds the English drop by 12.8 percentage points for mE5-small (95% bootstrap interval [3.5, 22.2]) and 28.1 for BM25 ([14.9, 40.6]). Near-ceiling scores in this pilot therefore rest substantially on title evidence, more so for Uzbek. The design does not identify why the languages differ; question construction, background passage length, morphology and tokenisation remain plausible explanations. We release ranked predictions, passage hashes and verification scripts.

## 1. Introduction

Retrieval-augmented generation depends on finding the right source before any answer is generated [1, 2]. For under-resourced languages, retrieval quality is often judged on small purpose-built benchmarks, because large multilingual collections such as MIRACL and Mr. TyDi cover a limited set of languages [8, 9]. How such benchmarks are constructed matters. Questions written while looking at a passage share its vocabulary, which favours lexical matching [13]; short entity-centric questions behave differently from natural ones for dense retrievers [14]; and dataset artifacts more generally let models succeed for reasons unrelated to the intended skill [15, 16].

This paper examines one such artifact in an English-Uzbek pilot. Its questions are short templates about Wikipedia articles, and most name their target, for example the Uzbek "Toshkent nima?" ("What is Tashkent?") and the English "What is Art Deco?". In a frozen-corpus version of the pilot, mE5-small retrieved the target in the top three for every original question in both languages. A ceiling like this says little about retrieval if it rests on matching the title.

We hold the questions, corpus and retrievers fixed and remove title evidence from the passages. Natural entity mentions are legitimate retrieval evidence, so this is a sensitivity analysis rather than a test for leakage. Our contributions are:

- a frozen, hash-checked title-masking protocol with a fixed-window control, applied to target and background passages alike;
- evidence that complete-corpus Hit@3 in this pilot depends on title evidence, with larger drops for Uzbek than English under both sparse and dense retrieval;
- passage-level diagnostics and released ranked predictions, with standalone scripts that recompute every reported cell.

## 2. Related work

**Multilingual retrieval benchmarks.** TyDi QA [10], Mr. TyDi [9] and MIRACL [8] provide monolingual retrieval and question answering across typologically diverse languages with native-speaker questions; XOR QA extends this to cross-lingual retrieval [11]; BEIR covers heterogeneous zero-shot retrieval in English [12]. Uzbek is not among the MIRACL or Mr. TyDi languages, which motivates small dedicated pilots such as this one, and also their scrutiny.

**Retrievers.** We use BM25 [3] as the lexical baseline and dense bi-encoders in the style of DPR [2]: multilingual E5 [4, 5] and the dense mode of BGE-M3 [6], both built on XLM-RoBERTa encoders [7].

**Artifacts and shortcuts.** Annotation artifacts let models exploit surface cues [15], a case of shortcut learning more broadly [16]. In open-domain question answering, Lee et al. note that questions written against a passage overstate lexical overlap [13], and Sciavolino et al. show that dense retrievers struggle with simple entity-centric questions that BM25 handles well [14]. We study the converse situation: entity-named template questions where title matching may inflate scores.

**Under-resourced languages.** Many languages remain poorly served by NLP resources [17], and multilingual tokenisers can represent some languages less efficiently than monolingual ones [18]. Uzbek has dedicated encoders such as UzBERT [19] but no established retrieval benchmark comparable to the resources above. Generation-side evaluation, for example with RAGAs [20], is outside our scope.

## 3. Data and frozen corpus

The pilot release contains 200 original questions and 200 deterministic alternate phrasings, balanced across governance, history, institutions and culture. The English and Uzbek halves are not translations, and difficulty labels are heuristic. Questions are short templates; all 96 resolved Uzbek and 89 of 100 English original questions contain the normalised target title.

Targets were resolved to Wikipedia pages and frozen at recorded revisions with raw and extracted-text hashes. All 100 English and 96 Uzbek targets resolved; the four Uzbek exclusions are "-1" (legacy ID 1036); "2 (son)" (legacy ID 1037); "Sovet Ittifoqi Madhiyasi" (legacy ID 14266); "Oʻzbekistondagi universitetlar" (legacy ID 1887). Each language adds 1,000 background articles sampled once from main-namespace nonredirect pages and frozen by revision ID. Retrieval is within language, over the complete corpus.

**Table 1. Questions and candidates.**

| Language | Original questions | Title in question | Alternate phrasings | Background articles | Candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| English | 100 | 89 | 100 | 1,000 | 1,100 |
| Uzbek | 96 | 96 | 96 | 1,000 | 1,096 |

## 4. Method

### 4.1 Passage representations

Each candidate is represented by one lead passage of at most 480 tokens of the pinned mE5-small tokeniser. We compare four representations, each applied to every candidate in the corpus:

- **Title prefix**: title + ". " + article lead, truncated (the original pilot protocol);
- **No added prefix**: the lead only; the title still appears wherever the article mentions it;
- **Title masked**: every occurrence of the article's own title, and of its form without a parenthetical disambiguator, is removed from the lead before truncation;
- **Masked fixed window**: the same 480-token window as "no added prefix" is selected first and then masked, so later text cannot replace removed tokens.

Matching is case-insensitive, tolerates Uzbek apostrophe variants (ʻ, ʼ, ' and similar) and uses Unicode word boundaries, so masking "Art" leaves "Earth" intact. Inflected forms such as "Toshkentda" are not masked, and synonyms and partial names remain; the procedure removes exact title strings only.

### 4.2 Retrievers

BM25 uses the repository implementation (k1 = 1.5, b = 0.75, Unicode word tokenisation, lowercasing). mE5-small (`intfloat/multilingual-e5-small`, revision `614241f622f5`) uses `query: ` and `passage: ` prefixes, normalised embeddings and dot-product ranking. **[Pending: additional dense retrievers.]** Ties are broken by document ID.

### 4.3 Measures

Hit@k is the share of questions whose designated source appears in the top k (k = 1, 3, 5; k = 3 primary). Original questions, one per distinct source, form the primary analysis; alternate phrasings are reported separately and never pooled. Within-language drops use a paired bootstrap over source groups (10,000 resamples, seed 42). Between-language differences, and differences between the two languages' drops, use an unpaired bootstrap that resamples each language independently. Intervals are descriptive, condition on the frozen corpus and questions, and are not adjusted for the number of comparisons.

## 5. Results

### 5.1 Main results

**Table 2. Hit@3 on original questions, complete corpus.**

| Retriever | Language | Title prefix | No added prefix | Title masked | Masked fixed window |
| --- | --- | ---: | ---: | ---: | ---: |
| BM25 | English | 99.0% | 98.0% | 75.0% | 75.0% |
| BM25 | Uzbek | 92.7% | 90.6% | 40.6% | 40.6% |
| mE5-small | English | 100.0% | 100.0% | 92.0% | 93.0% |
| mE5-small | Uzbek | 100.0% | 95.8% | 79.2% | 79.2% |

With the pilot's title-prefixed passages, mE5-small reaches 100.0% in both languages and BM25 99.0% (English) and 92.7% (Uzbek). Removing only the added prefix changes little, because titles recur in article leads. Masking those occurrences produces the large drops. The fixed-window control gives nearly the same values, so the drops are not caused by later text being drawn into masked passages.

### 5.2 Drops within each language

**Table 3. Hit@3 drop from title prefix to title masked, in percentage points with 95% intervals.**

| Retriever | English Hit@3 | English drop | Uzbek Hit@3 | Uzbek drop | Uzbek minus English drop |
| --- | --- | --- | --- | --- | --- |
| BM25 | 99.0% to 75.0% | 24.0 [16.0, 33.0] | 92.7% to 40.6% | 52.1 [41.7, 61.5] | 28.1 [14.9, 40.6] |
| mE5-small | 100.0% to 92.0% | 8.0 [3.0, 14.0] | 100.0% to 79.2% | 20.8 [13.5, 29.2] | 12.8 [3.5, 22.2] |

Both languages lose accuracy under masking, and Uzbek loses more under both BM25 and mE5-small. The dense retriever is far less sensitive than BM25: mE5-small keeps 79.2% of Uzbek targets in the top three where BM25 keeps 40.6%.

### 5.3 Between-language differences

**Table 4. English minus Uzbek Hit@3, in percentage points with 95% intervals.**

| Retriever | Title prefix | No added prefix | Title masked | Masked fixed window |
| --- | --- | --- | --- | --- |
| BM25 | 6.3 [1.1, 12.5] | 7.4 [1.2, 13.8] | 34.4 [21.2, 46.8] | 34.4 [21.1, 46.9] |
| mE5-small | 0.0 [0.0, 0.0] | 4.2 [1.0, 8.3] | 12.8 [3.5, 23.0] | 13.8 [4.6, 23.3] |

With title prefixes, mE5-small shows no measurable English-Uzbek difference because both languages are at ceiling. A small difference appears without the added prefix (4.2 points) and widens to 12.8 points [3.5, 23.0] after masking. The intervals exclude zero but are wide, and they describe this question set and corpus only.

### 5.4 Other cutoffs and alternate phrasings

**Table 5. Hit@1 / Hit@5 on original questions.**

| Retriever | Language | Title prefix | Title masked |
| --- | --- | --- | --- |
| BM25 | English | 98.0 / 99.0 | 68.0 / 78.0 |
| BM25 | Uzbek | 81.2 / 99.0 | 25.0 / 42.7 |
| mE5-small | English | 100.0 / 100.0 | 90.0 / 94.0 |
| mE5-small | Uzbek | 93.8 / 100.0 | 61.5 / 81.2 |

**Table 6. Hit@3 on alternate phrasings.**

| Retriever | English, title prefix | English, title masked | Uzbek, title prefix | Uzbek, title masked |
| --- | ---: | ---: | ---: | ---: |
| BM25 | 99.0% | 79.0% | 88.5% | 35.4% |
| mE5-small | 99.0% | 91.0% | 96.9% | 70.8% |

The pattern holds at k = 1 and k = 5 and on the alternate phrasings, which share sources with the original questions and are therefore not independent evidence.

### 5.5 Passage diagnostics

**Table 7. Lead-window length and masking extent (mE5-small tokens).**

| Language | Role | Articles | Median window | Window under 128 tokens | Any title removed | Mean share of tokens removed |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| English | target | 100 | 480 | 0.0% | 81.0% | 2.5% |
| English | background | 1,000 | 472 | 16.9% | 78.9% | 3.4% |
| Uzbek | target | 96 | 480 | 6.2% | 91.7% | 2.7% |
| Uzbek | background | 1,000 | 104 | 59.3% | 87.7% | 5.5% |

Masking removes a similar small share of tokens from English and Uzbek target passages (2.5% and 2.7% on average), so the larger Uzbek drop is not explained by more text being removed from targets. The background differs sharply: Uzbek background windows have a median of 104 tokens against 472 for English, and 59.3% are under 128 tokens. Many randomly sampled Uzbek articles are short stubs. Whether short distractors make masked Uzbek retrieval harder or easier is not identified by this design.

### 5.6 Additional retrievers

**[Pending: run `python scripts/run_title_masking_retrievers.py` on the frozen cache to add mE5-base, mE5-large and BGE-M3. This paragraph, Tables 2 and 3, Figure 1 and the abstract update automatically.]**

## 6. Discussion

The original pilot's ceiling is not evidence of strong retrieval in either language: once title strings are removed, every retriever loses accuracy in both languages, and BM25 loses most of its Uzbek performance. For benchmark construction, the implication is direct. Template questions that name their target measure title matching as much as retrieval, and reporting a title-masked or title-free variant alongside headline scores would make that visible.

The language difference is the more interesting and the less settled result. Several explanations fit the data and are not separated here. Uzbek is agglutinative, so unmasked inflected forms carry the entity in a different surface form from the question; the shared multilingual tokeniser may segment Uzbek less efficiently [18]; Uzbek background articles, and some Uzbek targets, are much shorter; and the two languages' question templates and subject mixes differ. Native-speaker questions that do not name their target, matched candidate pools, and morphology-aware lexical baselines would test these explanations directly.

## 7. Limitations

The questions are automatic templates, with about 100 sources per language, so intervals are wide and do not support population-level claims. The corpus deliberately contains every target, and random background articles are easier distractors than same-topic articles. Each article is represented by a single truncated lead passage. Masking removes exact title strings only; it does not remove inflected forms, synonyms or other entity clues, so it underestimates title reliance. All text is Wikipedia, Uzbek is in Latin script only, and retrieval is monolingual. Several comparisons are reported without multiplicity adjustment. Generation quality is not assessed.

Earlier repository reports of 39% to 98% Uzbek recall after targeted corpus supplementation used different corpora and settings, selected supplementary sources with knowledge of the evaluation targets, and lack recoverable prediction provenance. They are not used in this paper.

## 8. Reproducibility and data availability

Frozen revision manifests, ranked predictions, passage hashes and metrics are public in the repository ([title-masking package](../title_masking/README.md); [pilot package](../reproducible_pilot/README.md)). Article text stays local and is re-fetched by revision ID; acquisition stops on any hash mismatch. `scripts/verify_title_masking.py` recomputes every Hit@k cell and paired interval from the predictions and checks that title-prefixed rankings reproduce the original pilot exactly; `scripts/analyze_title_masking_gaps.py --check` recomputes the between-language intervals. Both use only the Python standard library and run in continuous integration. The title-masking runner's SHA-256 is `62a522995dac1676...`; full provenance is in each `metrics.json`.

The benchmark release is CC BY 4.0 ([DOI 10.5281/zenodo.21067667](https://doi.org/10.5281/zenodo.21067667); the DOI identifies the dataset, not this manuscript), and code is MIT-licensed. Wikipedia text retains its upstream licence and is not redistributed.

## 9. Conclusion

In this English-Uzbek pilot, near-ceiling retrieval scores depend substantially on article titles, and Uzbek retrieval depends on them more than English. The finding is a caution for small benchmarks built from entity-named templates, and a starting point rather than a conclusion about Uzbek retrieval: establishing a language effect requires natural questions that do not name their targets.

## Acknowledgements

All experiments in this paper ran locally on CPU without paid inference. Earlier development of the benchmark used the Isambard-AI supercomputer under project u6ef. This author-maintained work does not represent an official institutional position. **[Disclose any use of AI writing or coding assistance according to the target venue's policy.]**

## References

1. Lewis, P., et al. (2020). [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401). NeurIPS 2020.
2. Karpukhin, V., et al. (2020). [Dense Passage Retrieval for Open-Domain Question Answering](https://aclanthology.org/2020.emnlp-main.550/). EMNLP 2020.
3. Robertson, S., and Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. Foundations and Trends in Information Retrieval, 3(4), 333-389.
4. Wang, L., et al. (2024). [Multilingual E5 Text Embeddings: A Technical Report](https://arxiv.org/abs/2402.05672). arXiv:2402.05672.
5. intfloat. [multilingual-e5-small model card](https://huggingface.co/intfloat/multilingual-e5-small). Accessed 6 October 2026.
6. Chen, J., et al. (2024). [M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation](https://arxiv.org/abs/2402.03216). Findings of ACL 2024.
7. Conneau, A., et al. (2020). [Unsupervised Cross-lingual Representation Learning at Scale](https://aclanthology.org/2020.acl-main.747/). ACL 2020.
8. Zhang, X., et al. (2023). [MIRACL: A Multilingual Retrieval Dataset Covering 18 Diverse Languages](https://aclanthology.org/2023.tacl-1.63/). Transactions of the ACL, 11, 1114-1131.
9. Zhang, X., Ma, X., Shi, P., and Lin, J. (2021). [Mr. TyDi: A Multi-lingual Benchmark for Dense Retrieval](https://aclanthology.org/2021.mrl-1.12/). Workshop on Multilingual Representation Learning.
10. Clark, J. H., et al. (2020). [TyDi QA: A Benchmark for Information-Seeking Question Answering in Typologically Diverse Languages](https://aclanthology.org/2020.tacl-1.30/). Transactions of the ACL, 8, 454-470.
11. Asai, A., et al. (2021). [XOR QA: Cross-lingual Open-Retrieval Question Answering](https://aclanthology.org/2021.naacl-main.46/). NAACL 2021.
12. Thakur, N., et al. (2021). [BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://arxiv.org/abs/2104.08663). NeurIPS 2021 Datasets and Benchmarks Track.
13. Lee, K., Chang, M.-W., and Toutanova, K. (2019). [Latent Retrieval for Weakly Supervised Open Domain Question Answering](https://aclanthology.org/P19-1612/). ACL 2019.
14. Sciavolino, C., Zhong, Z., Lee, J., and Chen, D. (2021). [Simple Entity-Centric Questions Challenge Dense Retrievers](https://aclanthology.org/2021.emnlp-main.496/). EMNLP 2021.
15. Gururangan, S., et al. (2018). [Annotation Artifacts in Natural Language Inference Data](https://aclanthology.org/N18-2017/). NAACL 2018.
16. Geirhos, R., et al. (2020). Shortcut Learning in Deep Neural Networks. Nature Machine Intelligence, 2, 665-673.
17. Joshi, P., et al. (2020). [The State and Fate of Linguistic Diversity and Inclusion in the NLP World](https://aclanthology.org/2020.acl-main.560/). ACL 2020.
18. Rust, P., et al. (2021). [How Good is Your Tokenizer? On the Monolingual Performance of Multilingual Language Models](https://aclanthology.org/2021.acl-long.243/). ACL 2021.
19. Mansurov, B., and Mansurov, A. (2021). [UzBERT: Pretraining a BERT Model for Uzbek](https://arxiv.org/abs/2108.09814). arXiv:2108.09814.
20. Es, S., James, J., Espinosa Anke, L., and Schockaert, S. (2024). [RAGAs: Automated Evaluation of Retrieval Augmented Generation](https://aclanthology.org/2024.eacl-demo.16/). EACL System Demonstrations.

## Appendix A. Source-removal diagnostic

The original pilot removed half of each language's target pages (seed 42; seeds 43-46 in the pilot package) while holding questions and background fixed. Because a removed source cannot be retrieved, the reduced-corpus scores are close to the share of targets retained and are reported only for completeness.

**Table A1. Hit@3, complete versus seed-42 reduced corpus (title-prefix passages).**

| Language | Retriever | Complete | Half removed | Difference, pp [95% interval] |
| --- | --- | ---: | ---: | --- |
| English | BM25 | 99.0% | 49.0% | 50.0 [40.0, 60.0] |
| English | mE5-small | 100.0% | 50.0% | 50.0 [40.0, 60.0] |
| English | mE5-small, no prefixes | 100.0% | 50.0% | 50.0 [40.0, 60.0] |
| Uzbek | BM25 | 92.7% | 47.9% | 44.8 [34.4, 55.2] |
| Uzbek | mE5-small | 100.0% | 50.0% | 50.0 [39.6, 60.4] |
| Uzbek | mE5-small, no prefixes | 100.0% | 50.0% | 50.0 [39.6, 60.4] |
