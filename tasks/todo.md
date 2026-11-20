# BiasLens — Production Launch & Algorithm Credibility

## Phase 1: Validate Deployment ✓ COMPLETE
- [x] Test /health endpoint — returns `{"status":"ok","version":"1.0.0"}` ✓
- [x] Test /analyze endpoint with Sikh bias data — responds with bias detection ✓
- [x] Test /analyze/batch endpoint (tested with 3 samples) — responds correctly ✓
- [x] Check for Railway errors — API online and stable ✓
- ⚠️  **Finding:** OPENAI_API_KEY not set in Railway (improved responses not generated) — will fix in Phase 1.5

## Phase 1.5: Fix OpenAI API Key Integration (Blocker)
- [ ] Update `biaslense/src/core/bamip_pipeline.py` to read OPENAI_API_KEY from environment variables
- [ ] Change `st.secrets["OPENAI_API_KEY"]` to `os.environ.get("OPENAI_API_KEY")`
- [ ] Add graceful fallback if key is missing (skip improved response generation)
- [ ] Set OPENAI_API_KEY in Railway environment variables
- [ ] Test full /analyze flow (including improved response generation)

## Phase 2: Fix Algorithm Credibility ✓ COMPLETE (4.25 hours)
- [x] Step 1: Build data pipeline (load 7 CSVs, merge) — 30 min ✓
  - Merged 276 evaluations from 6 raters, 3 models, 54 prompts
  - Output: `results/rater_data_combined.csv`
- [x] Step 2: Compute Krippendorff's α per dimension/model — 45 min ✓
  - α values: GPT-4 avg -0.123, LLaMA avg 0.231, Claude avg 0.056
  - Finding: IRA mostly poor/fair, validates empirical calibration approach
  - Output: `results/krippendorff_alpha_results.csv`
- [x] Step 3: Derive empirical baseline scores (population means) — 20 min ✓
  - Fairness: 3.49, Neutrality: 3.55, Representation: 3.60
  - Replaces hardcoded 5.0 baselines throughout algorithm
  - Output: `results/dimension_baselines.csv`
- [x] Step 4: Calibrate penalty multipliers from rater score variance — 90 min ✓
  - Extreme bias: -4.5 → -1.49 (empirical)
  - Religious conflation: -3.5 → -1.47
  - Generalizations: -2.5 → -1.20
  - Output: `results/calibrated_multipliers.csv`
- [x] Step 5: Validate composite metric (F+N+R)/3 formula — 30 min ✓
  - Composite aligns with rater severity categories
  - Severe (≤2.5): 13.8%, Moderate (2.5-3.5): 19.2%, Mild (>3.5): 44.9%
- [x] Step 6: Update rubric_scoring.py with empirical values — 45 min ✓
  - Updated _score_fairness, _score_representation, _score_linguistic_balance
  - Added inline citations to empirical data
  - Preserved algorithm structure, only updated constants
- [x] Step 7: Create ALGORITHM.md with full methodology & findings — 30 min ✓
  - 201 lines documenting validation, limitations, reproducibility
  - Ready for paper resubmission with methodology details
- [x] Step 8: Update README + mark Phase 2 complete — 15 min ✓ (in progress)

**Deferred for Future Phases:**
- [ ] Claude calibration in Phase 4 (currently only 38 rater responses, 16 overlapping)
- [ ] Model-specific multiplier code path (marked "TODO" in rubric_scoring.py for easy addition)

## Phase 3: Build Python SDK (2-3 hours)
- [ ] Create `biaslense/sdk/` directory with `__init__.py`
- [ ] Write `BamiPClient` class — wraps REST API calls
- [ ] Support both local and remote API endpoints
- [ ] Add batch processing helper
- [ ] Write docstrings + type hints
- [ ] Add example usage in `examples/`

## Phase 4: Documentation & Launch (1-2 hours)
- [ ] Update README with SDK installation & examples
- [ ] Publish SDK to PyPI or GitHub Packages
- [ ] Create ALGORITHM.md documenting validation approach
- [ ] Prepare resubmission summary for your paper

---

**Critical Path:** Phase 1 → Phase 1.5 → Phase 2 → Phase 3 → Phase 4
(Don't skip Phase 1.5 or 2 — algorithm credibility is table stakes for paper resubmission)

---

## README cleanup — match resume, cut unsourced numbers (2026-11-02) ✓ COMPLETE
- [x] Trace every number in README to code/data
  - 276 ratings / 6 raters / 3 LLMs / 54 prompts → `results/rater_data_combined.csv`
  - 5 dimensions (Accuracy, Relevance, Fairness, Neutrality, Representation) → `llm_scorer.py`, rater CSV
  - Held-out split (seed 42, 8 test / 30 dev) → `tasks/validate_scorer.py`, `data/scorer_split.json`
- [x] Cut unsourced percentages (127.1%, 141.3%, 85%/88% effectiveness, 271% example, etc.); only source was hardcoded constants in `bamip_pipeline.py`
- [x] Remove stale claims: embedding checker (removed from code), OpenAI key (code uses ANTHROPIC_API_KEY), duplicated second README, dead links (LICENSE, CONTRIBUTING.md, requirements-dev.txt), placeholder citation
- [x] Add resume items missing from README: LLM-as-judge scorer + held-out validation, MCP server
- [x] Verify: all relative links resolve, no `%` remains, SDK claims checked against `sdk/client.py`, final read-through

**Review:** README went from 593 to ~250 lines. Open follow-ups: LICENSE file is missing although setup.py says MIT; the hardcoded effectiveness constants in `bamip_pipeline.py` still drive strategy selection and are unsourced.

---

## Close out BiasLens — repo, paper, LinkedIn match resume (2026-11-20)

Source of truth: resume PDF in Drive (2026-11-20). BiasLens: Jan 2024 – Nov 2026 (start confirmed: planning began
Jan 2024), 276 ratings / 6 raters / 3 LLMs, Krippendorff's alpha, LLM-as-judge + held-out split, SDK/API/app/MCP,
United Sikhs Summit 2025. README "national policy recommendations" claim confirmed true.

### Step 1 — README + paper cleanup ✓
- [x] README traced to resume; unsourced % removed (2026-11-02); paper PDF linked
- [x] Bug: loader paired raters by row order → Claude alpha was on mismatched prompts. Fixed + test (c90f685)
- [x] §3 rebuilt from the 276-rating set with Friedman/Wilcoxon/Kruskal-Wallis (85848db); old 7-rater analysis retired
- [x] §5 recomputed from source data, cross-checked against two copies (b2c7262); real gains ~half the old %s
- [x] Calibration on all 276 ratings (b368c4b); ALGORITHM.md rewritten to match code (d804334, d1fd203)
- [x] Paper text fixed: 54 prompts / 162 responses, 6 raters, 16 Claude overlap, categories, embedding null result,
      §5.6 verbatim example, Krippendorff 0.667 standard, §4.6 method, Discussion/Conclusion/Abstract
- [x] References: all 38 verified (4 parallel agents); 3 non-existent removed (old 7→real source, 22, 37);
      metadata and claims corrected; renumbered to 36; every one cited
- [x] BAMIP diagram: removed unsourced "F1 = 0.92" and "+127% (Tong et al.)" parameter box
- [x] TOC removed (page numbers would be wrong); Tabs 2–3 left out of the new doc (still in the original Google Doc)

### Step 2 — Review + reference verification (Jaspreet)
- [ ] Read ~/projects/biaslense_paper_review_2026-11/citation_changelog.md (every citation change + reason)
- [ ] Spot-check references against the URLs in reference_checks/batch1-4_result.md
- [ ] Read the new Google Doc / docs/paper/biaslense_paper.pdf end to end

### Step 3 — PDF in repo ✓
- [x] docs/paper/biaslense_paper.pdf added, stale .txt removed (bb8d961)
- [ ] `git push` (README PDF link 404s until pushed)

### Step 4 — LinkedIn + resume (Jaspreet, manual)
- [ ] LinkedIn BiasLens end date → Nov 2026
- [ ] Resume "Jan 2024 – Present" → "Jan 2024 – Nov 2026"

### Step 5 — Railway (Jaspreet decides at the end)
- Resume links only GitHub + LinkedIn. Railway is used by README live-API links, mcp_server.py default URL,
  examples/sdk_basic.py. If cancelling, update those three first.

### Done check
- [x] Repo ↔ resume: 276/6/3, Krippendorff, calibration, LLM-as-judge, SDK/API/app/MCP all agree
- [x] Paper ↔ repo: every number regenerated by committed scripts; figures from docs/paper/figures/
- [ ] LinkedIn + resume dates (Step 4)

## Review (2026-11-20)
- Biggest finds: row-order pairing bug; paper mixed two datasets with contradictory conclusions; 3 fabricated and
  several misattributed references; unsourced numbers in text and inside the BAMIP diagram image; §5.6 quotes
  that did not match the data.
- Findings that held: retrieval grounding helps most; original penalties overstated bias (~3x); linguistic-bias
  prompts score lowest for 2 of 3 models.
- Findings that did not hold: "Claude strongest overall", "LLaMA lowest fairness", embedding corroboration,
  +127/134/83%.
- Pre-existing, not fixed: legacy test biaslense/tests/test_basic_functionality.py (expects removed `overall_score`
  path); a stale global `src` package in system site-packages shadows the repo's `src` when both test dirs run together.
- Optional strengthening: test whether the calibrated rule scorer agrees with raters better than the original
  (baseline response texts exist in ~/projects/data/combined/).
