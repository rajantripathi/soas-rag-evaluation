# Cross-Lingual Analysis Status Update
## 20 March 2026 - 15:10 UTC

## Current Status: RUNNING ✅

**Jobs:**
- LLM Judge (Job 3244850): Running on nid010364 (~1:30 remaining)
- Cross-Lingual Eval (Job 3245086): Running on nid010573 (just started)

## What We Added Today

### 1. Cross-Lingual Analysis Infrastructure 🔥 NEW

**Research Question:** How much does cultural/language mismatch hurt RAG performance?

**Experimental Design:**
1. Split corpus into language-specific corpora:
   - English-only: 80 documents
   - Uzbek-only: 141 documents

2. Cross-lingual experiments:
   - Uzbek questions → English corpus (culturally mismatched)
   - English questions → Uzbek corpus (culturally mismatched)

3. Compare to baseline (mixed corpus → respective language)

**Funding Value:** HIGH
- Demonstrates cultural bias in AI systems (AHRC priority)
- Quantifies "cultural imperialism" in multilingual AI
- SOAS strength: Central Asian expertise + cultural understanding

### 2. Files Created

**Data:**
- `data/processed/corpus_english_only.jsonl` (80 docs)
- `data/processed/corpus_uzbek_only.jsonl` (141 docs)

**Indexes:**
- `data/indexes/cross_lingual_english_only_index/`
- `data/indexes/cross_lingual_uzbek_only_index/`

**Scripts:**
- `scripts/create_cross_lingual_corpora.py` - Split corpus by language
- `scripts/build_cross_lingual_indexes.py` - Build language-specific indexes
- `scripts/run_cross_lingual_eval.py` - Run cross-lingual experiments

**Configs:**
- `configs/exp_cross_lingual_english_only.yaml`
- `configs/exp_cross_lingual_uzbek_only.yaml`

### 3. Expected Results

We will quantify:
- How much performance drops when using wrong language corpus
- Whether cultural knowledge transfer works across languages
- The "cultural bias penalty" in multilingual RAG systems

## Strategic Value

**For Paper (ACL Findings):**
- Novel cross-lingual evaluation dimension
- Quantifies cultural bias in RAG
- Strengthens "culturally grounded AI" contribution

**For Funding (AHRC/ESRC):**
- Demonstrates understanding of cultural bias
- Provides evidence for policy recommendations
- Shows SOAS expertise (Central Asia focus)

**Timeline:** ~1 hour for results

## Commit
Commit: eb86e2f

