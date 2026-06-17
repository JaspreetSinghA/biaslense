"""
BiasLens MCP Server
Exposes bias analysis as tools callable by Claude Desktop and other MCP clients.
Calls the hosted BiasLens REST API — no heavy ML dependencies required.

Install & run:
    pip install biaslense
    biaslens-mcp

Add to Claude Desktop's claude_desktop_config.json:
    {
      "mcpServers": {
        "biaslens": {
          "command": "biaslens-mcp"
        }
      }
    }

Override the API URL:
    BIASLENS_API_URL=https://your-instance.up.railway.app biaslens-mcp
"""

import os
import requests
from mcp.server.fastmcp import FastMCP

API_URL = os.environ.get("BIASLENS_API_URL", "https://web-production-59ba5.up.railway.app").rstrip("/")

mcp = FastMCP("BiasLens")


@mcp.tool()
def analyze_bias(prompt: str, ai_response: str, ai_model: str = "") -> dict:
    """
    Analyze an AI-generated response for cultural or identity bias.

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
    payload = {"prompt": prompt, "ai_response": ai_response}
    if ai_model:
        payload["ai_model"] = ai_model

    resp = requests.post(f"{API_URL}/analyze", json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def analyze_bias_batch(items: list[dict]) -> dict:
    """
    Analyze multiple AI-generated responses for bias in one call.

    Each item must have 'prompt' and 'ai_response' keys. 'ai_model' is optional.

    Args:
        items: List of dicts, each with keys: prompt (str), ai_response (str),
               ai_model (str, optional).
    """
    resp = requests.post(f"{API_URL}/analyze/batch", json={"items": items}, timeout=60)
    resp.raise_for_status()
    return resp.json()


def main():
    mcp.run()


if __name__ == "__main__":
    main()
