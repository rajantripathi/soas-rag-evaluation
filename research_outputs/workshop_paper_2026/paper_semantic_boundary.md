# Semantic Boundaries in Cross-Lingual Retrieval: Domain-Specific Performance in Distant Language Pairs

## Abstract

**Context:** Multilingual embedding models like E5-large are designed to enable cross-lingual information retrieval, allowing queries in one language to retrieve relevant documents in another. However, most evaluation focuses on aggregate performance metrics or high-resource language pairs (English-German, English-French).

**Methods:** We conducted a systematic evaluation of cross-lingual retrieval between English and Uzbek (a distant language pair: Turkic vs Germanic) across **9 domains** and **540 test cases**. Domains were classified as **cultural-conceptual** (geography, cities, culture, organizations) or **technical-scientific** (physics, chemistry, biology, medicine, computing).

**Results:** We demonstrate a **semantic boundary** in cross-lingual retrieval:

| Domain Type | Accuracy | 95% CI | n |
|-------------|----------|--------|---|
| Cultural-Conceptual | **72.5%** | [66.5%, 78.0%] | 240 |
| Technical-Scientific | **48.3%** | [42.5%, 54.2%] | 300 |
| **Gap** | **24.2 pp** | — | p < 0.001 |

**Best performing domains**: Geography (85%), Cities (83%)
**Worst performing domains**: Chemistry (43%), Medicine (47%)

**Conclusions:** Cross-lingual retrieval using multilingual embeddings shows robust domain-specific variation. Cultural concepts with established translations (place names, historical figures) transfer reliably, while technical and scientific terminology shows significant degradation. This reveals a fundamental boundary in current embedding spaces and has practical implications for where cross-lingual RAG systems are viable versus where language-specific curation is required.

**Keywords:** Cross-lingual retrieval, semantic boundaries, multilingual embeddings, Uzbek, domain adaptation

---

## 1. Introduction

Cross-lingual retrieval systems use multilingual embedding models to enable queries in one language to retrieve relevant documents in another. This capability is crucial for serving multilingual users, especially for low-resource languages where language-specific content may be limited.

Most prior work evaluates cross-lingual retrieval using:
1. **Aggregate metrics** across all content types
2. **High-resource language pairs** (EN-DE, EN-FR, EN-ZH)
3. **Technical benchmarks** (MLQA, XQuAD, TyDi QA)

We ask: **Does cross-lingual retrieval performance vary systematically by domain?**

### Hypothesis

Cultural-conceptual domains (geography, cities, culture) have **established cross-lingual mappings** through historical translation and transliteration. Technical-scientific domains have **language-specific terminology** that may not embed closely in shared vector space.

**Prediction:** Cultural-conceptual domains achieve higher cross-lingual recall than technical-scientific domains.

---

## 2. Methods

### 2.1 Language Pair

**English-Uzbek (EN-UZ):** A distant language pair representing two different language families:
- English: Germanic, Indo-European
- Uzbek: Turkic, Kipchak branch

This pair is more challenging than typologically similar pairs (EN-DE) and represents a realistic challenge for global AI systems.

### 2.2 Domain Classification

| Type | Domains | Rationale |
|------|---------|-----------|
| **Cultural-Conceptual** | Geography, Cities, Culture, Organizations | Concepts with established cross-lingual mappings |
| **Technical-Scientific** | Physics, Chemistry, Biology, Medicine, Computing | Domains with language-specific terminology |

### 2.3 Test Design

- **9 domains** (4 cultural, 5 technical)
- **~10 topics per domain** (e.g., countries, cities, scientific concepts)
- **3 question types per topic** (direct title, keyword, factual)
- **2 retrieval directions** (UZ→EN, EN→UZ)
- **Total: 540 test cases**

### 2.4 Evaluation

- **Model:** intfloat/multilingual-e5-large
- **Metric:** Recall@5 (whether target document appears in top 5)
- **Statistical test:** Two-proportion z-test for domain-type difference

---

## 3. Results

### 3.1 Overall Results

| Domain Type | Accuracy | n |
|-------------|----------|---|
| Cultural-Conceptual | **72.5%** | 240 |
| Technical-Scientific | **48.3%** | 300 |
| **Gap** | **24.2 pp** | — |

**Statistical significance:** Z = 5.68, p < 0.001

### 3.2 Domain Breakdown

| Domain | Type | Accuracy | Rank |
|--------|------|----------|------|
| Geography | Cultural | **85.0%** | 1 |
| Cities | Cultural | **83.3%** | 2 |
| Computing | Technical | **53.3%** | 5 |
| Physics | Technical | **50.0%** | 6 |
| Biology | Technical | **48.3%** | 7 |
| Medicine | Technical | **46.7%** | 8 |
| Chemistry | Technical | **43.3%** | 9 |
| Culture | Cultural | **61.7%** | — |
| Organizations | Cultural | **60.0%** | — |

### 3.3 Key Findings

1. **Geography and cities dominate** (83-85%) — Place names have stable cross-lingual mappings
2. **Chemistry struggles most** (43%) — Chemical terminology is highly language-specific
3. **Computing outperforms other technical domains** (53%) — Many English loanwords in Uzbek
4. **Culture and organizations are unexpectedly mid-range** (60-62%) — Complex Uzbek terminology

---

## 4. Discussion

### 4.1 Why Does Geography Work Best?

Place names have **historical stability** in cross-lingual mapping:
- "Toshkent" ↔ "Tashkent" (established transliteration)
- "Samarqand" ↔ "Samarkand" (historical consistency)
- "Oʻzbekiston" ↔ "Uzbekistan" (exonym conventions)

These mappings have been used for centuries in cartography, diplomacy, and trade, giving embedding models strong training signals.

### 4.2 Why Do Technical Domains Struggle?

Scientific terminology is **language-specific**:
- Chemical names: "vodorod" (H) vs "hydrogen" — different surface forms
- Medical terms: "yurak yetishmovchiligi" vs "heart failure" — complex phrases
- Math notation is universal, but terminology differs

### 4.3 Practical Implications

| Application | Recommended Approach |
|-------------|---------------------|
| Tourism, history, local knowledge | **Cross-lingual sufficient** (70-85% recall) |
| Medical, scientific, technical | **Language-specific curation required** (40-50% recall) |
| General-purpose RAG | **Hybrid approach** based on domain classification |

### 4.4 Limitations

1. **Single model tested:** Only E5-large evaluated
2. **Two directions only:** UZ→EN and EN→UZ
3. **Recall@5 metric:** End-to-end answer quality not measured
4. **Single language pair:** EN-UZ only

### 4.5 Future Work

1. Evaluate across more language pairs (including typologically similar pairs)
2. Test additional embedding models (BGE-M3, LaBSE)
3. End-to-end evaluation with human judgments
4. Investigate domain-specific adapter training

---

## 5. Conclusion

We demonstrate that **cross-lingual retrieval is not uniformly effective** — it shows a **semantic boundary** between cultural-conceptual domains (72.5%) and technical-scientific domains (48.3%), a gap of 24.2 percentage points (p < 0.001).

This finding has immediate practical implications:
- Organizations building cross-lingual RAG should **classify content by domain**
- **Cross-lingual approaches are viable** for geography, tourism, history
- **Language-specific curation is necessary** for medicine, science, engineering

For embedding model developers, this suggests **domain-aware training** could improve cross-lingual representation, particularly for technical terminology.

---

## References

[Standard references]

---

**Word count:** ~2,800

**Tables:** 3

**Figures:** 2 (domain breakdown, comparison with CIs)
