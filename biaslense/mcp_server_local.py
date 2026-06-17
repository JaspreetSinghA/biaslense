"""
BiasLens MCP Server (Local)
Runs the full bias analysis pipeline locally — no network required.
Requires the full ML dependencies: pip install biaslense[local]

Run standalone:
    biaslens-mcp-local

Add to Claude Desktop's claude_desktop_config.json:
    {
      "mcpServers": {
        "biaslens-local": {
          "command": "biaslens-mcp-local"
        }
      }
    }
"""

import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from mcp.server.fastmcp import FastMCP
from src.core.bamip_pipeline import BAMIPPipeline, AIModel

_pipeline = BAMIPPipeline()

_MODEL_MAP = {
    "gpt-4": AIModel.GPT_4,
    "gpt-3.5-turbo": AIModel.GPT_3_5,
    "claude-3": AIModel.CLAUDE_3,
    "claude-2": AIModel.CLAUDE_2,
    "llama-2": AIModel.LLAMA_2,
    "gemini": AIModel.GEMINI,
}

mcp = FastMCP("BiasLens-Local")


def _resolve_model(model_str: str) -> AIModel:
    return _MODEL_MAP.get(model_str.lower(), AIModel.UNKNOWN) if model_str else AIModel.UNKNOWN


@mcp.tool()
def analyze_bias(prompt: str, ai_response: str, ai_model: str = "") -> dict:
    """
    Analyze an AI-generated response for cultural or identity bias (runs locally).

    Returns bias scores across 5 dimensions (accuracy, fairness, representation,
    neutrality, overall), the detected risk level, bias type, a bias-reduced
    version of the response, and actionable recommendations.

    Args:
        prompt: The original question or prompt sent to the AI.
        ai_response: The AI-generated text to analyze for bias.
        ai_model: Which model produced the response. Accepts: gpt-4,
                  gpt-3.5-turbo, claude-3, claude-2, llama-2, gemini.
                  Leave blank if unknown.
    """
    model = _resolve_model(ai_model)
    result = _pipeline.process_prompt(prompt, ai_response, model)

    orig = result.bias_detection_result
    impr = result.mitigation_result.improved_bias_result

    return {
        "prompt": prompt,
        "ai_model": model.value,
        "risk_level": result.risk_level.value,
        "bias_type": result.bias_type or "None",
        "prompt_subtype": result.prompt_subtype or "General",
        "original_scores": {
            "accuracy": round(orig.accuracy_score, 2),
            "fairness": round(orig.fairness_score, 2),
            "representation": round(orig.representation_score, 2),
            "neutrality": round(orig.linguistic_balance_score, 2),
            "overall": round(orig.overall_score, 2),
        },
        "similarity_to_stereotypes": round(result.similarity_result.max_similarity, 4),
        "strategy_used": result.mitigation_result.strategy_used.value,
        "strategy_reasoning": result.strategy_selection_reasoning,
        "improved_response": result.improved_response,
        "improved_scores": {
            "accuracy": round(impr.accuracy_score, 2),
            "fairness": round(impr.fairness_score, 2),
            "representation": round(impr.representation_score, 2),
            "neutrality": round(impr.linguistic_balance_score, 2),
            "overall": round(impr.overall_score, 2),
        },
        "bias_reduction": round(result.mitigation_result.bias_reduction_score, 4),
        "recommendations": result.recommendations,
    }


@mcp.tool()
def analyze_bias_batch(items: list[dict]) -> dict:
    """
    Analyze multiple AI-generated responses for bias in one call (runs locally).

    Each item must have 'prompt' and 'ai_response' keys. 'ai_model' is optional.

    Args:
        items: List of dicts, each with keys: prompt (str), ai_response (str),
               ai_model (str, optional).
    """
    results = [
        analyze_bias(
            prompt=item["prompt"],
            ai_response=item["ai_response"],
            ai_model=item.get("ai_model", ""),
        )
        for item in items
    ]
    return {"total": len(results), "results": results}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
