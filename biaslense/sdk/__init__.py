"""BiasLens Python SDK - Easy bias detection for AI-generated content.

Install: pip install biaslense
Usage:
    from biaslense.sdk import BamiPClient

    client = BamiPClient()  # Local or remote
    result = client.analyze(
        prompt="...",
        ai_response="...",
        ai_model="gpt-4"
    )
    print(f"Risk: {result.risk_level}")
"""

from .client import BamiPClient
from .exceptions import (
    BamiPException,
    ConnectionException,
    RateLimitException,
    ValidationException,
    ServerException,
)
from .types import AnalyzeRequest, AnalyzeResponse, BatchAnalyzeRequest

__version__ = "1.0.0"
__all__ = [
    "BamiPClient",
    "AnalyzeRequest",
    "AnalyzeResponse",
    "BatchAnalyzeRequest",
    "BamiPException",
    "ConnectionException",
    "RateLimitException",
    "ValidationException",
    "ServerException",
]
