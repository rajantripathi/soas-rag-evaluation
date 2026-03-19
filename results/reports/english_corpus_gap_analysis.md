# English Corpus Gap Analysis

## Overview

This analysis identifies missing English source documents in the current corpus, following the same methodology used for Uzbek gap analysis. The goal is to identify which English domains need supplementation.

**Total English items:** 200
**Items with source in corpus:** 126 (63.0%)
**Items with missing source:** 74 (37.0%)

## Coverage by Domain

| Domain | Total | Present | Missing | Coverage % |
| --- | ---: | ---: | ---: | ---: |
| Governance | 50 | 40 | 10 | 80.0% |
| History | 50 | 20 | 30 | 40.0% |
| Institutions | 50 | 16 | 34 | 32.0% |
| Culture | 50 | 50 | 0 | 100.0% |

## Missing Source Documents by Domain

### Governance

**Missing count:** 10 of 50 (20.0%)

- **en_65** (`None`): What place, state, or political entity is Marxism?...
- **en_67** (`None`): What place, state, or political entity is Guerrilla warfare?...
- **en_70** (`None`): What place, state, or political entity is Pacific Gas & Electric Co. v. State En...
- **en_71** (`None`): What place, state, or political entity is Municipalities of Belgium?...
- **en_75** (`None`): What place, state, or political entity is The Culture?...
- **en_governance_v4_20** (`None`): How is Marxism described as a political or territorial entity?...
- **en_governance_v4_21** (`None`): What kind of governed place or polity is Guerrilla warfare?...
- **en_governance_v4_22** (`None`): How is Pacific Gas & Electric Co. v. State Energy Resources Conservation & Devel...
- **en_governance_v4_23** (`None`): What kind of governed place or polity is Municipalities of Belgium?...
- **en_governance_v4_24** (`None`): How is The Culture described as a political or territorial entity?...

### History

**Missing count:** 30 of 50 (60.0%)

- **en_63** (`None`): What is Súper Sábado Sensacional in historical context?...
- **en_66** (`None`): What is Taoism in historical context?...
- **en_68** (`None`): What is Emperor Xian of Han in historical context?...
- **en_69** (`None`): What is Monte Carlo in historical context?...
- **en_72** (`None`): What is Emperor Gaozu of Tang in historical context?...
- **en_73** (`None`): What is History of the World Wide Web in historical context?...
- **en_74** (`None`): What is History of Freemasonry in historical context?...
- **en_76** (`None`): What is World War I casualties in historical context?...
- **en_77** (`None`): What is Ram Pickup in historical context?...
- **en_78** (`None`): What is Tin sources and trade in ancient times in historical context?...
- ... and 20 more

### Institutions

**Missing count:** 34 of 50 (68.0%)

- **en_64** (`None`): What institution, organization, or formal body is Really Achieving Your Childhoo...
- **en_84** (`None`): What institution, organization, or formal body is Llantrisant and Taff Vale Junc...
- **en_85** (`None`): What institution, organization, or formal body is Apprenticeship?...
- **en_86** (`None`): What institution, organization, or formal body is Maryland Terrapins football?...
- **en_87** (`None`): What institution, organization, or formal body is Twelfth grade?...
- **en_88** (`None`): What institution, organization, or formal body is Global Marshall Plan Initiativ...
- **en_89** (`None`): What institution, organization, or formal body is Media conglomerate?...
- **en_90** (`None`): What institution, organization, or formal body is Discovery Channel?...
- **en_91** (`None`): What institution, organization, or formal body is Johnny Cueto?...
- **en_92** (`None`): What institution, organization, or formal body is World Intellectual Property Or...
- ... and 24 more

## Key Findings

1. **Weakest domain:** Institutions with only 32.0% coverage
2. **Domains needing attention:** History, institutions (all below 70% coverage)
3. **Total supplementation needed:** 74 English documents

## Recommendations

Based on this analysis, the following supplementation strategy is recommended:

### Governance

- **Priority:** Medium
- **Documents needed:** 10
- **Source strategy:** Search MIRACL and TyDi QA English corpora for matching Wikipedia titles

### History

- **Priority:** High
- **Documents needed:** 30
- **Source strategy:** Search MIRACL and TyDi QA English corpora for matching Wikipedia titles

### Institutions

- **Priority:** High
- **Documents needed:** 34
- **Source strategy:** Search MIRACL and TyDi QA English corpora for matching Wikipedia titles

## Next Steps

1. Extract missing English documents from existing raw datasets (MIRACL, TyDi QA)
2. For documents not found in raw datasets, flag for manual curation
3. Build English supplement corpus and merge with existing corpus
4. Re-run evaluation to measure English recall improvement

