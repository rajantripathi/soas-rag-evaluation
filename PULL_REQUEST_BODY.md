# Pull Request: Retraction and correction

## Summary

This PR contains important retractions and corrections to Phase 3 results, removing invalid English supplement claims while preserving validated Uzbek results.

## Changes

### Retractions
- **English supplement v1 RETRACTED** due to data leakage (synthetic documents contained gold_answer text)
- Files renamed with `_INVALID` suffix (not deleted for transparency)
- Removed all claims of 100% English recall
- Invalid metrics clearly marked as retracted

### Validated Results (Preserved)
- ✅ **Uzbek supplementation:** 39% to 98% (+59%, p < 0.001, d = 2.91)
- ✅ All baseline comparisons remain valid
- ✅ Statistical analysis remains valid (bootstrap CIs, McNemar's test, effect sizes)
- ✅ Effect size: Corpus 7.8x more effective than model optimisation

### New Analysis
- **English supplement v2 attempted:** MIRACL corpus lacks 0/37 required English Wikipedia articles
- **Gold answer audit:** 38 items (9.5%) flagged for Wikipedia navigation artefacts
- **Honest reporting:** 37% English gap documented as valid finding

## Files Modified
- `PHASE3_COMPLETION_SUMMARY.md` - Added retraction notice
- `scripts/build_english_supplement_v2.py` - New script for transparent methodology
- `RETRACTION_AND_CORRECTION_COMPLETE.md` - Completion summary
- `results/gold_answer_quality_flags.json` - Quality audit results

## Commits
1. Retract invalid English supplement (9ba3ec7)
2. Add gold answer quality audit (6d4b5a0)
3. Add completion summary (b319582)

## Impact
- **Core contribution remains strong:** Validated Uzbek results demonstrate corpus coverage dominates model choice
- **Retraction strengthens credibility:** Transparent about data leakage issue
- **English gap as finding:** Differential data availability IS a research contribution

## Publication Ready
✅ Workshop paper (Uzbek results valid)
✅ Policy brief (uses only Uzbek numbers)
✅ Statistical rigour maintained

See `RETRACTION_AND_CORRECTION_COMPLETE.md` for full details.
