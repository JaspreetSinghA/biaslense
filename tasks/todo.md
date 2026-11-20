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

Source of truth: resume PDF in Drive (uploaded 2026-11-20). BiasLens line: "Jan 2024 – Present",
276 ratings / 6 raters / 3 LLMs, Krippendorff's alpha, LLM-as-judge + held-out split, SDK/API/app/MCP,
United Sikhs Summit 2025.

Constraint: the paper Google Doc is read-only through Claude's Drive connector.

DECISIONS (2026-11-20):
- Original Google Doc is NOT edited; it stays as the archive. Claude builds a corrected paper as a
  NEW Google Doc (Drive) + PDF (docs/paper/), one dataset throughout (276 ratings / 6 raters / 54 prompts).
- §3 rebuilt from results/rater_data_combined.csv (option B).
- References: Claude finds each source + evidence table with links; Jaspreet confirms each link.
- End date: Nov 2026 (last commits 2026-11-03). Resume "Jan 2024 – Present" → "Jan 2024 – Nov 2026"; LinkedIn same.
  Open: earliest artifact found is Jul 2025; Jaspreet to confirm Jan 2024 start.
- Railway: decide later (not blocking).

### Step 1 — README + paper cleanup (Claude prepares)
- [x] README already traced to resume + unsourced % removed (2026-11-02 section above)
- [ ] README: cut or source "invited to contribute to national policy recommendations" (line 8; not on resume)
- [ ] README/MCP/examples: apply Railway decision (Step 5) to live-API links
- [ ] Paper edit list (Tab 1), each with the evidence behind it:
  - [ ] Rater count: §3 line "seven human raters" → 6 (matches §2.4, §4.6, resume)
  - [ ] Prompt count: "55 prompts × 3 = 165" (§2.3, §3, Fig 1 caption) vs 54 prompts in rated data → state 55 submitted / 54 rated, with reason
  - [ ] §2.4 "rated by four people" contradicts "two per model" → "two raters"
  - [ ] §2.6 Claude "38 matched pairs" → 16 (by prompt ID). Table 2 Claude column must use the corrected alpha values
  - [x] BUG FIXED: load_rater_data.py paired raters by row order ("Prompt ID" header never matched). Claude alpha was
        computed on mismatched prompts. Fixed + tests/test_load_rater_data.py; results regenerated. Means/baselines/
        calibration unchanged; GPT-4/LLaMA alpha unchanged; Claude alpha changed (acc 0.49→−0.05, fair 0.03→0.38,
        neut 0.07→0.25, rep −0.16→0.08, rel −0.14→−0.08). n_pairs column also fixed (was total items).
  - [ ] Penalties: Table 3 matches code; but §4.6 says moderate penalties come from IQR, while code uses 1.47/1.20/0.95/1.40, which are not in results/calibrated_multipliers.csv (moderate = 0.70/0.64/0.40) → reword or footnote
  - [ ] In-text citation index errors (e.g. Liang et al. cited as ^19; Liang is ref 18)
  - [ ] Embedding-diagnostic claims (abstract, §4.1, §4.4, §8): describe as the study-time method, not a current feature (code removed it)
  - [ ] Remove leftover notes ("Mentor name?" comment, any [a]/[b] comment anchors)
  - [ ] TWO DATASETS: §3 Results (Table 1, Figs 1+) = older 7-rater pruned set; §2.4/§2.6/§4.6 = 276-rating 6-rater set.
        They disagree (§3: "Claude strongest in every category but accuracy"; 276 set: GPT-4 highest overall 3.78,
        LLaMA highest Fairness 3.54, which §4.6 itself reports). §8 "LLaMA lowest fairness" also contradicts §4.6. Needs a decision.
  - [ ] Citations 18/19 swapped throughout: Liang (HELM) cited as ^19, Li et al. cited as ^18
  - [ ] §7.2 dangling clause "; aggregate such metrics across dozens of publicly released models via the Open-LLM Leaderboard" (citation missing)
  - [ ] Unsourced % in paper: §4.4 "+127.1 %", §5.3 "+127% / +134% / +83%", "50–75%" (same numbers cut from README as unsourced)
  - [x] §4.6 "−3.0 for terrorism-adjacent language" — SOURCED: `score -= 3.0` in commit af82d67 (git history)
  - Data available to close holes (checked 2026-11-20):
    - Prompt categories: `Category`/`Subcategory` columns in biaslense/data/*.xlsx (54 rows each) → §3 category figures rebuildable
    - §5 mitigation: Drive sheet "Sikh Bias in LLMs - Improved Responses" (3 strategies × 3 models, ~5 prompts each) → §5 % recomputable, small-n caveat
- [ ] Move Tab 2 (speech script) + Tab 3 (reviewer feedback table) to a separate private doc, then delete them from the paper

### Step 2 — Review + reference verification (Jaspreet; not delegable)
- [ ] Review the Step 1 diff and edit list
- [ ] Verify all 38 references: exists, authors, venue, year, pages, and that the in-text claim matches the source
  - Start with the refs whose metadata looks off: 6, 7, 8, 10, 11, 12, 19, 22, 36, 37

### Step 3 — Tab 1 as PDF in repo
- [ ] Export Tab 1 → docs/paper/biaslense_paper.pdf
- [ ] Remove stale docs/paper/*.txt (contains old "Mentor name?" note); link PDF from README
- [ ] Commit

### Step 4 — LinkedIn end date (Jaspreet, manual)
- [ ] Set end date; also change resume "Present" → same date so they match

### Step 5 — Railway
- Facts: resume links only GitHub + LinkedIn, not the API. Streamlit app (free) does not call Railway.
  SDK defaults to local mode. Railway is used by: README live-API links, mcp_server.py default URL, examples/sdk_basic.py.
- [ ] Decide keep or cancel; if cancel, update those 3 places to self-host instructions BEFORE cancelling

### Done check
- [ ] Resume ↔ README ↔ paper ↔ LinkedIn: dates, counts (276/6/3/54), claims all agree
- [ ] Every README link resolves
