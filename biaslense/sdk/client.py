"""BamiPClient - Unified interface for local and remote bias analysis."""

import os
import time
import csv
from pathlib import Path
from typing import List, Optional, Dict, Any
import requests

from .types import AnalyzeRequest, AnalyzeResponse, BatchAnalyzeResponse, HealthResponse
from .exceptions import (
    ConnectionException,
    RateLimitException,
    ValidationException,
    ServerException,
)


class BamiPClient:
    """Unified client for BiasLens bias detection (local or remote).

    Supports both local BAMIPPipeline (for development/testing) and
    remote REST API (for production). Same API for both.

    Args:
        endpoint: Remote API URL (e.g., "https://api.railway.app").
                 If None, uses local BAMIPPipeline directly.
        timeout: HTTP request timeout in seconds (remote only). Default 30.

    Example:
        >>> # Local (development)
        >>> client = BamiPClient()
        >>> result = client.analyze(
        ...     prompt="Tell me about Sikhism",
        ...     ai_response="Sikhs are Muslims...",
        ...     ai_model="gpt-4"
        ... )

        >>> # Remote (production)
        >>> client = BamiPClient(endpoint="https://api.railway.app")
        >>> result = client.analyze(prompt="...", ai_response="...")

        >>> # Batch processing
        >>> results = client.analyze_batch([
        ...     {"prompt": "...", "ai_response": "..."},
        ... ], verbose=True)
    """

    def __init__(self, endpoint: Optional[str] = None, timeout: int = 30):
        """Initialize BAMIP client.

        Args:
            endpoint: Remote API URL. If None, uses local pipeline.
            timeout: HTTP timeout in seconds (remote only).

        Raises:
            ConnectionException: If endpoint is provided but unreachable.
        """
        self.endpoint = endpoint
        self.timeout = timeout
        self._is_local = endpoint is None
        self._pipeline = None
        self._request_count = 0
        self._last_request_time = 0

        if self._is_local:
            # Import and cache local pipeline
            try:
                from biaslense.src.core.bamip_pipeline import BAMIPPipeline

                self._pipeline = BAMIPPipeline()
            except ImportError as e:
                raise ConnectionException(
                    "Could not import local BAMIPPipeline. "
                    "Are you running from the BiasLens directory? "
                    f"Error: {e}"
                )
        else:
            # Verify remote endpoint is reachable
            self._check_connection()

    def _check_connection(self) -> None:
        """Verify remote endpoint is reachable.

        Raises:
            ConnectionException: If endpoint is unreachable.
        """
        try:
            response = requests.get(
                f"{self.endpoint}/health",
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise ConnectionException(
                f"Cannot reach endpoint: {self.endpoint}\n"
                f"Is the API running? Error: {e}"
            )
        except requests.exceptions.Timeout:
            raise ConnectionException(
                f"Timeout connecting to {self.endpoint}\n"
                f"Try increasing timeout or checking network."
            )
        except Exception as e:
            raise ConnectionException(
                f"Failed to connect to {self.endpoint}: {e}"
            )

    def analyze(
        self,
        prompt: str,
        ai_response: str,
        ai_model: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> AnalyzeResponse:
        """Analyze AI-generated response for sociocultural bias.

        Args:
            prompt: Original question/instruction sent to the AI.
            ai_response: AI-generated text to analyze.
            ai_model: Model that generated the response.
                     One of: gpt-4, gpt-3.5-turbo, claude-3, claude-2, llama-2, gemini.
                     Defaults to "unknown" if not provided.
            timeout: Request timeout in seconds (remote only).
                    Defaults to client timeout.

        Returns:
            AnalyzeResponse with bias scores, risk level, and mitigation strategy.

        Raises:
            ValidationException: If prompt or ai_response is empty.
            RateLimitException: If rate limit exceeded (auto-retries first).
            ConnectionException: If unable to reach remote endpoint.
            ServerException: If API returns 5xx error.

        Example:
            >>> client = BamiPClient()
            >>> result = client.analyze(
            ...     prompt="What is Sikhism?",
            ...     ai_response="Sikhs are a Muslim group...",
            ...     ai_model="gpt-4"
            ... )
            >>> print(f"Risk: {result.risk_level}")
            >>> print(f"Fairness: {result.original_scores.fairness}/5")
        """
        # Validate inputs
        if not prompt or not prompt.strip():
            raise ValidationException("prompt cannot be empty")
        if not ai_response or not ai_response.strip():
            raise ValidationException("ai_response cannot be empty")

        request = AnalyzeRequest(
            prompt=prompt,
            ai_response=ai_response,
            ai_model=ai_model or "unknown",
        )

        if self._is_local:
            return self._analyze_local(request)
        else:
            return self._analyze_remote(request, timeout)

    def _analyze_local(self, request: AnalyzeRequest) -> AnalyzeResponse:
        """Analyze using local BAMIPPipeline."""
        try:
            result = self._pipeline.run(
                prompt=request.prompt,
                ai_response=request.ai_response,
                ai_model=request.ai_model,
            )

            # Convert to AnalyzeResponse
            return AnalyzeResponse(
                prompt=request.prompt,
                ai_model=request.ai_model,
                risk_level=result.risk_level.value,
                bias_type=result.bias_type or "Unknown",
                prompt_subtype=result.prompt_subtype or "Unknown",
                original_scores=result.bias_detection_result.dimension_scores,
                similarity_to_stereotypes=result.similarity_result.max_similarity,
                strategy_used=result.mitigation_result.strategy.value,
                strategy_reasoning=result.strategy_selection_reasoning,
                improved_response=result.improved_response,
                improved_scores=result.mitigation_result.new_scores,
                bias_reduction=result.mitigation_result.bias_reduction,
                recommendations=result.recommendations,
            )
        except Exception as e:
            raise ServerException(f"Local analysis failed: {e}")

    def _analyze_remote(
        self, request: AnalyzeRequest, timeout: Optional[int] = None
    ) -> AnalyzeResponse:
        """Analyze using remote REST API with retry logic."""
        timeout = timeout or self.timeout
        max_retries = 3
        retry_delay = 1.0  # Start with 1 second, exponential backoff

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.endpoint}/analyze",
                    json=request.dict(),
                    timeout=timeout,
                )

                if response.status_code == 200:
                    return AnalyzeResponse(**response.json())

                elif response.status_code == 429:
                    # Rate limited - retry with backoff
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"Rate limited. Waiting {wait_time:.1f}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RateLimitException(
                            "Rate limit exceeded after retries. "
                            "Wait before retrying or use local endpoint."
                        )

                elif response.status_code >= 500:
                    raise ServerException(
                        f"API error {response.status_code}: {response.text}"
                    )

                elif response.status_code == 400:
                    raise ValidationException(
                        f"Invalid request: {response.json().get('detail', 'Unknown error')}"
                    )

                else:
                    raise ServerException(
                        f"Unexpected response {response.status_code}: {response.text}"
                    )

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                raise ConnectionException(
                    f"Request timeout after {max_retries} attempts"
                )
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                raise ConnectionException(
                    f"Failed to connect to {self.endpoint}"
                )

    def analyze_batch(
        self,
        items: List[Dict[str, str]],
        verbose: bool = False,
    ) -> List[AnalyzeResponse]:
        """Analyze multiple AI-generated responses in batch.

        Automatically handles rate limiting and batching.

        Args:
            items: List of dicts with keys: prompt, ai_response (optional: ai_model).
                   Example: [{"prompt": "...", "ai_response": "..."}, ...]
            verbose: Show progress bar if True.

        Returns:
            List of AnalyzeResponse objects (in same order as input).

        Raises:
            ValidationException: If items list is empty.
            RateLimitException: If rate limit exceeded.
            ConnectionException: If unable to reach endpoint.

        Example:
            >>> client = BamiPClient()
            >>> responses = [
            ...     {"prompt": "Q1", "ai_response": "Response 1", "ai_model": "gpt-4"},
            ...     {"prompt": "Q2", "ai_response": "Response 2"},
            ... ]
            >>> results = client.analyze_batch(responses, verbose=True)
            >>> print(f"Analyzed {len(results)} responses")
        """
        if not items:
            raise ValidationException("items list cannot be empty")

        results = []

        if self._is_local:
            # Local: Process sequentially
            for i, item in enumerate(items):
                if verbose:
                    print(f"[{i+1}/{len(items)}] Analyzing...", end="\r")
                try:
                    result = self.analyze(
                        prompt=item["prompt"],
                        ai_response=item["ai_response"],
                        ai_model=item.get("ai_model"),
                    )
                    results.append(result)
                except Exception as e:
                    print(f"\nError analyzing item {i+1}: {e}")
                    raise

            if verbose:
                print(f"[{len(items)}/{len(items)}] Complete!         ")
        else:
            # Remote: Use batch endpoint with smart chunking
            chunk_size = 20  # Respects rate limit (5 req/min)

            for chunk_start in range(0, len(items), chunk_size):
                chunk = items[chunk_start : chunk_start + chunk_size]
                chunk_num = (chunk_start // chunk_size) + 1
                total_chunks = (len(items) + chunk_size - 1) // chunk_size

                if verbose:
                    print(f"[Chunk {chunk_num}/{total_chunks}] Sending {len(chunk)} items...")

                try:
                    # Convert to AnalyzeRequest objects
                    requests_list = [
                        AnalyzeRequest(
                            prompt=item["prompt"],
                            ai_response=item["ai_response"],
                            ai_model=item.get("ai_model"),
                        )
                        for item in chunk
                    ]

                    # Make batch request
                    response = requests.post(
                        f"{self.endpoint}/analyze/batch",
                        json={"items": [r.dict() for r in requests_list]},
                        timeout=self.timeout,
                    )

                    if response.status_code == 200:
                        batch_response = BatchAnalyzeResponse(**response.json())
                        results.extend(batch_response.results)
                    elif response.status_code == 429:
                        raise RateLimitException(
                            "Batch rate limit exceeded. Try smaller batches or wait."
                        )
                    else:
                        raise ServerException(
                            f"Batch API error {response.status_code}: {response.text}"
                        )

                except RateLimitException:
                    raise
                except Exception as e:
                    raise ConnectionException(f"Batch request failed: {e}")

                # Small delay between chunks to avoid rate limiting
                if chunk_start + chunk_size < len(items):
                    time.sleep(0.5)

            if verbose:
                print(f"Batch analysis complete: {len(results)}/{len(items)} items")

        return results

    def get_health(self) -> HealthResponse:
        """Check if API is healthy and running.

        Returns:
            HealthResponse with status and version.

        Raises:
            ConnectionException: If unable to reach endpoint.

        Example:
            >>> client = BamiPClient(endpoint="https://api.railway.app")
            >>> health = client.get_health()
            >>> print(f"Status: {health.status}, Version: {health.version}")
        """
        if self._is_local:
            return HealthResponse(status="ok", version="1.0.0")

        try:
            response = requests.get(
                f"{self.endpoint}/health",
                timeout=self.timeout,
            )
            if response.status_code == 200:
                return HealthResponse(**response.json())
            else:
                raise ConnectionException(
                    f"Health check failed: {response.status_code}"
                )
        except requests.exceptions.Exception as e:
            raise ConnectionException(f"Cannot reach health endpoint: {e}")

    def analyze_file(
        self,
        filepath: str,
        verbose: bool = False,
    ) -> List[AnalyzeResponse]:
        """Analyze all AI responses in a CSV file.

        Expected CSV columns: prompt, ai_response (optional: ai_model)

        Args:
            filepath: Path to CSV file.
            verbose: Show progress if True.

        Returns:
            List of AnalyzeResponse objects.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If CSV is missing required columns.

        Example:
            >>> client = BamiPClient()
            >>> results = client.analyze_file("responses.csv", verbose=True)
            >>> print(f"Analyzed {len(results)} responses from CSV")
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        items = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None or "prompt" not in reader.fieldnames:
                raise ValueError(
                    "CSV must have 'prompt' column and 'ai_response' column"
                )
            if "ai_response" not in reader.fieldnames:
                raise ValueError(
                    "CSV must have 'prompt' column and 'ai_response' column"
                )

            for row in reader:
                items.append({
                    "prompt": row["prompt"],
                    "ai_response": row["ai_response"],
                    "ai_model": row.get("ai_model"),
                })

        return self.analyze_batch(items, verbose=verbose)

    def export_results(
        self,
        results: List[AnalyzeResponse],
        filepath: str,
        format: str = "csv",
    ) -> None:
        """Export analysis results to a file.

        Args:
            results: List of AnalyzeResponse objects.
            filepath: Output file path.
            format: Output format. Currently only "csv" is supported.

        Raises:
            ValueError: If format is not supported.

        Example:
            >>> results = client.analyze_batch([...])
            >>> client.export_results(results, "analysis_output.csv")
        """
        if format != "csv":
            raise ValueError(f"Unsupported format: {format}. Only 'csv' is supported.")

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "prompt",
                "ai_model",
                "risk_level",
                "original_accuracy",
                "original_fairness",
                "original_neutrality",
                "original_representation",
                "improved_accuracy",
                "improved_fairness",
                "improved_neutrality",
                "improved_representation",
                "bias_reduction_percent",
                "strategy_used",
                "recommendations",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                writer.writerow({
                    "prompt": result.prompt,
                    "ai_model": result.ai_model,
                    "risk_level": result.risk_level,
                    "original_accuracy": result.original_scores.accuracy,
                    "original_fairness": result.original_scores.fairness,
                    "original_neutrality": result.original_scores.neutrality,
                    "original_representation": result.original_scores.representation,
                    "improved_accuracy": result.improved_scores.accuracy,
                    "improved_fairness": result.improved_scores.fairness,
                    "improved_neutrality": result.improved_scores.neutrality,
                    "improved_representation": result.improved_scores.representation,
                    "bias_reduction_percent": f"{result.bias_reduction_percent():.2f}%",
                    "strategy_used": result.strategy_used,
                    "recommendations": " | ".join(result.recommendations),
                })

        print(f"Exported {len(results)} results to {filepath}")
