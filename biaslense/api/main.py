"""
BAMIP REST API
Exposes bias detection and mitigation as callable HTTP endpoints.
Run from the biaslense/ project directory:
    uvicorn api.main:app --reload
"""

import os
import sys

# Resolve project root (biaslense/) so imports match the Streamlit app
_here = os.path.dirname(os.path.abspath(__file__))          # biaslense/api/
_project_root = os.path.dirname(_here)                       # biaslense/
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from typing import Optional
from fastapi import FastAPI, HTTPException

from src.core.bamip_pipeline import BAMIPPipeline, AIModel
from api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    DimensionScores,
    HealthResponse,
)

app = FastAPI(
    title="BAMIP API",
    description="Bias-Aware Mitigation and Intervention Pipeline — detect and reduce bias in AI-generated text.",
    version="1.0.0",
)

_pipeline = BAMIPPipeline()

VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MODEL_MAP = {
    "gpt-4": AIModel.GPT_4,
    "gpt-3.5-turbo": AIModel.GPT_3_5,
    "claude-3": AIModel.CLAUDE_3,
    "claude-2": AIModel.CLAUDE_2,
    "llama-2": AIModel.LLAMA_2,
    "gemini": AIModel.GEMINI,
}


def _resolve_model(model_str: Optional[str]) -> AIModel:
    if not model_str:
        return AIModel.UNKNOWN
    return _MODEL_MAP.get(model_str.lower(), AIModel.UNKNOWN)


def _build_response(req: AnalyzeRequest) -> AnalyzeResponse:
    ai_model = _resolve_model(req.ai_model)
    result = _pipeline.process_prompt(req.prompt, req.ai_response, ai_model)

    orig = result.bias_detection_result
    impr = result.mitigation_result.improved_bias_result

    original_scores = DimensionScores(
        accuracy=round(orig.accuracy_score, 2),
        fairness=round(orig.fairness_score, 2),
        representation=round(orig.representation_score, 2),
        neutrality=round(orig.linguistic_balance_score, 2),
        overall=round(orig.overall_score, 2),
    )

    improved_scores = DimensionScores(
        accuracy=round(impr.accuracy_score, 2),
        fairness=round(impr.fairness_score, 2),
        representation=round(impr.representation_score, 2),
        neutrality=round(impr.linguistic_balance_score, 2),
        overall=round(impr.overall_score, 2),
    )

    bias_reduction = round(result.mitigation_result.bias_reduction_score, 4)

    return AnalyzeResponse(
        prompt=req.prompt,
        ai_model=ai_model.value,
        risk_level=result.risk_level.value,
        bias_type=result.bias_type or "None",
        prompt_subtype=result.prompt_subtype or "General",
        original_scores=original_scores,
        similarity_to_stereotypes=round(result.similarity_result.max_similarity, 4),
        strategy_used=result.mitigation_result.strategy_used.value,
        strategy_reasoning=result.strategy_selection_reasoning,
        improved_response=result.improved_response,
        improved_scores=improved_scores,
        bias_reduction=bias_reduction,
        recommendations=result.recommendations,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    """Liveness check — confirms the API is running."""
    return HealthResponse(status="ok", version=VERSION)


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Bias Analysis"])
def analyze(req: AnalyzeRequest):
    """
    Analyze a single AI-generated response for bias.

    Returns bias scores across 5 dimensions, risk level, the detected bias type,
    the optimal mitigation strategy, and a bias-reduced version of the response.
    """
    try:
        return _build_response(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch", response_model=BatchAnalyzeResponse, tags=["Bias Analysis"])
def analyze_batch(req: BatchAnalyzeRequest):
    """
    Analyze multiple AI-generated responses in one call.

    Useful for auditing large sets of AI outputs. Returns one result per input item.
    """
    if not req.items:
        raise HTTPException(status_code=400, detail="items list cannot be empty")
    try:
        results = [_build_response(item) for item in req.items]
        return BatchAnalyzeResponse(total=len(results), results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
