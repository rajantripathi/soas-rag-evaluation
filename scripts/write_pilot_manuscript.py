"""Build the manuscript from verified pilot metrics; historical reports stay separate."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'research_outputs/reproducible_pilot'


def main():
    metrics=json.loads((PUBLIC/'metrics.json').read_text())
    intervals=json.loads((PUBLIC/'paired_intervals.json').read_text())
    mapping=json.loads((PUBLIC/'target_mapping.json').read_text())
    manifest=json.loads((PUBLIC/'run_manifest.json').read_text())
    methods={'bm25':'BM25','e5_prefixed':'E5 + prefixes','e5_unprefixed':'E5, no prefixes'}
    def metric(lang,method,condition='full',subset='original'):
        return next(m for m in metrics if m['language']==lang and m['method']==method and m['condition']==condition and m['subset']==subset and m['k']==3)
    def pct(v): return f'{100*v:.1f}%'
    main_table=['| Language | Retriever | Full Hit@3 | Removed Hit@3 | Gain (pp) | 95% paired interval (pp) |',
                '| --- | --- | ---: | ---: | ---: | --- |']
    seed_table=['| Language | Retriever | Seed 42 | Seed 43 | Seed 44 | Seed 45 | Seed 46 |',
                '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    sensitivity=['| Language | Retriever | Original Hit@3 | Alternate Hit@3 | Unflagged original Hit@3 (n) |',
                 '| --- | --- | ---: | ---: | --- |']
    for lang in ('en','uz'):
        for method,label in methods.items():
            full=metric(lang,method);removed=metric(lang,method,'removed_42')
            interval=next(v for v in intervals if v['language']==lang and v['method']==method)
            main_table.append(f"| {lang} | {label} | {pct(full['hit_rate'])} | {pct(removed['hit_rate'])} | {100*interval['difference']:.1f} | [{100*interval['lower']:.1f}, {100*interval['upper']:.1f}] |")
            seed_table.append('| '+lang+' | '+label+' | '+' | '.join(pct(metric(lang,method,f'removed_{s}')['hit_rate']) for s in range(42,47))+' |')
            variants=metric(lang,method,subset='variants');unflagged=metric(lang,method,subset='unflagged_original')
            sensitivity.append(f"| {lang} | {label} | {pct(full['hit_rate'])} | {pct(variants['hit_rate'])} | {pct(unflagged['hit_rate'])} ({unflagged['rows']}) |")
    en=metric('en','e5_prefixed');uz=metric('uz','e5_prefixed')
    en_removed=metric('en','e5_prefixed','removed_42');uz_removed=metric('uz','e5_prefixed','removed_42')
    excluded='; '.join(f"{m['requested_title']} (legacy ID {m['legacy_id']})" for m in mapping if m['status']!='resolved')
    text=f'''# Controlled Source Availability in an English-Uzbek Retrieval Pilot

**Rajan Prasad Tripathi**

AI² Lab, American University of Technology, Uzbekistan; Centre for AI Futures, SOAS University of London

**Status:** Working preprint manuscript. The local experiment and tables below are reproducible research outputs, not a claim of peer-reviewed publication. The previously reported Isambard results are historical context only.

## Abstract

Retrieval depends on whether relevant sources are available as well as whether a retriever can rank them. We construct a reproducible source-availability diagnostic from an English-Uzbek pilot release covering governance, history, institutions, and culture. The release contains 400 question phrasings linked to 200 language-scoped targets. We resolve 196 targets and freeze their Wikipedia revisions with 1,000 background articles per language. We evaluate BM25 and multilingual E5-small, including a prefix ablation, on complete and reduced candidate pools. Correctly prefixed E5 achieves source hit rates at three of {pct(en['hit_rate'])} for English and {pct(uz['hit_rate'])} for Uzbek on the original questions with all resolved targets available. After removing half the target sources under the predeclared primary mask, the corresponding scores are {pct(en_removed['hit_rate'])} and {pct(uz_removed['hit_rate'])}. We report five removal masks, conditional retrieval scores, and source-group-aware paired intervals. These results describe controlled recovery of designated sources in small target-aware corpora; they do not establish performance on unseen sources or final answer quality. Code, revision manifests, model provenance, and retrieval-only predictions make the new experiment independently inspectable.

## 1. Introduction

Two distinct mechanisms can produce a retrieval miss: the intended source is absent, or the retriever fails to rank a source that is present. Model comparisons alone cannot distinguish them. A controlled source-removal experiment makes availability explicit while holding questions and background articles fixed.

This paper presents such a diagnostic using an English-Uzbek collection. The contribution is a reproducible experimental artifact with explicit source mappings, availability interventions, implementation ablations, and evidence boundaries. We ask how source hit rate changes when designated sources are removed and restored, how ranking differs between BM25 and multilingual E5-small, and how alternate question phrasings affect the result.

Removing a gold source mechanically prevents a designated-source hit for that question. We do not present that ceiling as a novel empirical discovery. The informative measurements are retrieval conditional on source presence, differences between implementations, and sensitivity to wording and removal masks. The experiment is not a representative estimate of deployment performance or a validation of cultural coverage.

## 2. Related work

MIRACL provides monolingual retrieval evaluation across 18 languages with native-speaker relevance judgments [1]. TyDi QA addresses information-seeking question answering across typologically diverse languages [2]. They motivate multilingual evaluation without establishing the quality of this smaller collection.

Multilingual E5 provides contrastively trained embedding models [3]. Its model card specifies query and passage prefixes for retrieval [4]; we explicitly compare prefixed and unprefixed encoding. RAGAs provides automated assessment of retrieval-augmented generation [5]. Our release supports the narrower task of designated-source retrieval and contains neither generated answers nor reference answers for assessing generation.

The present work is a controlled diagnostic and an inspectable pilot resource. It does not claim a new retrieval algorithm, superiority over established multilingual benchmarks, or a comprehensive review of corpus-curation research.

## 3. Benchmark and frozen corpus

### 3.1 Questions and source dependence

The existing release contains 200 original questions and 200 deterministic alternate phrasings. Each of its 200 language-scoped source targets appears in two question rows. The English and Uzbek halves are not translations. Each language-domain cell contains 25 original and 25 alternate questions. Twenty rows have quality flags; flagging is incomplete. Difficulty labels are heuristic rather than human difficulty ratings.

We preserve this release unchanged. The 200 original questions define the primary analysis; alternate phrasings form a separate sensitivity analysis. Related phrasings are never treated as independent source observations. Neither balanced labels nor the absence of a flag establishes cultural representativeness or linguistic quality.

### 3.2 Target resolution

English source titles and Uzbek page IDs are resolved against Wikipedia, retaining mappings to the original benchmark identifiers. Uzbek resolutions are checked against stored titles, allowing recorded redirects. Missing, short, nonarticle, and title-mismatched resolutions are excluded rather than replaced with guessed topics. A minimum of 90 resolved original targets per language was required before reporting a bilingual experiment.

All 100 English targets and 96 Uzbek targets resolved. The four Uzbek exclusions are: {excluded}. Reasons and mappings are recorded in the public resolution file; exclusion does not mean that the topic lacks valid evidence elsewhere.

**Table 1. Eligible questions and candidate articles.**

| Language | Resolved targets | Original questions | Alternate questions | Background articles | Full candidate articles |
| --- | ---: | ---: | ---: | ---: | ---: |
| English | 100 | 100 | 100 | 1,000 | 1,100 |
| Uzbek | 96 | 96 | 96 | 1,000 | 1,096 |

### 3.3 Background and article representation

Background articles were sampled once from Wikipedia main-namespace nonredirect pages, excluding resolved targets. Articles with fewer than 100 characters after extraction were rejected. The resulting 1,000 background articles per language were frozen; reproduction uses their revision IDs, not a new random draw. This is a service-generated random sample, not a claim of seed-reproducible sampling or representative domain coverage.

We record page and revision IDs, titles, timestamps, URLs, and raw and extracted-text hashes. A pinned `mwparserfromhell` version strips markup and whitespace is collapsed. Each candidate is represented by its title followed by opening article text, capped at 480 E5 tokenizer tokens and decoded to a common passage string. BM25 and E5 use that same passage string before adding model-specific prefixes. This representation is a lead-passage diagnostic, not full-document retrieval.

## 4. Experimental protocol

### 4.1 Retrieval implementations

BM25 uses the repository implementation with k1=1.5 and b=0.75, Unicode word tokenisation, and lowercasing. Its statistics are recomputed for each corpus condition. E5-small uses normalised embeddings and dot-product ranking, with a pinned model revision. The prefixed condition adds `query: ` to questions and `passage: ` to passages; the unprefixed condition omits both. This ablation is not a separate trained model.

Execution uses CPU, four PyTorch threads, batches of eight, and a model sequence limit of 512 tokens. Dense embeddings are cached by input, prefix, model revision, and software versions. Rankings use document-ID tie breaking. Queries search only their own language's candidates. All retrievers return up to five articles, including tied zero-score BM25 candidates, using the same deterministic tie rule.

### 4.2 Source removal and restoration

The complete condition contains all resolved targets and the fixed background. Five reduced conditions remove half the unique target pages within each language using seeds 42-46. Thus each reduced corpus retains 50 English or 48 Uzbek target pages. All phrasings sharing a target share its availability. Background articles remain unchanged, and the complete condition restores the exact removed revisions.

The target-aware construction deliberately uses evaluation labels. It is a controlled availability intervention, not a corpus curated independently of the test questions. It cannot demonstrate held-out source generalisation. Source overlap or alternative relevant evidence among background articles is not assessed; the endpoint is recovery of the designated page ID.

### 4.3 Measures and uncertainty

For question i with designated source G_i and top-k retrieved IDs R_i, the source hit is 1 if G_i appears in R_i and 0 otherwise. Hit@k is the mean over questions. We report k=1, 3, and 5, with k=3 primary, together with source availability and hit rate conditional on availability. The repository historically calls this Recall@k; it is a designated-source hit rate rather than recall over an exhaustively judged relevance set.

Primary paired intervals compare the complete corpus with seed-42 removal at k=3. We use 10,000 bootstrap resamples of source groups separately within each language. The 196 eligible original questions have distinct source groups. These descriptive resampling intervals condition on the frozen corpus, questions, and primary mask. The questions are not a probability sample of a wider population, so the intervals do not justify population-level generalisation. They do not capture background sampling, annotation uncertainty, or variability across removal masks; the five masks are reported individually. No omnibus significance or model-superiority claim is made.

## 5. Results

### 5.1 Complete and primary reduced corpus

The reduced corpus has 50% designated-source availability in each language; the complete corpus has 100%. Table 2 reports original questions only. Gains refer to restoration, with all other corpus content fixed. The prefixed E5 conditional Hit@3 under removal is {pct(en_removed['conditional_hit_rate'])} for English and {pct(uz_removed['conditional_hit_rate'])} for Uzbek. Complete-corpus conditional rates equal complete-corpus hit rates.

**Table 2. Primary Hit@3 results and source-bootstrap intervals.**

{chr(10).join(main_table)}

Both E5 variants saturate original-question Hit@3 in both languages, so this endpoint cannot discriminate their prefix settings on the complete candidate pools. At Hit@1, the prefixed and unprefixed Uzbek scores are 90/96 and 91/96, respectively; this pilot therefore does not support a claim that prefixes improved observed retrieval. The unprefixed condition remains an ablation rather than a recommended implementation.

The size of a restoration gain partly reflects the imposed availability ceiling. It should not be interpreted as evidence that source additions generally dominate embedding changes. The accompanying prefix ablation measures an implementation choice within E5-small on these candidate pools; it does not reproduce the historical E5-large-versus-mpnet comparison.

### 5.2 Removal-mask sensitivity

Table 3 gives Hit@3 for all five reduced corpora. Variation reflects which targets were removed and, for BM25, changes in corpus-dependent statistics. No favourable seed is selected after evaluation.

**Table 3. Hit@3 across the five reduced corpora.**

{chr(10).join(seed_table)}

### 5.3 Question and flag sensitivity

Table 4 reports complete-corpus performance. Alternate questions use the same sources. The unflagged-original subset excludes existing flags only and is not described as a clean or independently validated set. Different subset denominators prevent interpreting every percentage change as a paired effect.

**Table 4. Complete-corpus question and flag sensitivity.**

{chr(10).join(sensitivity)}

All k=1 and k=5 results, availability-conditioned scores, and all subset/condition combinations are provided in the machine-readable metrics. The report generator validates prediction completeness and source identities before computing these tables.

## 6. Historical context and limitations

Earlier repository reports describe 39% to 98% Uzbek recall after targeted supplementation with E5-large on 100 Uzbek questions. Those reports used different corpora and implementation settings, and their complete prediction provenance was not recovered. They are not rerun results and are not pooled with this experiment. Earlier effect sizes and inferential statistics remain excluded from this paper's new conclusions. An English synthetic-supplement experiment was retracted because reference-answer text entered the corpus.

The current corpus is small and deliberately contains the resolved target set; random background articles may be easier distractors than domain-matched negatives. Source titles in questions can further simplify matching. Frozen Wikipedia revisions may differ from the historical source material, and truncation can remove relevant evidence. Background selection and target exclusions may affect language comparisons.

The benchmark retains domain mismatches and template artifacts. Human annotation and relevance assessment have not been completed. A source hit does not establish that the selected lead passage answers the question, and valid alternative sources can be counted as misses. These limitations prevent claims of semantic answer correctness, cultural representativeness, or broad low-resource-language performance.

A confirmatory study requires new source-disjoint questions, bilingual review, harder candidate pools, and corpus decisions made before inspecting test labels. Retrospectively partitioning this target-aware experiment would not create an untouched test set. Generation quality and cross-lingual retrieval remain outside scope.

## 7. Reproducibility and data availability

The [pilot package](../reproducible_pilot/README.md) includes the protocol, source manifest, legacy-to-canonical mapping, model revision, run metadata, retrieval-only predictions, metrics, and paired intervals. Source content and embedding caches stay local; source revisions can be fetched by the manifest. Acquisition stops on unavailable or mismatched revisions rather than substituting current content. Inputs, dependencies, and code are hashed, and runs can resume cached batches.

The executable runner used Git commit `{manifest['git_commit']}` with SHA-256 `{manifest['runner_sha256']}`. Its full model and package provenance is in `run_manifest.json`. Public predictions contain identifiers and analysis metadata, not source passages or answers. The unchanged benchmark release is available under [DOI 10.5281/zenodo.21067667](https://doi.org/10.5281/zenodo.21067667); that DOI identifies the dataset rather than this manuscript.

Code is MIT-licensed and the benchmark release is CC BY 4.0. Wikipedia material retains its upstream terms; these repository labels do not relicense downloaded source text. The public manifest provides source attribution and revision links.

## 8. Conclusion

This pilot makes corpus availability an explicit, reproducible experimental variable. It pairs frozen source revisions with public ranked predictions and separates original questions from dependent alternate phrasings. The measured results describe retrieval of designated sources in a controlled bilingual candidate pool. They support an inspectable diagnostic artifact and further source-disjoint evaluation, rather than a universal claim about corpus curation or model selection.

## Acknowledgements

The new experiment ran locally without paid inference or cluster compute. Earlier reported work used Isambard-AI under project u6ef; this historical acknowledgement does not imply current access. This author-maintained artifact does not represent an official institutional position.

## References

1. Zhang, X., et al. (2023). [MIRACL: A Multilingual Retrieval Dataset Covering 18 Diverse Languages](https://aclanthology.org/2023.tacl-1.63/). Transactions of the Association for Computational Linguistics, 11, 1114-1131.
2. Clark, J. H., et al. (2020). [TyDi QA: A Benchmark for Information-Seeking Question Answering in Typologically Diverse Languages](https://aclanthology.org/2020.tacl-1.30/). Transactions of the Association for Computational Linguistics, 8, 454-470.
3. Wang, L., et al. (2024). [Multilingual E5 Text Embeddings: A Technical Report](https://arxiv.org/abs/2402.05672). arXiv:2402.05672.
4. intfloat. [multilingual-e5-small model card](https://huggingface.co/intfloat/multilingual-e5-small). Retrieval prefix and model usage documentation, accessed 6 October 2026.
5. Es, S., James, J., Espinosa Anke, L., and Schockaert, S. (2024). [RAGAs: Automated Evaluation of Retrieval Augmented Generation](https://aclanthology.org/2024.eacl-demo.16/). EACL System Demonstrations, 150-158.
'''
    (ROOT/'research_outputs/workshop_paper_2026/paper_final.md').write_text(text)
    print('Manuscript regenerated from verified metrics')


if __name__=='__main__': main()
