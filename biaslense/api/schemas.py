"""
Request and response shapes for the BAMIP API.
Defines what data goes in and what comes out of each endpoint.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    prompt: str = Field(..., description="The original question or prompt sent to the AI")
    ai_response: str = Field(..., description="The AI-generated text to analyze for bias")
    ai_model: Optional[str] = Field(
        None,
        description="Which AI produced the response: gpt-4, gpt-3.5-turbo, claude-3, llama-2, gemini. Omit if unknown.",
    )


class BatchAnalyzeRequest(BaseModel):
    items: List[AnalyzeRequest] = Field(..., description="List of prompt-response pairs to analyze")


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class DimensionScores(BaseModel):
    accuracy: float = Field(..., description="Factual correctness (1–5)")
    fairness: float = Field(..., description="Equal, stereotype-free treatment (1–5)")
    representation: float = Field(..., description="Nuance and depth of portrayal (1–5)")
    neutrality: float = Field(..., description="Tone and language balance (1–5)")
    overall: float = Field(..., description="Mean of all dimensions (1–5)")


class AnalyzeResponse(BaseModel):
    # Input echo
    prompt: str
    ai_model: str

    # Bias assessment
    risk_level: str = Field(..., description="low / medium / high")
    bias_type: str = Field(..., description="Detected bias category, e.g. Representational Bias")
    prompt_subtype: str = Field(..., description="Prompt category, e.g. Identity Confusion")
    original_scores: DimensionScores
    similarity_to_stereotypes: float = Field(..., description="0–1 cosine similarity to known bias phrases")

    # Mitigation
    strategy_used: str = Field(..., description="Which of the 3 BAMIP strategies was applied")
    strategy_reasoning: str = Field(..., description="Why this strategy was selected")
    improved_response: str = Field(..., description="The bias-mitigated version of the AI response")
    improved_scores: DimensionScores
    bias_reduction: float = Field(..., description="Score improvement as a fraction, e.g. 0.42 = 42% reduction")

    # Guidance
    recommendations: List[str]


class BatchAnalyzeResponse(BaseModel):
    total: int
    results: List[AnalyzeResponse]


class HealthResponse(BaseModel):
    status: str
    version: str
