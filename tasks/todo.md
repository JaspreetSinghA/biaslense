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

## Phase 2: Fix Algorithm Credibility (4.25 hours) — IN PROGRESS
- [ ] Step 1: Build data pipeline (load 7 CSVs, merge) — 30 min
- [ ] Step 2: Compute Krippendorff's α per dimension/model (GPT-4 + LLaMA focus) — 45 min
- [ ] Step 3: Derive empirical baseline scores (population means) — 20 min
- [ ] Step 4: Calibrate penalty multipliers from rater score variance — 90 min ⭐
- [ ] Step 5: Validate composite metric (F+N+R)/3 formula — 30 min
- [ ] Step 6: Update rubric_scoring.py with empirical values (model-specific multipliers + fallback) — 45 min
- [ ] Step 7: Create ALGORITHM.md with full methodology & findings — 30 min
- [ ] Step 8: Update README + mark Phase 2 complete — 15 min
- [ ] **Deferred:** Add Claude calibration in Phase 4 (currently only 16 overlapping prompts)
- [ ] **Deferred:** Model-specific multipliers with commented-out unified fallback (for easy downgrade if too complex)

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
