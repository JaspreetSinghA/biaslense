"""Type definitions and data models for BiasLens SDK.

These wrap the REST API schemas with convenience methods and docstrings.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request to analyze a single AI-generated response.

    Attributes:
        prompt: The original question or instruction sent to the AI.
        ai_response: The AI-generated text to analyze for bias.
        ai_model: Which AI model generated the response (optional).
                 One of: gpt-4, gpt-3.5-turbo, claude-3, claude-2, llama-2, gemini.

    Example:
        >>> req = AnalyzeRequest(
        ...     prompt="Tell me about Sikhism",
        ...     ai_response="Sikhs are Muslims who wear turbans.",
        ...     ai_model="gpt-4"
        ... )
    """

    prompt: str = Field(..., description="The original question or prompt sent to the AI")
    ai_response: str = Field(..., description="The AI-generated text to analyze for bias")
    ai_model: Optional[str] = Field(
        None,
        description="Which AI produced the response: gpt-4, gpt-3.5-turbo, claude-3, llama-2, gemini. Omit if unknown.",
    )


class BatchAnalyzeRequest(BaseModel):
    """Request to analyze multiple AI-generated responses.

    Attributes:
        items: List of AnalyzeRequest objects to process in batch.

    Example:
        >>> batch = BatchAnalyzeRequest(items=[
        ...     AnalyzeRequest(prompt="...", ai_response="..."),
        ...     AnalyzeRequest(prompt="...", ai_response="..."),
        ... ])
    """

    items: List[AnalyzeRequest] = Field(
        ..., description="List of prompt-response pairs to analyze (must not be empty)"
    )


class DimensionScores(BaseModel):
    """Bias scores across five dimensions (1–5 scale).

    Attributes:
        accuracy: Factual correctness about the topic.
        fairness: Impartiality and absence of harmful stereotypes.
        representation: Depth, nuance, and acknowledgment of diversity.
        neutrality: Linguistic balance, tone, and language neutrality.
        overall: Mean of all dimensions.

    Example:
        >>> scores = DimensionScores(
        ...     accuracy=3.5, fairness=2.0, representation=3.0,
        ...     neutrality=2.5, overall=2.75
        ... )
        >>> print(f"Fairness: {scores.fairness}/5")
    """

    accuracy: float = Field(..., description="Factual correctness (1–5)")
    fairness: float = Field(..., description="Equal, stereotype-free treatment (1–5)")
    representation: float = Field(..., description="Nuance and depth of portrayal (1–5)")
    neutrality: float = Field(..., description="Tone and language balance (1–5)")
    overall: float = Field(..., description="Mean of all dimensions (1–5)")

    def mean_score(self) -> float:
        """Return average of all dimension scores."""
        return (self.accuracy + self.fairness + self.representation + self.neutrality) / 4


class AnalyzeResponse(BaseModel):
    """Complete bias analysis result for an AI-generated response.

    Attributes:
        prompt: The original prompt (echoed back).
        ai_model: The AI model that generated the response.
        risk_level: Overall risk assessment: "low", "medium", or "high".
        bias_type: Detected bias category (e.g., "Religious Conflation").
        prompt_subtype: Prompt structure type (e.g., "Comparative", "Identity Confusion").
        original_scores: Dimension scores before mitigation.
        similarity_to_stereotypes: Cosine similarity (0–1) to known bias phrases.
        strategy_used: Which mitigation strategy was applied.
        strategy_reasoning: Why this strategy was selected.
        improved_response: The bias-mitigated version of the response.
        improved_scores: Dimension scores after mitigation.
        bias_reduction: Fraction of bias improvement (0–1, e.g., 0.42 = 42% reduction).
        recommendations: List of actionable recommendations for the user.

    Example:
        >>> result = client.analyze(prompt="...", ai_response="...")
        >>> print(f"Risk: {result.risk_level}")
        >>> print(f"Fairness improved: {result.bias_reduction * 100:.1f}%")
        >>> print(f"Strategy: {result.strategy_used}")
    """

    # Input echo
    prompt: str = Field(..., description="The original prompt (echoed back)")
    ai_model: str = Field(..., description="The AI model that generated the response")

    # Bias assessment
    risk_level: str = Field(..., description="low / medium / high")
    bias_type: str = Field(..., description="Detected bias category, e.g. Representational Bias")
    prompt_subtype: str = Field(..., description="Prompt category, e.g. Identity Confusion")
    original_scores: DimensionScores = Field(..., description="Bias scores before mitigation")
    similarity_to_stereotypes: float = Field(..., description="0–1 cosine similarity to known bias phrases")

    # Mitigation
    strategy_used: str = Field(..., description="Which BAMIP strategy was applied")
    strategy_reasoning: str = Field(..., description="Why this strategy was selected")
    improved_response: str = Field(..., description="The bias-mitigated version of the AI response")
    improved_scores: DimensionScores = Field(..., description="Bias scores after mitigation")
    bias_reduction: float = Field(..., description="Score improvement as a fraction, e.g. 0.42 = 42% reduction")

    # Guidance
    recommendations: List[str] = Field(..., description="Actionable recommendations")

    def bias_reduction_percent(self) -> float:
        """Return bias reduction as a percentage (0–100)."""
        return self.bias_reduction * 100

    def fairness_improved(self) -> bool:
        """Return True if fairness score improved."""
        return self.improved_scores.fairness > self.original_scores.fairness

    def neutrality_improved(self) -> bool:
        """Return True if neutrality score improved."""
        return self.improved_scores.neutrality > self.original_scores.neutrality


class BatchAnalyzeResponse(BaseModel):
    """Response from batch analysis of multiple responses.

    Attributes:
        total: Number of items analyzed.
        results: List of AnalyzeResponse objects (in same order as input).

    Example:
        >>> batch_result = client.analyze_batch([...])
        >>> for result in batch_result.results:
        ...     print(f"{result.risk_level}: {result.bias_reduction_percent():.1f}%")
    """

    total: int = Field(..., description="Number of items analyzed")
    results: List[AnalyzeResponse] = Field(..., description="Analysis results (in same order as input)")


class HealthResponse(BaseModel):
    """Health check response from API.

    Attributes:
        status: "ok" if API is healthy.
        version: API version number.
    """

    status: str = Field(..., description="ok if healthy, otherwise error description")
    version: str = Field(..., description="API version (e.g. 1.0.0)")
