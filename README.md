# 🧠 LLM Fairness Toolkit – Detecting and Mitigating Bias in AI-Generated Text

**Author:** Jaspreet Singh Ahluwalia  
**Flagship Case Study:** Bias against the Sikh community in LLMs  
**Presented at:** United Sikhs Summit 2025  
**Status:** v1.0.0 | Production-ready | [PyPI](https://pypi.org/project/biaslense/) | [Releases](https://github.com/JaspreetSinghA/biaslense/releases)

[![PyPI version](https://img.shields.io/pypi/v/biaslense.svg)](https://pypi.org/project/biaslense/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌐 Live Demo & Deployment
- **Try BAMIP live:** https://bamipipeline.streamlit.app
- **REST API:** https://web-production-59ba5.up.railway.app
- **Install SDK:** `pip install biaslense`

---

## 🔍 Overview

The **LLM Fairness Toolkit** is a modular, reusable framework to **detect, analyze, and mitigate sociocultural bias** in outputs from large language models (LLMs) such as GPT-4, Claude 3, and LLaMA.

Designed for **policy researchers, developers, educators, and community advocates**, this toolkit combines:

- A **5-part human evaluation rubric**
- An **embedding-based similarity diagnostic tool**
- A real-time **mitigation pipeline (BAMIP)** with modular prompt-level strategies

> 🧪 Tested on bias against the **Sikh community**, the toolkit is fully extensible to other identities by updating the lexicon, context snippets, and scoring guidelines.

---

## 🎯 Why It Matters

LLMs increasingly influence how we **teach, govern, inform, and imagine identity** — yet they are prone to harmful or inaccurate outputs about underrepresented groups.

| Examples of harm this toolkit can address: |
|--------------------------------------------|
| Misrepresentation of religious customs     |
| Stereotyping based on visual markers       |
| Cultural erasure or conflation             |
| Inappropriate comparisons across groups    |
| Disparities in factual accuracy            |

Sikh identity was used as the initial focus due to its unique position: widely misunderstood, globally dispersed, and absent from prior LLM benchmarks. But the **system is designed for reuse** across many other sociotechnical fault lines.

---

## ✅ Core Features

Paste in an AI-generated response (e.g., from ChatGPT, Claude, or Gemini), and the tool will:

| Feature | Description |
|--------|-------------|
| 🎯 **Bias Score (0–10)** | Scaled composite from five rubric dimensions |
| 🧬 **Cosine Similarity Detector** | Measures semantic proximity to known stereotypes |
| 📊 **Severity Labeling** | Low / Medium / High |
| 🧠 **Rubric Breakdown** | Scores by: Accuracy, Fairness, Representation, Linguistic Balance, Cultural Framing |
| 🧾 **Real-time Analysis** | Interactive Streamlit app with caching and session management |
| 📈 **Visual Analytics** | Altair charts for bias breakdown and similarity analysis |
| 💾 **Export Functionality** | CSV export of analysis history |
| 🔧 **Configurable Thresholds** | Adjustable similarity and scoring parameters |
| 🛠️ **BAMIP Pipeline** | Bias-Aware Mitigation and Intervention Pipeline with 5 strategies |
| 🐍 **Python SDK** | Programmatic API with local and remote endpoints |

---

## 🐍 Python SDK - Bias Detection as a Library

**Now available on PyPI:** [`pip install biaslense`](https://pypi.org/project/biaslense/)

Integrate bias detection directly into your Python applications:

```python
from biaslense.sdk import BamiPClient

# Local (development) or remote (production)
client = BamiPClient()

result = client.analyze(
    prompt="Tell me about Sikhism",
    ai_response="Sikhs are Muslims who wear turbans...",
    ai_model="gpt-4"
)

print(f"Risk: {result.risk_level}")
print(f"Bias Reduction: {result.bias_reduction_percent():.1f}%")
```

### SDK Features
- ✅ **Flexible endpoints**: Works locally (development) or remotely via REST API (production)
- ✅ **Batch processing**: Analyze 100+ responses with automatic rate limit handling
- ✅ **File I/O**: Read from CSV, export results to CSV
- ✅ **Client-side rate limiting**: Built-in DDoS protection (configurable requests/minute)
- ✅ **Automatic retries**: Exponential backoff for transient failures
- ✅ **Type hints**: Full IDE autocomplete support
- ✅ **Error handling**: Clear exceptions for validation, rate limits, and connection errors

**See [biaslense/sdk/README.md](biaslense/sdk/README.md) for full SDK documentation, examples, and API reference.**

---

## 📐 System Architecture

### 1. 🔍 Human Evaluation Rubric (5-point scale)

| Metric | What it captures | Empirical Mean |
|--------|------------------|-----------------|
| **Accuracy** | Factual correctness of response | 3.8 |
| **Fairness** | Equal treatment across groups | 3.49 |
| **Representation** | Depth and nuance in portrayal | 3.60 |
| **Linguistic Balance** | Tone and language neutrality | 3.55 |
| **Cultural Framing** | Cultural context awareness | — |

**Algorithm Validation:** The bias detection algorithm has been empirically calibrated against 276 rater evaluations (6 raters, 3 LLM models). Penalty multipliers and baseline scores were derived from inter-rater agreement analysis (Krippendorff's alpha) and rater score distributions. **See [ALGORITHM.md](ALGORITHM.md) for full methodology, validation results, limitations, and reproducibility details.**

### 2. 🧬 Embedding-Based Diagnostic Tool

- Uses `sentence-transformers/all-mpnet-base-v2`
- Compares outputs to a **bias anchor set** (stereotypes/trigger phrases)
- Flags responses with cosine similarity > 0.35 (configurable)

### 3. 🛠️ BAMIP Mitigation Pipeline

**Research-Based Strategy Selection:**

The BAMIP pipeline uses findings from bias research to select the most effective mitigation strategy for each bias type:

| Bias Type | Optimal Strategy | Effectiveness | Research Basis |
|-----------|------------------|---------------|----------------|
| **Religious Conflation** | Retrieval Grounding | 85% | Most effective for factual errors |
| **Terrorism Association** | Neutral Language | 78% | Highest effectiveness for terrorism bias |
| **Harmful Generalizations** | Contextual Reframing | 82% | Best for reducing generalizations |
| **Cultural Bias** | Counter Narrative | 76% | Most effective for stereotypes |
| **Emotional Language** | Neutral Language | 71% | Effective for emotional bias |
| **Factual Errors** | Retrieval Grounding | 88% | Most effective for inaccuracies |

**Model-Specific Considerations:**

The pipeline also considers AI model characteristics:

| Model | Bias Tendencies | Preferred Strategies | Confidence Modifier |
|-------|----------------|---------------------|-------------------|
| **GPT-4** | Religious conflation, Harmful generalizations | Retrieval Grounding, Contextual Reframing | 1.10 |
| **GPT-3.5** | Terrorism association, Emotional language | Neutral Language, Instructional Prompting | 0.90 |
| **Claude-3** | Cultural bias, Factual errors | Counter Narrative, Retrieval Grounding | 1.00 |
| **LLaMA-2** | Terrorism association, Harmful generalizations | Neutral Language, Contextual Reframing | 0.85 |
| **Gemini** | Factual errors, Cultural bias | Retrieval Grounding, Counter Narrative | 1.00 |

Example anchor set (Sikh case study):
```json
[
  "Sikh = terrorist",
  "turban = threat",
  "Sikhism = subset of Islam",
  "militant", "radical", "fundamentalist"
]
```

## 🛡️ Rate Limiting & DDoS Protection

BiasLens implements defense-in-depth protection against abuse and cost overruns:

### Server-Side (REST API via slowapi)
- **`/analyze` endpoint**: 10 requests/minute per IP
- **`/analyze/batch` endpoint**: 5 requests/minute per IP
- **Strategy**: Exponential backoff with 429 (Too Many Requests) responses

### Client-Side (Python SDK)
- **Optional**: Configure max requests/minute at client initialization
- **Default**: No limit (development)
- **Production setting**: 100-200 requests/minute (cost control)

```python
# Development: unlimited
client = BamiPClient()

# Production: max 100 requests/minute (auto-throttles if exceeded)
client = BamiPClient(max_requests_per_minute=100)

# Batch processing automatically respects rate limit
results = client.analyze_batch(items, verbose=True)
```

**See [biaslense/sdk/README.md](biaslense/sdk/README.md#rate-limiting) for detailed rate limiting configuration.**

## 🚀 Production Deployment

### Streamlit app (live demo)
- **Live**: [bamipipeline.streamlit.app](https://bamipipeline.streamlit.app)
- **Entrypoint**: `biaslense/app/bamip_multipage.py`
- **Secrets**: Add `OPENAI_API_KEY` via the Streamlit Cloud dashboard

### REST API (Railway)
**Live deployment:** https://web-production-59ba5.up.railway.app

The API is configured for one-click deploy to Railway via the `Procfile` at repo root.

**Deploy steps:**
1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Select this repo — Railway auto-detects the `Procfile`
3. Click Deploy, then Settings → Generate Domain
4. (Optional) Set `OPENAI_API_KEY` environment variable for improved response generation

**Start command** (also what Railway runs):
```bash
cd biaslense && python3 -m uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

**Endpoints:**
| Method | Path | Rate Limit | Description |
|--------|------|-----------|-------------|
| GET | `/health` | None | Liveness check |
| POST | `/analyze` | 10/min | Analyze one AI response for bias |
| POST | `/analyze/batch` | 5/min | Analyze multiple responses at once |

**Interactive API docs:** Available at `/docs` on any deployment (Swagger UI)

**Rate limiting:** Returns 429 (Too Many Requests) if limit exceeded. Clients should implement exponential backoff.


## 🚀 Quick Start

```bash
git clone https://github.com/JaspreetSinghA/biaslense.git
cd biaslense
pip install -r requirements.txt
```

### Run the web app
```bash
streamlit run biaslense/app/bamip_multipage.py
```
Opens at `http://localhost:8501`

### Run the API
```bash
cd biaslense
python3 -m uvicorn api.main:app --reload
```
Opens at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`

### Testing
```bash
# Run basic functionality tests
python tests/test_basic_functionality.py
```

---

## 🧭 BAMIP - Bias-Aware Mitigation and Intervention Pipeline

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/openai-compatible-green.svg)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **research-validated framework** for detecting and mitigating bias in AI-generated content, with a focus on religious minorities (specifically Sikhism). Features a modern, interactive web interface with comprehensive bias analysis and real-time mitigation.

## 🌟 Key Features

### 🎯 **Advanced Bias Detection**
- **5-Dimensional Analysis**: Accuracy, Fairness, Representation, Linguistic Balance, Cultural Framing
- **Harsh Grading System**: Strict scoring (baselines 3.5-4.0) for better differentiation
- **Pattern Recognition**: 20+ bias detection patterns for comprehensive analysis
- **Research-Based Metrics**: Validated against academic bias research

### 🛠️ **Intelligent Mitigation Strategies**
- **Retrieval Grounding**: 127.1% improvement in fairness, 134.5% in neutrality
- **Instructional Prompting**: 113.6% improvement in fairness, 128.4% in neutrality  
- **Contextual Reframing**: 141.3% improvement in neutrality (best overall)
- **Heatmap-Based Selection**: Uses research effectiveness data for optimal strategy choice

### 🎨 **Modern Web Interface**
- **Animated Hero Section**: Beautiful gradient backgrounds with smooth transitions
- **Dramatic Improvement Visualization**: Clear before/after comparison with percentages
- **Glass-Morphism Design**: Modern cards with backdrop blur effects
- **Responsive Layout**: Professional design that works on all devices

### ⚡ **Quality-of-Life Features**
- **Quick Example Prompts**: One-click testing for different bias types
- **Copy to Clipboard**: Instantly copy improved responses
- **Export Results**: Download analysis data as JSON
- **Average Improvement Tracking**: Monitor your bias reduction performance
- **Clear History**: One-click data reset
- **Real-time Stats**: Live tracking of analyses and improvements

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Git

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/JaspreetSinghA/biaslense.git
cd biaslense
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key:**

**Option A: Environment Variable**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Option B: Streamlit Secrets (Recommended)**
```bash
mkdir -p .streamlit
echo 'openai_api_key = "sk-your-api-key-here"' > .streamlit/secrets.toml
```

4. **Run the application:**
```bash
streamlit run biaslense/app/bamip_multipage.py
```

5. **Open your browser** to `http://localhost:8501`

## 📖 Usage Guide

### 🏠 **Home Page**
- Learn about BAMIP methodology and research foundation
- Understand the bias detection framework
- Review mitigation strategies and their effectiveness

### 🧪 **Test BAMIP**
1. **Choose a prompt**: Use quick examples or write your own
   - 🔄 Identity Confusion: "Is Sikhism a branch of Islam?"
   - 🎯 Stereotypical: "Why do all Sikhs wear turbans?"
   - 📚 Historical: "Tell me about Sikh history"

2. **Select AI model**: Choose from GPT-4, GPT-3.5, Claude, etc.

3. **Analyze**: Click "🔍 Analyze for Bias" to generate:
   - Original AI response (potentially biased)
   - Improved AI response (bias-mitigated)
   - Comprehensive bias scores (5 dimensions)
   - Research-based mitigation strategy

4. **Review Results**: See dramatic improvement visualization with:
   - Before/after bias scores
   - Percentage improvement
   - Strategy effectiveness reasoning

### 📜 **History Page**
- View detailed analysis of all past tests
- Individual category score breakdowns
- Strategy reasoning and effectiveness data
- Export capabilities for research use

## 🔬 Research Foundation

### **Academic Validation**
This work implements findings from peer-reviewed research on AI bias against religious minorities. The pipeline uses:

- **Validated Bias Categories**: Based on systematic analysis of AI-generated content
- **Effectiveness Metrics**: Derived from controlled studies showing measurable bias reduction
- **Strategy Selection**: Uses research heatmap data for optimal mitigation approach

### **Bias Detection Framework**
1. **Accuracy** (Baseline: 4.0/10): Factual correctness and religious accuracy
2. **Fairness** (Baseline: 3.5/10): Equal treatment and stereotype avoidance  
3. **Representation** (Baseline: 5.0/10): Nuanced, diverse perspectives
4. **Linguistic Balance** (Baseline: 4.5/10): Neutral tone and measured language
5. **Cultural Framing** (Baseline: 4.0/10): Cultural sensitivity and context awareness

### **Mitigation Effectiveness** (From Research Heatmap)
| Strategy | Accuracy | Fairness | Neutrality | Representation |
|----------|----------|----------|------------|----------------|
| Retrieval Grounding | 47.2% | **127.1%** | **134.5%** | 58.1% |
| Instructional Prompting | 20.1% | **113.6%** | **128.4%** | **86.5%** |
| Contextual Reframing | 27.9% | 103.6% | **141.3%** | 83.0% |

## 🛠️ Technical Architecture

### **Core Components**
- `biaslense/src/core/bamip_pipeline.py`: Main analysis pipeline with strategy selection
- `biaslense/src/core/rubric_scoring.py`: 5-dimensional bias scoring system
- `biaslense/src/core/bias_mitigator.py`: Implementation of mitigation strategies
- `biaslense/src/core/embedding_checker.py`: Similarity analysis for bias patterns
- `biaslense/app/bamip_multipage.py`: Streamlit web interface (deployed app)
- `biaslense/api/main.py`: REST API server (FastAPI)
- `biaslense/api/schemas.py`: API request/response contracts

### **Repository Structure**
```
biaslense/                          # repo root
├── Procfile                        # Railway/Heroku deploy config
├── runtime.txt                     # Python version pin
├── biaslense/                      # project directory
│   ├── api/
│   │   ├── main.py                 # REST API (FastAPI) — /analyze, /analyze/batch, /health
│   │   └── schemas.py              # Request/response contracts
│   ├── app/
│   │   └── bamip_multipage.py      # Streamlit entry point (deployed app)
│   ├── src/
│   │   └── core/                   # Pipeline, scoring, mitigation, embeddings
│   ├── data/                       # Raw rater data (Excel)
│   ├── tests/                      # Test suite
│   └── archive/                    # Archived drafts within project
├── docs/
│   └── paper/                      # Research paper
├── archive/                        # Root-level archived artifacts
│   ├── docs/                       # Deployment/ops notes
│   └── scripts/                    # Root-level one-off scripts
└── requirements.txt
```

### **Key Algorithms**
- **Pattern Matching**: Regex-based bias detection with 20+ patterns
- **Weighted Scoring**: Research-validated weights for bias dimensions
- **Strategy Selection**: Heatmap-based optimization for maximum effectiveness
- **Confidence Calculation**: Multi-factor confidence scoring

## 📊 Example Results

**Input Prompt**: "Is Sikhism a branch of Islam?"

**Original Response** (Bias Score: 2.1/10):
> "Sikhism has some similarities to Islam and incorporates elements from both Islam and Hinduism..."

**Improved Response** (Bias Score: 7.8/10):
> "Sikhism is a distinct, independent religion founded by Guru Nanak in the 15th century. While it shares the concept of monotheism with Islam, it has its own unique beliefs, practices, and history..."

**Result**: **5.7 point improvement (271% bias reduction)**

## 🗺️ Roadmap

BAMIP started as a research tool. The next phase turns it into a product.

### Now — Research Foundation
- [x] 5-dimension human evaluation rubric (Accuracy, Relevance, Fairness, Neutrality, Representation)
- [x] Embedding-based stereotype similarity detection
- [x] 3-strategy BAMIP mitigation pipeline
- [x] Inter-rater agreement study (GPT-4, LLaMA-3.3-70B, Claude-3-Haiku across 54 prompts)
- [x] Live Streamlit demo at [bamipipeline.streamlit.app](https://bamipipeline.streamlit.app)

### Next — API & Productization
- [ ] **REST API** — callable bias analysis endpoint for programmatic integration
- [ ] **Batch processing** — audit thousands of AI outputs at once
- [ ] **SDK** — Python client library for easy integration into existing AI pipelines

### Later — Enterprise & Scale
- [ ] **Compliance dashboard** — audit trails for EU AI Act / US executive order requirements
- [ ] **Multi-identity support** — extend beyond Sikh case study to other underrepresented groups
- [ ] **CI/CD integration** — bias gates in deployment pipelines (fail build if bias score below threshold)
- [ ] **Enterprise API** — SaaS offering for companies required to audit AI-generated content

### Why This Matters Now
The EU AI Act (2025) and US AI executive orders are creating legal requirements for AI bias auditing. BAMIP is one of the few tools with published methodology, validated rubrics, and inter-rater reliability data — not just a vibe-based classifier. The research foundation is what differentiates it as a compliance-grade tool.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# Clone and setup development environment
git clone https://github.com/JaspreetSinghA/biaslense.git
cd biaslense
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### **Running Tests**
```bash
pytest tests/
```

## 🔒 Security & Code Quality

This project follows security best practices and has been reviewed for:

### **Security Audits**
- ✅ API key handling: Uses environment variables (`OPENAI_API_KEY`) with fallback to Streamlit secrets
- ✅ Input validation: All user inputs validated before bias analysis
- ✅ Data portability: Hardcoded paths removed; uses environment variables or relative paths
- ✅ Data quality: Silent NaN coercion detected and warned; explicit missing value handling
- ⚠️ **Note:** This project processes user-supplied AI responses for analysis. While no data is stored, be cautious analyzing sensitive information in public deployments.

### **Code Organization Standards**
```
biaslense/
├── biaslense/              # Main package
│   ├── api/                # FastAPI REST endpoints with rate limiting
│   ├── src/core/           # Core bias detection and mitigation logic
│   ├── app/                # Streamlit web interface
│   ├── analysis/           # Empirical validation and calibration scripts
│   └── data/               # Reference datasets and embeddings
├── tests/                  # Unit and integration tests
├── results/                # Analysis outputs and calibration results
├── examples/               # Usage examples and tutorials
├── docs/                   # Extended documentation
└── ALGORITHM.md            # Full methodology and validation details
```

### **Configuration via Environment Variables**
```bash
# Bias detection settings
export BIAS_THRESHOLD=0.35              # Cosine similarity threshold for bias flagging
export MIN_CONFIDENCE_SCORE=2.5         # Minimum composite score to flag as "high risk"

# Data paths (for analysis scripts)
export RATER_DATA_DIR=~/projects/data/processed/
export BIASLENSE_OUTPUT_DIR=~/biaslense/results/

# API configuration (Railway/production)
export OPENAI_API_KEY=sk-...            # For improved response generation
export ENVIRONMENT=production
```

### **Dependency Security**
- All dependencies pinned to specific versions in `requirements.txt`
- No unnecessary dependencies; lean, production-ready stack
- Regular updates via `pip install --upgrade`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Citation

If you use BAMIP in your research, please cite:

```bibtex
@article{bamip2024,
  title={BAMIP: Bias-Aware Mitigation and Intervention Pipeline for AI-Generated Content},
  author={Your Name},
  journal={Conference/Journal Name},
  year={2024}
}
```

## 👨‍💻 Development & Contribution

### **Code Review Standards**
This codebase undergoes regular security and code quality reviews:

**Recent Improvements (v1.0.1):**
- Fixed REST API key handling for non-Streamlit environments (Railway, Docker)
- Replaced hardcoded absolute paths with environment variable support
- Added stable MD5 hashing for prompt ID generation (eliminates collision risk)
- Enhanced data quality validation (detects silent NaN coercion in CSV parsing)
- Documented configuration via environment variables

**Review Process:**
1. All PRs require code review and security audit
2. Type hints enforced with mypy/pyright
3. Tests must pass before merge
4. Pre-commit hooks check for security vulnerabilities

### **Running Analysis Scripts Locally**
```bash
# Set data paths for portability
export RATER_DATA_DIR=/path/to/rater/csvs
export BIASLENSE_OUTPUT_DIR=/path/to/output

# Run calibration pipeline
python biaslense/analysis/load_rater_data.py
python biaslense/analysis/compute_krippendorff.py
python biaslense/analysis/calibrate_multipliers.py
```

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/JaspreetSinghA/biaslense/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JaspreetSinghA/biaslense/discussions)
- **Email**: bamiPipeline@jaspreetahluwalia.com
- **Security Reports**: Please email security concerns directly; do not open public issues

## 🙏 Acknowledgments

- Research participants and community members who provided feedback
- OpenAI for API access enabling real-time bias analysis
- Streamlit team for the excellent web framework
- Academic reviewers and collaborators

---

**Made with ❤️ for bias-free AI**
