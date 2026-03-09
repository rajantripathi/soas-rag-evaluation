# Dataset Card: manual_eval_v5

## Overview

manual_eval_v5 is a deterministic enrichment of the 400-item bilingual retrieval benchmark for culturally grounded question answering in English and Uzbek. It preserves every v4 benchmark item exactly while adding human-readable source titles, a coarse difficulty heuristic, and auditable quality flags derived from the Stage 1 dataset audit.

## Languages

- English
- Uzbek

## Domains

- governance
- history
- institutions
- culture

## Dataset Schema

| field | type | description |
| --- | --- | --- |
| id | str | Stable item identifier. |
| language | str | Benchmark language (`en` or `uz`). |
| domain | str | Benchmark domain (`governance`, `history`, `institutions`, `culture`). |
| question | str | Evaluation question text. |
| gold_answer | str | Reference answer text used for audit and downstream evaluation. |
| cultural_specificity | str | Manual cultural-specificity label retained from v4. |
| answerable | bool | Whether the item is considered answerable. |
| source_doc_ids | list[str] | Source document identifiers retained from v4. |
| source_title | str | null | Human-readable title resolved from the corpus using `source_doc_ids[0]`. |
| difficulty | str | Deterministic heuristic difficulty label: `easy`, `medium`, or `hard`. |
| quality_flag | str | null | Audit-derived label for known benchmark issues. |

## Difficulty Levels

- `easy`: non-history items with gold answers of 20 words or fewer.
- `medium`: items that are neither `easy` nor `hard` under the deterministic heuristic.
- `hard`: all history items plus reasoning-oriented question forms.

| difficulty | count |
| --- | --- |
| easy | 152 |
| medium | 107 |
| hard | 141 |

## Quality Flags

Quality flags preserve known audit findings without mutating the benchmark content. Allowed values are `domain_misclassification`, `question_quality`, `gold_answer_quality`, and `null`.

| quality_flag | count |
| --- | --- |
| domain_misclassification | 12 |
| question_quality | 4 |
| gold_answer_quality | 0 |
| clean | 384 |

## Source Title Resolution

Resolved titles: 326 / 400. Null values indicate that `source_doc_ids[0]` could not be matched to a titled row in the supplied corpus file.

| language | resolved | total |
| --- | --- | --- |
| en | 126 | 200 |
| uz | 200 | 200 |

## Changelog from v4

- Added `source_title` resolved from the corpus.
- Added deterministic `difficulty` labels.
- Added audit-derived `quality_flag` labels.
- Preserved all original v4 fields and values exactly.

## Fields Excluded from v5

- `evidence_text`: requires corpus-backed extraction and human verification; deferred to v6.
- `source_url`: requires verified URL resolution for each source; deferred to v6.
- `pair_id`: the English and Uzbek halves are not parallel and do not support a meaningful 1:1 pairing in v5.

## Known Limitations

- The benchmark remains manually curated and moderate in size.
- Quality-flagged items are still present; the flag is documentation, not removal.
- The difficulty heuristic is coarse and should not be treated as a human judgment label.
- Source title coverage depends on the supplied corpus and may be incomplete.
- Retrieval and answer-quality evaluation remain separable concerns when stub generation is used.

## Example Entries

### en_00

```json
{
  "id": "en_00",
  "language": "en",
  "domain": "culture",
  "question": "What is Art Deco?",
  "gold_answer": "Art Deco, sometimes referred to as Deco, is a style of visual arts, architecture and design that first appeared in France just before World War I",
  "source_doc_ids": [
    "Art Deco"
  ],
  "answerable": true,
  "cultural_specificity": "high",
  "source_title": "Art Deco",
  "difficulty": "medium",
  "quality_flag": null
}
```

### en_03

```json
{
  "id": "en_03",
  "language": "en",
  "domain": "history",
  "question": "What is the Château de Brest?",
  "gold_answer": "Coordinates: \n\nThe Château de Brest is a castle in Brest, Finistère, France",
  "source_doc_ids": [
    "Château de Brest"
  ],
  "answerable": true,
  "cultural_specificity": "high",
  "source_title": "Château de Brest",
  "difficulty": "hard",
  "quality_flag": null
}
```

### uz_00

```json
{
  "id": "uz_00",
  "language": "uz",
  "domain": "governance",
  "question": "Oʻzbekiston nima?",
  "gold_answer": "Oʻzbekiston (rasman: Oʻzbekiston Respublikasi,) — Markaziy Osiyoning markaziy qismida joylashgan mamlakat",
  "source_doc_ids": [
    "793"
  ],
  "answerable": true,
  "cultural_specificity": "high",
  "source_title": "Oʻzbekiston",
  "difficulty": "easy",
  "quality_flag": null
}
```

### uz_01

```json
{
  "id": "uz_01",
  "language": "uz",
  "domain": "history",
  "question": "Xorazm nima?",
  "gold_answer": "Xorazm () – Amudaryo sohillarida markazga ega Oʻrta Osiyo qadimiy mintaqasi – qadimiy davlat va rivojlangan irrigatsiyali dehqonchilik, hunarmandlik va savdo mintaqasi",
  "source_doc_ids": [
    "1031"
  ],
  "answerable": true,
  "cultural_specificity": "high",
  "source_title": "Xorazm",
  "difficulty": "hard",
  "quality_flag": null
}
```

