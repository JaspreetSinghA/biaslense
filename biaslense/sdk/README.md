# BiasLens Python SDK

Analyze AI-generated content for sociocultural bias with a simple Python library.

## Installation

```bash
pip install biaslense
```

Or, for development:
```bash
git clone https://github.com/JaspreetSinghA/biaslense.git
cd biaslense
pip install -e .
```

---

## Quick Start

```python
from biaslense.sdk import BamiPClient

# Initialize client (local or remote)
client = BamiPClient()

# Analyze a single response
result = client.analyze(
    prompt="Tell me about Sikhism",
    ai_response="Sikhs are Muslims who wear turbans...",
    ai_model="gpt-4"
)

print(f"Risk Level: {result.risk_level}")
print(f"Fairness Score: {result.original_scores.fairness}/5")
print(f"Improved: {result.bias_reduction_percent():.1f}% bias reduction")
```

---

## Usage Patterns

### 1. Local Analysis (Development)

Use the local BAMIPPipeline for development and testing:

```python
from biaslense.sdk import BamiPClient

# No endpoint = uses local pipeline directly
client = BamiPClient()

result = client.analyze(
    prompt="What is Sikhism?",
    ai_response="Sikhism is a religion...",
    ai_model="gpt-4"
)
```

**Advantages:**
- No network calls (fast)
- Perfect for development and testing
- No rate limits
- Works offline

### 2. Remote Analysis (Production)

Use the remote REST API for production deployments:

```python
from biaslense.sdk import BamiPClient

# Specify your API endpoint
client = BamiPClient(endpoint="https://api.railway.app")

result = client.analyze(
    prompt="What is Sikhism?",
    ai_response="Sikhism is a religion...",
    ai_model="gpt-4"
)
```

**Advantages:**
- Distributed analysis (scales horizontally)
- Centralized API management
- Easy to integrate with existing systems
- Can be shared across teams

### 3. Batch Processing

Analyze multiple responses efficiently:

```python
responses = [
    {
        "prompt": "What is Sikhism?",
        "ai_response": "Sikhism is a religion...",
        "ai_model": "gpt-4"
    },
    {
        "prompt": "Describe Sikh practices",
        "ai_response": "Sikhs visit temples...",
        "ai_model": "claude-3"
    },
]

# Analyze batch with automatic retry and rate limit handling
results = client.analyze_batch(responses, verbose=True)

for result in results:
    print(f"{result.risk_level}: {result.bias_reduction_percent():.1f}%")
```

### 4. CSV File Processing

Analyze responses from a CSV file:

```python
# Input CSV must have columns: prompt, ai_response (optional: ai_model)
results = client.analyze_file("responses.csv", verbose=True)

# Export results to CSV
client.export_results(results, "analysis_output.csv")
```

---

## API Reference

### BamiPClient

Main class for bias analysis.

#### Constructor

```python
BamiPClient(
    endpoint: Optional[str] = None,
    timeout: int = 30
)
```

**Parameters:**
- `endpoint` (str, optional): Remote API URL. If None, uses local pipeline.
- `timeout` (int): HTTP timeout in seconds (remote only). Default: 30.

**Raises:**
- `ConnectionException`: If endpoint is unreachable.

#### Methods

##### `analyze()`

Analyze a single AI-generated response.

```python
analyze(
    prompt: str,
    ai_response: str,
    ai_model: Optional[str] = None,
    timeout: Optional[int] = None
) -> AnalyzeResponse
```

**Parameters:**
- `prompt` (str): Original question sent to AI
- `ai_response` (str): AI-generated text to analyze
- `ai_model` (str, optional): Model name (gpt-4, claude-3, etc.)
- `timeout` (int, optional): HTTP timeout (remote only)

**Returns:** `AnalyzeResponse` with bias scores, risk level, and mitigation strategy

**Raises:**
- `ValidationException`: If prompt or ai_response is empty
- `RateLimitException`: If rate limit exceeded (auto-retries)
- `ConnectionException`: If unable to reach endpoint
- `ServerException`: If API returns 5xx error

**Example:**
```python
result = client.analyze(
    prompt="Tell me about Sikhism",
    ai_response="Sikhs are Muslims...",
    ai_model="gpt-4"
)
```

##### `analyze_batch()`

Analyze multiple responses in batch.

```python
analyze_batch(
    items: List[Dict[str, str]],
    verbose: bool = False
) -> List[AnalyzeResponse]
```

**Parameters:**
- `items` (list): List of dicts with keys: prompt, ai_response, ai_model (optional)
- `verbose` (bool): Show progress bar if True

**Returns:** List of `AnalyzeResponse` objects (same order as input)

**Raises:**
- `ValidationException`: If items list is empty
- `RateLimitException`: If rate limit exceeded
- `ConnectionException`: If unable to reach endpoint

**Example:**
```python
responses = [
    {"prompt": "...", "ai_response": "..."},
    {"prompt": "...", "ai_response": "..."},
]
results = client.analyze_batch(responses, verbose=True)
```

##### `get_health()`

Check API health status.

```python
get_health() -> HealthResponse
```

**Returns:** `HealthResponse` with status and version

**Example:**
```python
health = client.get_health()
print(f"Status: {health.status}, Version: {health.version}")
```

##### `analyze_file()`

Analyze responses from a CSV file.

```python
analyze_file(
    filepath: str,
    verbose: bool = False
) -> List[AnalyzeResponse]
```

**Parameters:**
- `filepath` (str): Path to CSV file with columns: prompt, ai_response, ai_model (optional)
- `verbose` (bool): Show progress if True

**Returns:** List of `AnalyzeResponse` objects

**Raises:**
- `FileNotFoundError`: If file does not exist
- `ValueError`: If CSV is missing required columns

**Example:**
```python
results = client.analyze_file("responses.csv", verbose=True)
```

##### `export_results()`

Export analysis results to CSV file.

```python
export_results(
    results: List[AnalyzeResponse],
    filepath: str,
    format: str = "csv"
) -> None
```

**Parameters:**
- `results` (list): List of `AnalyzeResponse` objects
- `filepath` (str): Output file path
- `format` (str): Output format (currently only "csv")

**Example:**
```python
client.export_results(results, "output.csv")
```

### AnalyzeResponse

Complete analysis result for a single response.

**Attributes:**
- `prompt` (str): Original prompt (echoed back)
- `ai_model` (str): AI model that generated the response
- `risk_level` (str): "low", "medium", or "high"
- `bias_type` (str): Detected bias category
- `prompt_subtype` (str): Prompt structure type
- `original_scores` (DimensionScores): Scores before mitigation
- `improved_scores` (DimensionScores): Scores after mitigation
- `similarity_to_stereotypes` (float): 0–1 cosine similarity to bias phrases
- `strategy_used` (str): Which mitigation strategy was applied
- `strategy_reasoning` (str): Why this strategy was selected
- `improved_response` (str): Bias-mitigated version of response
- `bias_reduction` (float): Fraction of improvement (0–1)
- `recommendations` (list): Actionable recommendations

**Convenience Methods:**
- `bias_reduction_percent()` → float: Bias reduction as percentage (0–100)
- `fairness_improved()` → bool: True if fairness score improved
- `neutrality_improved()` → bool: True if neutrality score improved

**Example:**
```python
result = client.analyze(...)

print(f"Risk: {result.risk_level}")
print(f"Bias Reduction: {result.bias_reduction_percent():.1f}%")
print(f"Fairness: {result.original_scores.fairness:.1f} → {result.improved_scores.fairness:.1f}")

for rec in result.recommendations:
    print(f"  - {rec}")
```

### DimensionScores

Bias scores across five dimensions (1–5 scale).

**Attributes:**
- `accuracy` (float): Factual correctness
- `fairness` (float): Impartiality and absence of stereotypes
- `representation` (float): Depth and nuance
- `neutrality` (float): Linguistic balance
- `overall` (float): Mean of all dimensions

**Example:**
```python
scores = result.original_scores
print(f"Fairness: {scores.fairness}/5")
print(f"Neutrality: {scores.neutrality}/5")
```

---

## Error Handling

The SDK provides clear exceptions for different error scenarios:

```python
from biaslense.sdk import (
    BamiPClient,
    ValidationException,
    RateLimitException,
    ConnectionException,
    ServerException,
)

client = BamiPClient(endpoint="https://api.railway.app")

try:
    result = client.analyze(prompt="...", ai_response="...")
except ValidationException as e:
    # Empty prompt/response
    print(f"Invalid input: {e}")
except RateLimitException as e:
    # Rate limit exceeded (SDK auto-retries first)
    print(f"Please wait: {e}")
except ConnectionException as e:
    # Cannot reach API
    print(f"API unavailable: {e}")
except ServerException as e:
    # API returned 5xx error
    print(f"Server error: {e}")
```

---

## Performance Tips

### Batch Processing
- For 100+ items, use `analyze_batch()` instead of looping `analyze()`
- SDK automatically chunks large batches to respect rate limits
- Local batch processing is sequential but faster than HTTP calls

### Rate Limiting
- Remote: 10 requests/minute for `/analyze`, 5/minute for `/analyze/batch`
- SDK automatically retries with exponential backoff on 429 errors
- Use local client for development to avoid rate limits

### Caching
- For identical prompts, consider caching locally:
  ```python
  cache = {}
  if prompt not in cache:
      cache[prompt] = client.analyze(prompt, response)
  result = cache[prompt]
  ```

---

## Examples

See `examples/` directory:
- `sdk_basic.py` — Quick start with local and remote
- `sdk_batch.py` — Advanced batch processing
- `sdk_file_processing.py` — CSV workflows

Run examples:
```bash
cd /Users/jaspreetsingh/biaslense
python examples/sdk_basic.py
python examples/sdk_batch.py
python examples/sdk_file_processing.py
```

---

## Configuration

### Environment Variables (Optional)

```bash
# For remote endpoint
export BIASLENSE_ENDPOINT="https://api.railway.app"

# Or pass directly to client
client = BamiPClient(endpoint=os.environ.get("BIASLENSE_ENDPOINT"))
```

---

## Troubleshooting

### "Could not import local BAMIPPipeline"
- Ensure you're running from the BiasLens directory
- Install with: `pip install -e .` (editable install)

### "Cannot reach endpoint"
- Verify the API is deployed and running
- Check network connectivity
- Confirm endpoint URL is correct

### "Rate limit exceeded"
- Wait before retrying
- Use smaller batches
- Switch to local client for development

### Results seem incorrect
- Check that `ai_model` is set correctly (affects strategy selection)
- Verify `prompt` and `ai_response` are in the right order
- Try the same request locally vs remotely to isolate issues

---

## Support

- **Documentation**: See [ALGORITHM.md](../ALGORITHM.md) for methodology
- **Issues**: https://github.com/JaspreetSinghA/biaslense/issues
- **Email**: bamiPipeline@jaspreetahluwalia.com

---

## License

MIT License - See LICENSE file for details
