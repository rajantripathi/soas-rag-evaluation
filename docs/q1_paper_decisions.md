# Q1 Paper Decisions — Control Document

**Last updated:** 2026-04-03
**Status:** Active — Phase A locked, all else blocked

---

## Final Research Question

"To what extent does knowledge source coverage, as opposed to retrieval model architecture, determine the retrieval performance ceiling for culturally grounded questions in low-resource languages?"

---

## Allowed Claims

1. **Corpus supplementation effect magnitude**: Corpus coverage produces ~8x larger effect (d=2.91) than model optimization (d=0.31) for culturally grounded retrieval
2. **Cultural specificity gradient**: Culturally specific queries systematically fail under standard retrieval setups, and this failure is remediated by targeted corpus supplementation
3. **Retrieval benchmark contribution**: The EN-UZ benchmark with cultural specificity annotations is a novel evaluation instrument
4. **Framework contribution**: CRG and CSS metrics operationalize cultural specificity as a measurable retrieval confound

## Disallowed Claims (scope lock)

- Any claim about generation quality
- Any claim about RAG end-to-end performance
- Any claim about generalization beyond EN-UZ (unless third language is added)
- Any claim that model choice "doesn't matter" (it matters, just less than coverage)
- Any claim about cross-lingual transfer (not tested)

---

## Experiment Priorities

### Phase A (current — locked)
| ID | Experiment | Status | GPU Hours |
|----|-----------|--------|-----------|
| E1 | Clean English supplementation | BLOCKED (need leakage details) | 2h |
| E2 | BGE-M3 baseline | Script written | 4h |
| E3 | mDPR baseline | Not started | 4h |
| E4 | BM25+RM3 | Script written | 1h |
| E5 | Extended metrics (nDCG, MRR, MAP) | Script written | 0h |
| E6 | Cultural specificity (CRG, CSS) | Script written | 0h |

### Phase B (locked — do not start)
- E7: Chunk size ablation
- E8: Corpus scaling ablation
- E9: Multiple seeds
- E10: Per-domain analysis

### Phase C (locked — do not start)
- E11: Cross-lingual retrieval
- E12: ColBERTv2 baseline
- E13: Third language (Kazakh)

---

## Optional Extensions (require explicit approval)

- Human evaluation with native speakers
- Kazakh benchmark construction
- Cross-lingual retrieval experiments
- Paper draft writing

---

## Known Reviewer Risks

1. **"Only 2 languages"** — Mitigate: frame as rigorous case study with generalizable framework
2. **"Adding docs improves recall — obvious"** — Mitigate: magnitude (8x) is the contribution, not direction
3. **"English supplementation was retracted"** — Mitigate: re-run with clean data, document transparently
4. **"Only 400 items"** — Mitigate: post-hoc power > 0.99 for d=2.91
5. **"Why Uzbek?"** — Mitigate: low-resource, typologically distinct, SOAS expertise, 200M+ Turkic speakers
6. **"No human evaluation"** — Mitigate: acknowledge in Limitations; plan for future work

---

## Target Venue

**TACL** (Transactions of the Association for Computational Linguistics)
- Q1, rolling submissions, 8,000-10,000 words
- Archival with ACL/EMNLP presentation

---

## Git Rules

- Branch: `paper/q1-retrieval`
- Main tagged: `v1.0-workshop`
- No modifications to existing files without explicit approval
- All outputs to `results/q1_experiments/`
