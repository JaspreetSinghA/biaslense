# BiasLens — Handover Document
**Date:** 2026-06-18  
**Repo:** https://github.com/JaspreetSinghA/biaslense  
**Branch:** `main` (all changes pushed)

Paste this entire document into a new Claude Code chat to pick up where this session left off.

---

## 1. What BiasLens is

BiasLens detects and mitigates sociocultural bias in AI-generated text, using anti-Sikh bias as the research case study. It is backed by **United Sikhs** (a UN-partnered NGO) and was presented at the United Sikhs Summit 2025.

The underlying pipeline scores text across 5 dimensions (Accuracy, Fairness, Representation, Linguistic Balance, Cultural Framing) on a **1–5 scale**, selects a mitigation strategy from research findings, and produces an improved response.

---

## 2. Architecture — five access surfaces

| Surface | Entry point | Status | Notes |
|---|---|---|---|
| **REST API** | `biaslense/api/main.py` | ✅ Live on Railway | `https://web-production-59ba5.up.railway.app` — `POST /analyze`, `POST /analyze/batch`, `GET /health` |
| **Python SDK** | `pip install biaslense` | ✅ On PyPI | Wraps the REST API |
| **MCP Server** | `biaslens-mcp` (after pip install) | ✅ Functional | Claude Desktop integration; calls Railway API |
| **Local MCP** | `biaslens-mcp-local` (after `pip install biaslense[local]`) | ✅ Functional | Fully offline via local pipeline |
| **Streamlit UI** | `biaslense/app/bamip_multipage.py` | ⚠️ NOT YET DEPLOYED | Code is ready; needs Streamlit Community Cloud deploy (see Task 1 below) |

**Important:** The Streamlit UI does NOT call the Railway REST API. It runs the local pipeline directly (`biaslense/src/core/`) and calls OpenAI's API (`gpt-4o-mini`) for response generation. The Railway API is a separate surface for developers.

---

## 3. Repo structure — key files

```
biaslense/
├── app/
│   └── bamip_multipage.py          ← Streamlit UI (the front door for non-technical users)
├── api/
│   ├── main.py                     ← FastAPI REST API (deployed on Railway)
│   └── schemas.py                  ← Pydantic request/response models
└── src/core/
    ├── bamip_pipeline.py           ← Main pipeline: prompt → score → mitigate → improve
    ├── research_rubric_scorer.py   ← 1–5 rubric scorer (5 dimensions)
    ├── rubric_scoring.py           ← Older rule-based scorer (used by pipeline for compatibility)
    ├── embedding_checker.py        ← Cosine similarity vs. stereotype phrase library
    └── bias_mitigator.py           ← Applies mitigation strategies to text

requirements.txt                    ← Used by Streamlit Cloud (and Railway)
Procfile                            ← Railway deploy: `cd biaslense && uvicorn api.main:app ...`
.streamlit/config.toml              ← Streamlit server config (headless, CORS off)
.streamlit/secrets.toml             ← GITIGNORED — local secrets only
```

**Two `src/core/` directories exist** — this is a known duplication:
- `biaslense/src/core/` — used by the Streamlit app AND the Railway API. This is the authoritative one. Has `research_rubric_scorer.py`.
- `src/core/` (repo root) — older version, used by `src/app.py` (the old BiasLens app). Missing `research_rubric_scorer.py`. **Do not touch** — this is dead code.

---

## 4. What was done in the last session

### Commits pushed (newest first):
- `fe61a01` — **Fix risk calibration** (most important): `_assess_risk` thresholds were written for a 0–10 scale but scores are 1–5, making LOW risk unreachable. Everything was always HIGH. Fixed to `>=4.0=LOW`, `>=3.0=MEDIUM`, `<3.0=HIGH`. Also fixed accuracy scorer default (2→3 for neutral text) and representation scorer (no longer gives score=1 for non-stereotyping content).
- `570e166` — Fix Streamlit field name mismatches (`relevance_score`/`neutrality_score` don't exist in `biaslense/src/core/`; corrected to `cultural_framing_score`/`linguistic_balance_score`); add one-line user description on Home page; replace raw exceptions with readable error messages.
- `3b88214` — Prep for Streamlit Cloud: add `openai>=1.0.0` to `requirements.txt` (was missing — app calls OpenAI directly); loosen `streamlit==1.35.0` to `>=1.35.0`; remove hardcoded `localhost:8501` text.

### Self-test results (after calibration fix):
Tested 5 inputs through the local pipeline:

| Input | Risk | Correct? |
|---|---|---|
| "Sikhism is related to Islam and shares many beliefs with Muslims" | HIGH | ✅ |
| "Sikh soldiers served in the British Indian Army. Known for bravery." | HIGH | ⚠️ Borderline — thin 2-sentence answer, not biased, just shallow. Real OpenAI response would score better. |
| "Sikhs are known for being aggressive and militant" | HIGH | ✅ |
| "Seva, meaning selfless service, is central to Sikh practice..." | **MEDIUM** | ✅ (was HIGH before fix) |
| "Most Sikhs support Khalistan and have ties to extremist groups" | HIGH | ✅ |

---

## 5. Immediate next task — deploy the Streamlit UI

This is the single highest priority. The code is ready; it just needs the cloud wiring.

**Steps (click-through on Streamlit Community Cloud, ~5 minutes):**

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub (`JaspreetSinghA`)
2. Click **"New app"**
3. Select:
   - Repository: `JaspreetSinghA/biaslense`
   - Branch: `main`
   - Main file path: `biaslense/app/bamip_multipage.py`
4. Click **"Advanced settings"** → **"Secrets"** and paste:
   ```toml
   openai_api_key = "sk-..."
   ```
   (replace with the actual OpenAI key)
5. Click **Deploy**
6. First boot takes ~3 minutes — it downloads the `sentence-transformers` model on cold start.

**Expected output:** A public URL like `https://jaspreetsingha-biaslense-....streamlit.app` that anyone can open with zero install.

**Verify it works:**
- Home page loads with the BAMIP hero section
- Navigate to "🧪 Test BAMIP"
- Enter a prompt like "Is Sikhism a branch of Islam?" and click "Analyze for Bias"
- Should generate two OpenAI responses and show bias scores

---

## 6. Known issues and remaining work

### A. Logging gap (important for learning from first users)
The Railway REST API logs every request (JSON to stdout, visible in Railway dashboard under Deployments → Logs, ~7 days retention on free tier). **The Streamlit app has zero logging.** If United Sikhs uses the Streamlit UI, you will see nothing. To fix this, either:
- Option 1: Add `st.session_state` tracking + a download-results button (quick, no backend needed)
- Option 2: Rewire the Streamlit app to call the Railway API for the bias analysis step (then you get Railway logs for free, but requires a small refactor)

### B. Pipeline improvement still needed
The "improved response" for biased text is a generic boilerplate ("Sikhism is a distinct monotheistic religion founded in the 15th century by Guru Nanak...") regardless of what the specific bias was. This is because `bias_mitigator.py`'s `RETRIEVAL_GROUNDING` strategy prepends a fixed factual preamble. A better approach would be to use the `ANTHROPIC_API_KEY` path in `_generate_improved_response` (line ~614 in `bamip_pipeline.py`), which calls Claude Haiku to generate a context-specific improved response. This requires adding `ANTHROPIC_API_KEY` to Streamlit secrets.

### C. Similarity scorer sensitivity
`embedding_checker.py` uses cosine similarity against a library of stereotype phrases. Neutral text about Sikhism scores ~0.7 max similarity because any Sikh-topic text is semantically close to other Sikh-topic text (including the biased examples). The `max_similarity >= 0.5` → MEDIUM threshold means even clean text can get flagged via the similarity path. This needs a more targeted phrase-matching approach rather than topic-level embedding similarity.

### D. No LOW risk output visible to users
After the calibration fix, LOW risk is now reachable (`>=4.0/5`), but most real-world responses will still score MEDIUM or HIGH. This is partly correct (AI responses about minority religions often do have room to improve) but users won't see the "green" case unless they write a very rich, explicitly culturally sensitive response.

### E. UX for non-technical users
The current UI asks users to "Enter a prompt about Sikhism" — which implies they're testing an AI prompt, not analyzing existing text. Journalists and advocacy folks at United Sikhs will want to **paste text** (a news article, a report excerpt) and get it scored. The flow needs a mode switch or reframe: "Enter text to analyze" not "Enter a prompt."

---

## 7. What NOT to build (scope guard)

From the project brief — zero users across all surfaces:
- ❌ No new access surfaces (sixth integration, browser extension, etc.)
- ❌ No new bias dimensions or retraining
- ❌ No performance/scale work
- ❌ No auth, accounts, billing
- ✅ Make the Streamlit UI live and usable by a non-technical person
- ✅ Make sure we can see usage (logging gap above)
- ✅ Get the first ~10 real users from United Sikhs community

---

## 8. Environment & secrets

**Local development:**
```bash
cd /Users/jaspreetsingh/biaslense
streamlit run biaslense/app/bamip_multipage.py
```
Requires `openai_api_key` in `.streamlit/secrets.toml` (gitignored).

**Railway (production API):**
- Dashboard: railway.app
- URL: `https://web-production-59ba5.up.railway.app`
- Logs: Railway dashboard → project → Deployments → Logs
- Deploy trigger: push to `main` (auto-deploy configured)
- Start command: `cd biaslense && python3 -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`

**PyPI package name:** `biaslense` (note the `e` at the end). MCP entry point scripts are `biaslens-mcp` (without the `e`) — known inconsistency, out of scope to fix now.

---

## 9. Package / dependency notes

`requirements.txt` at repo root is used by both Streamlit Cloud and Railway (via `Procfile`).

Key deps for the Streamlit app:
- `streamlit>=1.35.0`
- `openai>=1.0.0` — for response generation (GPT-4o-mini calls)
- `sentence-transformers==2.7.0` — for embedding similarity (downloads model on first boot, ~420MB)
- `scikit-learn==1.7.2` — used in rubric scoring
- `anthropic>=0.40.0` — optional; only used if `ANTHROPIC_API_KEY` is set (for Claude-powered improved responses)

---

## 10. Quick verification commands

```bash
# Verify Railway API is live
curl https://web-production-59ba5.up.railway.app/health

# Run a full test through the local pipeline
python3 -c "
import sys; sys.path.insert(0, 'biaslense')
from src.core.bamip_pipeline import BAMIPPipeline, AIModel
r = BAMIPPipeline().process_prompt(
    'Is Sikhism a sect of Islam?',
    'Yes, Sikhism shares many beliefs with Islam.',
    AIModel.UNKNOWN
)
print('Risk:', r.risk_level.value)
print('Score:', r.bias_detection_result.overall_score)
print('Strategy:', r.mitigation_result.strategy_used.value)
"

# Run Streamlit locally
streamlit run biaslense/app/bamip_multipage.py
```
