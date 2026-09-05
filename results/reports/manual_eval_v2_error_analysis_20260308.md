# Manual Eval v2 Error Analysis

This public report retains retrieval-side identifiers, questions, and recall outcomes. Answer text, retrieved source excerpts, and generated text have been removed pending source and licence clearance.

## Vector Retrieval Failures
- en_83 | en | history | recall=0.0
  question: What is Geological history of oxygen in historical context?
  gold_doc_ids: ['Geological history of oxygen']
  top_doc_ids: ['History of paleontology', 'Atmosphere of Earth', 'Dialectic']
- en_61 | en | governance | recall=0.0
  question: What place, state, or political entity is List of battleships of the United States Navy?
  gold_doc_ids: ['List of battleships of the United States Navy']
  top_doc_ids: ['List of United States cities by population density', 'Guanajuato', 'Permanent members of the United Nations Security Council']
- uz_93 | uz | institutions | recall=0.0
  question: Institut qanday muassasa yoki tashkilot?
  gold_doc_ids: ['14516']
  top_doc_ids: ['1675', '1790', '1570']
- uz_42 | uz | institutions | recall=0.0
  question: Oʻzbekistondagi universitetlar qanday muassasa yoki tashkilot?
  gold_doc_ids: ['1887']
  top_doc_ids: ['1790', '1570', '1636']
- uz_58 | uz | culture | recall=0.0
  question: Microsoft Windows nima?
  gold_doc_ids: ['2198']
  top_doc_ids: ['1798', 'Clannad (visual novel)', '1634']
- uz_71 | uz | institutions | recall=0.0
  question: Munavvarqori Abdurashidxon oʻgʻli qanday muassasa yoki tashkilot?
  gold_doc_ids: ['2826']
  top_doc_ids: ['1570', '1790', '1798']
- uz_78 | uz | institutions | recall=0.0
  question: Coldplay qanday muassasa yoki tashkilot?
  gold_doc_ids: ['4080']
  top_doc_ids: ['1790', '1570', '1798']
- uz_80 | uz | institutions | recall=0.0
  question: Oʻzbekiston milliy teleradiokompaniyasi qanday muassasa yoki tashkilot?
  gold_doc_ids: ['5309']
  top_doc_ids: ['1570', '1700', '1790']
- uz_82 | uz | institutions | recall=0.0
  question: 1477 qanday muassasa yoki tashkilot?
  gold_doc_ids: ['8090']
  top_doc_ids: ['1790', '1570', '1798']
- uz_83 | uz | institutions | recall=0.0
  question: 1917 qanday muassasa yoki tashkilot?
  gold_doc_ids: ['8855']
  top_doc_ids: ['1790', '1570', '1798']
- uz_89 | uz | institutions | recall=0.0
  question: Gmail qanday muassasa yoki tashkilot?
  gold_doc_ids: ['13959']
  top_doc_ids: ['1790', '1570', '1798']
- uz_92 | uz | institutions | recall=0.0
  question: Universitet qanday muassasa yoki tashkilot?
  gold_doc_ids: ['14515']
  top_doc_ids: ['1790', '1570', '1798']

## Flagged Answer-Overlap Cases (Content Withheld)
- en_00 | en | culture
  question: What is Art Deco?
  recall: 1.0
- en_01 | en | culture
  question: What are French-based creole languages associated with?
  recall: 1.0
- en_05 | en | culture
  question: Why is Mecca important?
  recall: 1.0
- en_11 | en | culture
  question: How important is football in Spain?
  recall: 1.0
- en_14 | en | culture
  question: What is Clannad?
  recall: 1.0
- en_15 | en | culture
  question: What is Still Game?
  recall: 1.0
- en_17 | en | culture
  question: What is the Sporthotel Pontresina?
  recall: 1.0
- en_18 | en | culture
  question: What does the name bluebonnet refer to?
  recall: 1.0
- en_21 | en | culture
  question: What is Biodegradable plastic?
  recall: 1.0
- en_32 | en | culture
  question: What is Guitar Hero Live?
  recall: 1.0
- en_44 | en | culture
  question: What is Camelford water pollution incident?
  recall: 1.0
- en_50 | en | culture
  question: What is Kakapo?
  recall: 1.0

## Short Interpretation
- Most vector failures are missed exact-source retrievals rather than total answer collapse; the retrieved text is often related but not the labeled source passage.
- Grounded-prompt errors are usually formatting or sentence-boundary mismatches because the stub generator truncates to the first retrieved sentence.
- Uzbek misses are concentrated where lexical variants or document-level chunks make exact source matching harder.
