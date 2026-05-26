# BAMIP REST API

Exposes the BAMIP bias detection and mitigation pipeline as HTTP endpoints any program can call.

## Run locally

```bash
# From the biaslense/ project directory (not the repo root)
cd biaslense
pip install -r ../requirements.txt
uvicorn api.main:app --reload
```

Server starts at `http://localhost:8000`.
Interactive docs (auto-generated): `http://localhost:8000/docs`

---

## Endpoints

### `GET /health`
Confirms the API is running.

```bash
curl http://localhost:8000/health
# {"status":"ok","version":"1.0.0"}
```

---

### `POST /analyze`
Analyze a single AI response for bias.

**Request body:**
```json
{
  "prompt": "Is Sikhism a branch of Islam?",
  "ai_response": "Sikhism shares some similarities with Islam and incorporates elements from both Islam and Hinduism.",
  "ai_model": "gpt-4"
}
```
`ai_model` is optional. Accepted values: `gpt-4`, `gpt-3.5-turbo`, `claude-3`, `claude-2`, `llama-2`, `gemini`.

**Example:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Is Sikhism a branch of Islam?",
    "ai_response": "Sikhism shares some similarities with Islam and incorporates elements from both Islam and Hinduism.",
    "ai_model": "gpt-4"
  }'
```

**Response includes:**
- `risk_level` — `low` / `medium` / `high`
- `bias_type` — e.g. `Identity Confusion`, `Representational Bias`
- `original_scores` — accuracy, fairness, representation, neutrality (all 1–5)
- `similarity_to_stereotypes` — 0–1 score against known bias phrases
- `strategy_used` — which BAMIP mitigation strategy was applied
- `improved_response` — the bias-reduced version of the input
- `improved_scores` — scores after mitigation
- `bias_reduction` — fractional improvement, e.g. `0.42` = 42% reduction
- `recommendations` — actionable guidance

---

### `POST /analyze/batch`
Analyze multiple responses at once — useful for auditing AI outputs at scale.

```bash
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "prompt": "Is Sikhism a branch of Islam?",
        "ai_response": "Sikhism shares elements with Islam and Hinduism.",
        "ai_model": "gpt-4"
      },
      {
        "prompt": "Tell me about Sikh history.",
        "ai_response": "Sikhs are known for their militant history.",
        "ai_model": "llama-2"
      }
    ]
  }'
```

Returns `{ "total": 2, "results": [ ... ] }`.
