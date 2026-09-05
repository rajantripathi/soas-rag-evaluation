# Limitations

## Evaluation Scope
- The 400-row public dataset is a pilot bilingual retrieval benchmark with documented template-generated questions, domain mismatches, and incomplete quality flags.
- The full retrieval-only dataset and a 30-row preview are public. Answer-bearing fields remain withheld pending source and licence clearance.
- Evidence is limited to this English-Uzbek evaluation setting and should not be generalised to all low-resource languages.

## Metrics
- The validated claims concern retrieval recall, not generated-answer quality.
- No human evaluation or LLM-as-judge evaluation has been completed.
- The generator is a first-sentence stub; heuristic answer-oriented metrics are not part of the headline claim.

## Corpus Coverage
- Uzbek coverage improved substantially after supplementation, but this does not imply full coverage of Uzbek institutional, legal, and historical knowledge.
- English history and institutions remained relatively weaker under the final setup, showing that source asymmetry still matters.

## Public Repository Constraints
- Full raw datasets, processed corpora, indexes, and HPC run directories are intentionally excluded from git.
- The public repository is therefore a lightweight benchmark and reporting bundle rather than a full archival snapshot of cluster storage.
- Isambard-AI is acknowledged as the historical compute environment for the reported experiments. The repository does not imply current or future access.
