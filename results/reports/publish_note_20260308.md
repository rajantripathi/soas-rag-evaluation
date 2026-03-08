# Publish Note

- Dataset sources: MIRACL English raw shard, TyDi QA primary_task, and Uzbek Wikipedia.
- MIRACL workaround: bypassed the broken datasets script loader by downloading raw MIRACL files from Hugging Face Hub.
- Manual eval set: 40 questions total, split into 20 English and 20 Uzbek items.
- Comparison results: none baseline scored 0.2924 groundedness with 1.0 hallucination rate; vector retrieval scored 1.0 groundedness with 0.0 hallucination rate.
- Current caveats: the generator and scorer are deterministic heuristics, MIRACL coverage uses a limited English shard, and the manual benchmark is still small.
- Recommended next experiments: expand English coverage, add stronger generation and judging, and run the manual comparison through Slurm.
