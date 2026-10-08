"""Write the title-sensitivity preprint from verified metrics, then build its figure and PDF.

Every number in the manuscript is read from committed, verifiable artifacts:

* research_outputs/title_masking/frozen/{metrics.json, passage_audit.jsonl}
* research_outputs/title_masking/frozen_retrievers/metrics.json   (optional; added when run)
* research_outputs/title_masking/language_gaps.json
* research_outputs/reproducible_pilot/{metrics.json, paired_intervals.json, target_mapping.json}

    python scripts/analyze_title_masking_gaps.py
    python scripts/write_title_sensitivity_manuscript.py           # Markdown + figure + PDF
    python scripts/write_title_sensitivity_manuscript.py --no-pdf  # Markdown only
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TM = ROOT / 'research_outputs/title_masking'
PILOT = ROOT / 'research_outputs/reproducible_pilot'
OUT_DIR = ROOT / 'research_outputs/preprint_2026'
PAPER = OUT_DIR / 'title_sensitivity.md'
FIGURE = OUT_DIR / 'title_masking_dumbbell'
PDF = ROOT / 'output/pdf/en-uz-title-sensitivity.pdf'
TITLE = 'Title Evidence and Retrieval in an English-Uzbek Pilot: A Frozen-Corpus Sensitivity Analysis'

LABELS = {'bm25': 'BM25', 'e5_prefixed': 'mE5-small', 'e5_base': 'mE5-base', 'e5_large': 'mE5-large', 'bge_m3': 'BGE-M3 (dense)'}
VARIANT_LABELS = ['title_prefix', 'no_prefix', 'title_masked', 'title_masked_fixed_window']
LANG = {'en': 'English', 'uz': 'Uzbek'}


def load(path):
    return json.loads(Path(path).read_text())


def collect():
    frozen = load(TM / 'frozen/metrics.json')
    runs = [frozen]
    extra_path = TM / 'frozen_retrievers/metrics.json'
    extra = load(extra_path) if extra_path.exists() else None
    if extra and not extra['approximate']:
        runs.append(extra)
    else:
        extra = None
    cells, drops, methods = {}, {}, []
    for run in runs:
        for m in run['methods']:
            methods.append(m)
        for r in run['results']:
            cells[(r['method'], r['language'], r['variant'], r['questions'])] = r
        for d in run['title_masking_drop']:
            drops[(d['method'], d['language'])] = d
    gaps = load(TM / 'language_gaps.json')['rows']
    gap = {(g['method'], g['variant'], g['measure']): g for g in gaps}
    return frozen, extra, methods, cells, drops, gap


def passage_stats():
    rows = [json.loads(line) for line in (TM / 'frozen/passage_audit.jsonl').read_text().splitlines()]
    index = {(r['doc_id'], r['variant']): r for r in rows}
    stats = {}
    for language in ('en', 'uz'):
        for role in ('target', 'background'):
            ids = sorted({r['doc_id'] for r in rows if r['doc_id'].startswith(language + ':') and r['role'] == role})
            window = [index[(d, 'no_prefix')]['tokens'] for d in ids]
            masked = [index[(d, 'title_masked_fixed_window')]['tokens'] for d in ids]
            stats[(language, role)] = dict(
                n=len(ids), median=statistics.median(window),
                short=100 * sum(w < 128 for w in window) / len(window),
                removed=100 * statistics.mean((w - m) / w for w, m in zip(window, masked) if w),
                any_removed=100 * sum(w > m for w, m in zip(window, masked)) / len(window))
    return stats


def figure(methods, cells):
    os.environ.setdefault('MPLCONFIGDIR', str(ROOT / 'tmp/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['svg.hashsalt'] = 'en-uz-title-sensitivity-v1'
    import matplotlib.pyplot as plt
    before_color, after_color, ink, muted = '#86b6ef', '#1c5cab', '#0b0b0b', '#52514e'
    order = list(reversed(methods))
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 0.62 * len(methods) + 1.35), sharey=True)
    for ax, language in zip(axes, ('en', 'uz')):
        for y, method in enumerate(order):
            a = cells[(method, language, 'title_prefix', 'original')]['hit@3']
            b = cells[(method, language, 'title_masked', 'original')]['hit@3']
            ax.plot([b, a], [y, y], color='#c3c2b7', linewidth=2, zorder=1, solid_capstyle='round')
            ax.scatter([a], [y], s=64, color=before_color, edgecolor='white', linewidth=1.5, zorder=2,
                       label='Title prefix (pilot protocol)' if y == 0 else None)
            ax.scatter([b], [y], s=64, color=after_color, edgecolor='white', linewidth=1.5, zorder=3,
                       label='Title masked' if y == 0 else None)
            ax.annotate(f'{b:.1f}', (b, y), xytext=(-7, 0), textcoords='offset points', ha='right', va='center',
                        fontsize=8, color=ink)
        ax.set_title(f"{LANG[language]} ({cells[(methods[0], language, 'title_prefix', 'original')]['n']} original questions)",
                     fontsize=10, color=ink)
        ax.set_xlim(0, 104)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.tick_params(colors=muted, labelsize=8)
        ax.set_yticks(range(len(order)), [LABELS[m] for m in order], fontsize=8.5, color=ink)
        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.spines['bottom'].set_color('#c3c2b7')
        ax.grid(axis='x', alpha=.18)
        ax.set_axisbelow(True)
        ax.set_xlabel('Hit@3 (%)', fontsize=8.5, color=muted)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=2, frameon=False, fontsize=8.5)
    fig.tight_layout(rect=(0, .09, 1, 1))
    fig.savefig(FIGURE.with_suffix('.png'), dpi=240)
    fig.savefig(FIGURE.with_suffix('.svg'), metadata={'Date': None})
    svg = FIGURE.with_suffix('.svg')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    plt.close(fig)
    return fig.get_size_inches()


def pct(v):
    return f'{v:.1f}%'


def ci(values):
    return f'[{values[0]:.1f}, {values[1]:.1f}]'


def write(frozen, extra, methods, cells, drops, gap, stats, save=True):
    h = lambda m, l, v, k=3, q='original': cells[(m, l, v, q)][f'hit@{k}']
    overlap = frozen['title_overlap']
    mapping = load(PILOT / 'target_mapping.json')
    excluded = '; '.join(f"\"{m['requested_title']}\" (legacy ID {m['legacy_id']})" for m in mapping if m['status'] != 'resolved')
    lock = frozen['model']
    did = {m: gap[(m, 'title_prefix_to_title_masked', 'uz_drop_minus_en_drop')] for m in methods}
    g = lambda m, v: gap[(m, v, 'en_minus_uz_hit@3')]
    extra_methods = [m for m in methods if m not in ('bm25', 'e5_prefixed')]
    all_drop = all(drops[(m, l)]['drop_pp'] > 0 for m in methods for l in ('en', 'uz'))
    opening = ('once title strings are removed, every retriever loses accuracy in both languages' if all_drop else
               'once title strings are removed, accuracy falls for most retriever and language combinations')

    if extra_methods:
        uz_vals = [h(m, 'uz', 'title_masked') for m in extra_methods]
        en_vals = [h(m, 'en', 'title_masked') for m in extra_methods]
        larger_uz = sum(drops[(m, 'uz')]['drop_pp'] > drops[(m, 'en')]['drop_pp'] for m in extra_methods)
        names = ', '.join(LABELS[m] for m in extra_methods)
        extra_abstract = (f' Three larger dense retrievers ({names}) reach between {min(uz_vals):.1f}% and {max(uz_vals):.1f}% '
                          f'Uzbek Hit@3 after masking, against {min(en_vals):.1f}% to {max(en_vals):.1f}% for English; '
                          f'the Uzbek drop is larger for {larger_uz} of {len(extra_methods)}.') if len(extra_methods) == 3 else (
                          f' Additional dense retrievers ({names}) reach {min(uz_vals):.1f}% to {max(uz_vals):.1f}% Uzbek Hit@3 after masking, '
                          f'against {min(en_vals):.1f}% to {max(en_vals):.1f}% for English.')
        extra_results = (f'Table 2 includes {names}, run with pinned revisions on byte-identical passages '
                         f'(`configs/title_masking_retrievers.json`). After masking, Uzbek Hit@3 ranges from {min(uz_vals):.1f}% to {max(uz_vals):.1f}% '
                         f'and English from {min(en_vals):.1f}% to {max(en_vals):.1f}%. The Uzbek drop exceeds the English drop for '
                         f'{larger_uz} of {len(extra_methods)} additional retrievers (Table 3). Model size and training data differ jointly across '
                         'these models, so the comparison is descriptive rather than a test of scale.')
        retriever_list = ('Additional dense retrievers are ' + '; '.join(
            f"{LABELS[r['name']]} (`{r['model_id']}`, revision `{r['revision'][:12]}`, "
            + (f"prefixes `{r['query_prefix'].strip()}`/`{r['passage_prefix'].strip()}`" if r['query_prefix'] else 'no prefixes')
            + ')' for r in extra['retrievers']) + '. They encode the same passages, with a 512-token sequence limit.')
    else:
        extra_abstract = ''
        extra_results = ('**[Pending: run `python scripts/run_title_masking_retrievers.py` on the frozen cache to add mE5-base, '
                         'mE5-large and BGE-M3. This paragraph, Tables 2 and 3, Figure 1 and the abstract update automatically.]**')
        retriever_list = '**[Pending: additional dense retrievers.]**'

    main_rows = []
    for m in methods:
        for l in ('en', 'uz'):
            main_rows.append(f"| {LABELS[m]} | {LANG[l]} | " + ' | '.join(pct(h(m, l, v)) for v in VARIANT_LABELS) + ' |')
    drop_rows = [f"| {LABELS[m]} | {pct(h(m, 'en', 'title_prefix'))} to {pct(h(m, 'en', 'title_masked'))} | "
                 f"{drops[(m, 'en')]['drop_pp']:.1f} {ci(drops[(m, 'en')]['ci95_pp'])} | "
                 f"{pct(h(m, 'uz', 'title_prefix'))} to {pct(h(m, 'uz', 'title_masked'))} | "
                 f"{drops[(m, 'uz')]['drop_pp']:.1f} {ci(drops[(m, 'uz')]['ci95_pp'])} | "
                 f"{did[m]['value_pp']:.1f} {ci(did[m]['ci95_pp'])} |" for m in methods]
    gap_rows = [f"| {LABELS[m]} | " + ' | '.join(f"{g(m, v)['value_pp']:.1f} {ci(g(m, v)['ci95_pp'])}" for v in VARIANT_LABELS) + ' |'
                for m in methods]
    alt_rows = [f"| {LABELS[m]} | " + ' | '.join(pct(h(m, l, v, q='alternate')) for l in ('en', 'uz') for v in ('title_prefix', 'title_masked')) + ' |'
                for m in methods]
    k_rows = [f"| {LABELS[m]} | {LANG[l]} | " + ' | '.join(f"{h(m, l, v, 1):.1f} / {h(m, l, v, 5):.1f}" for v in ('title_prefix', 'title_masked')) + ' |'
              for m in ('bm25', 'e5_prefixed') for l in ('en', 'uz')]
    s = stats
    stat_rows = [f"| {LANG[l]} | {role} | {s[(l, role)]['n']:,} | {s[(l, role)]['median']:.0f} | {s[(l, role)]['short']:.1f}% | "
                 f"{s[(l, role)]['any_removed']:.1f}% | {s[(l, role)]['removed']:.1f}% |"
                 for l in ('en', 'uz') for role in ('target', 'background')]

    pilot = load(PILOT / 'metrics.json')
    pilot_intervals = load(PILOT / 'paired_intervals.json')
    pm = lambda l, m, c: next(x for x in pilot if x['language'] == l and x['method'] == m and x['condition'] == c and x['subset'] == 'original' and x['k'] == 3)
    pilot_rows = []
    for l in ('en', 'uz'):
        for m, label in (('bm25', 'BM25'), ('e5_prefixed', 'mE5-small'), ('e5_unprefixed', 'mE5-small, no prefixes')):
            iv = next(v for v in pilot_intervals if v['language'] == l and v['method'] == m)
            pilot_rows.append(f"| {LANG[l]} | {label} | {pct(100 * pm(l, m, 'full')['hit_rate'])} | {pct(100 * pm(l, m, 'removed_42')['hit_rate'])} | "
                              f"{100 * iv['difference']:.1f} [{100 * iv['lower']:.1f}, {100 * iv['upper']:.1f}] |")
    nl = '\n'

    text = f'''# {TITLE}

**Rajan Prasad Tripathi** **[co-authors to be confirmed]**

AI² Lab, American University of Technology, Uzbekistan; Centre for AI Futures, SOAS University of London

**Status:** Draft for co-author review, generated from verified repository metrics. Not yet posted or peer reviewed.

## Abstract

Retrieval benchmarks for under-resourced languages are often built around article titles, which can let a retriever succeed by matching the named entity rather than the content. We examine this in an English-Uzbek pilot with {overlap['en']['targets_in_corpus']} English and {overlap['uz']['targets_in_corpus']} Uzbek frozen Wikipedia target articles and 1,000 random background articles per language. {overlap['en']['title_in_question']} of {overlap['en']['original_questions']} English and {overlap['uz']['title_in_question']} of {overlap['uz']['original_questions']} Uzbek original questions contain their target's title. We compare four passage representations, including title masking with a fixed-window control, applied to every candidate. With the title-prefixed passages of the original pilot, multilingual E5-small (mE5-small) places the target in the top three for every question in both languages. Masking each article's own title lowers its Hit@3 to {pct(h('e5_prefixed', 'en', 'title_masked'))} for English and {pct(h('e5_prefixed', 'uz', 'title_masked'))} for Uzbek; BM25 falls to {pct(h('bm25', 'en', 'title_masked'))} and {pct(h('bm25', 'uz', 'title_masked'))}. The Uzbek drop exceeds the English drop by {did['e5_prefixed']['value_pp']:.1f} percentage points for mE5-small (95% bootstrap interval {ci(did['e5_prefixed']['ci95_pp'])}) and {did['bm25']['value_pp']:.1f} for BM25 ({ci(did['bm25']['ci95_pp'])}).{extra_abstract} Near-ceiling scores in this pilot therefore rest substantially on title evidence, more so for Uzbek. The design does not identify why the languages differ; question construction, background passage length, morphology and tokenisation remain plausible explanations. We release ranked predictions, passage hashes and verification scripts.

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

The pilot release contains 200 original questions and 200 deterministic alternate phrasings, balanced across governance, history, institutions and culture. The English and Uzbek halves are not translations, and difficulty labels are heuristic. Questions are short templates; all {overlap['uz']['original_questions']} resolved Uzbek and {overlap['en']['title_in_question']} of {overlap['en']['original_questions']} English original questions contain the normalised target title.

Targets were resolved to Wikipedia pages and frozen at recorded revisions with raw and extracted-text hashes. All 100 English and 96 Uzbek targets resolved; the four Uzbek exclusions are {excluded}. Each language adds 1,000 background articles sampled once from main-namespace nonredirect pages and frozen by revision ID. Retrieval is within language, over the complete corpus.

**Table 1. Questions and candidates.**

| Language | Original questions | Title in question | Alternate phrasings | Background articles | Candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| English | {overlap['en']['original_questions']} | {overlap['en']['title_in_question']} | {cells[('e5_prefixed', 'en', 'title_prefix', 'alternate')]['n']} | {overlap['en']['background']:,} | {overlap['en']['candidates']:,} |
| Uzbek | {overlap['uz']['original_questions']} | {overlap['uz']['title_in_question']} | {cells[('e5_prefixed', 'uz', 'title_prefix', 'alternate')]['n']} | {overlap['uz']['background']:,} | {overlap['uz']['candidates']:,} |

## 4. Method

### 4.1 Passage representations

Each candidate is represented by one lead passage of at most 480 tokens of the pinned mE5-small tokeniser. We compare four representations, each applied to every candidate in the corpus:

- **Title prefix**: title + ". " + article lead, truncated (the original pilot protocol);
- **No added prefix**: the lead only; the title still appears wherever the article mentions it;
- **Title masked**: every occurrence of the article's own title, and of its form without a parenthetical disambiguator, is removed from the lead before truncation;
- **Masked fixed window**: the same 480-token window as "no added prefix" is selected first and then masked, so later text cannot replace removed tokens.

Matching is case-insensitive, tolerates Uzbek apostrophe variants (ʻ, ʼ, ' and similar) and uses Unicode word boundaries, so masking "Art" leaves "Earth" intact. Inflected forms such as "Toshkentda" are not masked, and synonyms and partial names remain; the procedure removes exact title strings only.

### 4.2 Retrievers

BM25 uses the repository implementation (k1 = 1.5, b = 0.75, Unicode word tokenisation, lowercasing). mE5-small (`{lock['model_id']}`, revision `{lock['revision'][:12]}`) uses `query: ` and `passage: ` prefixes, normalised embeddings and dot-product ranking. {retriever_list} Ties are broken by document ID.

### 4.3 Measures

Hit@k is the share of questions whose designated source appears in the top k (k = 1, 3, 5; k = 3 primary). Original questions, one per distinct source, form the primary analysis; alternate phrasings are reported separately and never pooled. Within-language drops use a paired bootstrap over source groups (10,000 resamples, seed 42). Between-language differences, and differences between the two languages' drops, use an unpaired bootstrap that resamples each language independently. Intervals are descriptive, condition on the frozen corpus and questions, and are not adjusted for the number of comparisons.

## 5. Results

### 5.1 Main results

**Table 2. Hit@3 on original questions, complete corpus.**

| Retriever | Language | Title prefix | No added prefix | Title masked | Masked fixed window |
| --- | --- | ---: | ---: | ---: | ---: |
{nl.join(main_rows)}

With the pilot's title-prefixed passages, mE5-small reaches {pct(h('e5_prefixed', 'en', 'title_prefix'))} in both languages and BM25 {pct(h('bm25', 'en', 'title_prefix'))} (English) and {pct(h('bm25', 'uz', 'title_prefix'))} (Uzbek). Removing only the added prefix changes little, because titles recur in article leads. Masking those occurrences produces the large drops. The fixed-window control gives nearly the same values, so the drops are not caused by later text being drawn into masked passages.

### 5.2 Drops within each language

**Table 3. Hit@3 drop from title prefix to title masked, in percentage points with 95% intervals.**

| Retriever | English Hit@3 | English drop | Uzbek Hit@3 | Uzbek drop | Uzbek minus English drop |
| --- | --- | --- | --- | --- | --- |
{nl.join(drop_rows)}

Both languages lose accuracy under masking, and Uzbek loses more under both BM25 and mE5-small. The dense retriever is far less sensitive than BM25: mE5-small keeps {pct(h('e5_prefixed', 'uz', 'title_masked'))} of Uzbek targets in the top three where BM25 keeps {pct(h('bm25', 'uz', 'title_masked'))}.

### 5.3 Between-language differences

**Table 4. English minus Uzbek Hit@3, in percentage points with 95% intervals.**

| Retriever | Title prefix | No added prefix | Title masked | Masked fixed window |
| --- | --- | --- | --- | --- |
{nl.join(gap_rows)}

With title prefixes, mE5-small shows no measurable English-Uzbek difference because both languages are at ceiling. A small difference appears without the added prefix ({g('e5_prefixed', 'no_prefix')['value_pp']:.1f} points) and widens to {g('e5_prefixed', 'title_masked')['value_pp']:.1f} points {ci(g('e5_prefixed', 'title_masked')['ci95_pp'])} after masking. The intervals exclude zero but are wide, and they describe this question set and corpus only.

### 5.4 Other cutoffs and alternate phrasings

**Table 5. Hit@1 / Hit@5 on original questions.**

| Retriever | Language | Title prefix | Title masked |
| --- | --- | --- | --- |
{nl.join(k_rows)}

**Table 6. Hit@3 on alternate phrasings.**

| Retriever | English, title prefix | English, title masked | Uzbek, title prefix | Uzbek, title masked |
| --- | ---: | ---: | ---: | ---: |
{nl.join(alt_rows)}

The pattern holds at k = 1 and k = 5 and on the alternate phrasings, which share sources with the original questions and are therefore not independent evidence.

### 5.5 Passage diagnostics

**Table 7. Lead-window length and masking extent (mE5-small tokens).**

| Language | Role | Articles | Median window | Window under 128 tokens | Any title removed | Mean share of tokens removed |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
{nl.join(stat_rows)}

Masking removes a similar small share of tokens from English and Uzbek target passages ({s[('en', 'target')]['removed']:.1f}% and {s[('uz', 'target')]['removed']:.1f}% on average), so the larger Uzbek drop is not explained by more text being removed from targets. The background differs sharply: Uzbek background windows have a median of {s[('uz', 'background')]['median']:.0f} tokens against {s[('en', 'background')]['median']:.0f} for English, and {s[('uz', 'background')]['short']:.1f}% are under 128 tokens. Many randomly sampled Uzbek articles are short stubs. Whether short distractors make masked Uzbek retrieval harder or easier is not identified by this design.

### 5.6 Additional retrievers

{extra_results}

## 6. Discussion

The original pilot's ceiling is not evidence of strong retrieval in either language: {opening}, and BM25 loses most of its Uzbek performance. For benchmark construction, the implication is direct. Template questions that name their target measure title matching as much as retrieval, and reporting a title-masked or title-free variant alongside headline scores would make that visible.

The language difference is the more interesting and the less settled result. Several explanations fit the data and are not separated here. Uzbek is agglutinative, so unmasked inflected forms carry the entity in a different surface form from the question; the shared multilingual tokeniser may segment Uzbek less efficiently [18]; Uzbek background articles, and some Uzbek targets, are much shorter; and the two languages' question templates and subject mixes differ. Native-speaker questions that do not name their target, matched candidate pools, and morphology-aware lexical baselines would test these explanations directly.

## 7. Limitations

The questions are automatic templates, with about 100 sources per language, so intervals are wide and do not support population-level claims. The corpus deliberately contains every target, and random background articles are easier distractors than same-topic articles. Each article is represented by a single truncated lead passage. Masking removes exact title strings only; it does not remove inflected forms, synonyms or other entity clues, so it underestimates title reliance. All text is Wikipedia, Uzbek is in Latin script only, and retrieval is monolingual. Several comparisons are reported without multiplicity adjustment. Generation quality is not assessed.

Earlier repository reports of 39% to 98% Uzbek recall after targeted corpus supplementation used different corpora and settings, selected supplementary sources with knowledge of the evaluation targets, and lack recoverable prediction provenance. They are not used in this paper.

## 8. Reproducibility and data availability

Frozen revision manifests, ranked predictions, passage hashes and metrics are public in the repository ([title-masking package](../title_masking/README.md); [pilot package](../reproducible_pilot/README.md)). Article text stays local and is re-fetched by revision ID; acquisition stops on any hash mismatch. `scripts/verify_title_masking.py` recomputes every Hit@k cell and paired interval from the predictions and checks that title-prefixed rankings reproduce the original pilot exactly; `scripts/analyze_title_masking_gaps.py --check` recomputes the between-language intervals. Both use only the Python standard library and run in continuous integration. The title-masking runner's SHA-256 is `{frozen['provenance']['script_sha256'][:16]}...`; full provenance is in each `metrics.json`.

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
{nl.join(pilot_rows)}
'''
    if save:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        PAPER.write_text(text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--no-pdf', action='store_true')
    parser.add_argument('--check', action='store_true', help='Confirm the committed Markdown matches the metrics (no writes)')
    args = parser.parse_args()
    frozen, extra, methods, cells, drops, gap = collect()
    if args.check:
        committed = PAPER.read_text()
        fresh = write(frozen, extra, methods, cells, drops, gap, passage_stats(), save=False)
        assert committed == fresh, 'Manuscript is out of date: run scripts/write_title_sensitivity_manuscript.py'
        print('Manuscript matches the committed metrics.')
        return
    write(frozen, extra, methods, cells, drops, gap, passage_stats())
    print(PAPER)
    if not args.no_pdf:
        width, height = figure(methods, cells)
        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        from build_pilot_paper import pdf
        caption = ('Figure 1. Hit@3 on original questions before (title prefix) and after title masking, complete corpus. '
                   'Labels give the masked value.')
        pdf(paper=PAPER, out=PDF, link_base='research_outputs/preprint_2026/', title=TITLE,
            footer_text='English-Uzbek title sensitivity | Draft for co-author review',
            figures=[('Masked fixed window', FIGURE.with_suffix('.png'), height / width, caption)])


if __name__ == '__main__':
    main()
