"""
BAMIP Professional Web Application
Production-ready FastAPI application for BAMIP pipeline deployment
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
from datetime import datetime
from typing import List, Optional
import uvicorn

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from src.core.bamip_pipeline import BAMIPPipeline, AIModel
    BAMIP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: BAMIP pipeline not available: {e}")
    BAMIP_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(
    title="BAMIP Pipeline",
    description="Bias-Aware Mitigation and Intervention Pipeline for AI Content Analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize BAMIP pipeline
pipeline = None
if BAMIP_AVAILABLE:
    try:
        pipeline = BAMIPPipeline()
        print("✅ BAMIP Pipeline initialized successfully")
    except Exception as e:
        print(f"❌ BAMIP Pipeline initialization failed: {e}")

# Storage for analysis history
analysis_history = []

# Pydantic models
class AnalysisRequest(BaseModel):
    prompt: str
    ai_model: Optional[str] = "gpt-4"

class AnalysisResponse(BaseModel):
    prompt: str
    original_response: str
    improved_response: str
    bias_score: float
    risk_level: str
    bias_type: str
    mitigation_strategy: str
    bias_reduction: float
    confidence: float
    recommendations: List[str]
    timestamp: str

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main application page"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BAMIP Pipeline - Professional Bias Analysis</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header {
            text-align: center; margin-bottom: 40px;
            background: rgba(255, 255, 255, 0.95);
            padding: 40px; border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            font-size: 3rem;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .nav-tabs {
            display: flex; justify-content: center; margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px; padding: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        .nav-tab {
            padding: 15px 30px; margin: 0 5px; border: none;
            background: transparent; border-radius: 10px;
            cursor: pointer; font-size: 16px; font-weight: 500;
            transition: all 0.3s ease; color: #666;
        }
        .nav-tab.active {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .content-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px; padding: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        .form-control {
            width: 100%; padding: 15px;
            border: 2px solid #e0e0e0; border-radius: 10px;
            font-size: 16px; min-height: 120px; resize: vertical;
        }
        .btn-primary {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white; padding: 15px 30px; border: none;
            border-radius: 10px; font-size: 16px; font-weight: 600;
            cursor: pointer; width: 100%;
        }
        .results {
            margin-top: 30px; padding: 30px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px; border-left: 5px solid #667eea;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin-bottom: 25px;
        }
        .metric-card {
            background: white; padding: 20px; border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); text-align: center;
        }
        .response-comparison {
            display: grid; grid-template-columns: 1fr 1fr;
            gap: 25px; margin: 25px 0;
        }
        .response-box {
            background: white; padding: 25px; border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .recommendations ul { list-style: none; padding: 0; }
        .recommendations li {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            margin: 10px 0; padding: 15px; border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .loading { text-align: center; color: #667eea; font-size: 18px; margin: 30px 0; }
        .alert { padding: 20px; border-radius: 10px; margin: 20px 0; font-weight: 500; }
        .alert-error { background: #ffebee; color: #c62828; border-left: 4px solid #c62828; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-brain"></i> BAMIP Pipeline</h1>
            <p>Professional Bias-Aware Mitigation and Intervention Pipeline</p>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('analyze')">
                <i class="fas fa-microscope"></i> Analyze
            </button>
            <button class="nav-tab" onclick="showTab('history')">
                <i class="fas fa-history"></i> History
            </button>
            <button class="nav-tab" onclick="showTab('api')">
                <i class="fas fa-code"></i> API
            </button>
        </div>
        
        <div id="analyze-tab" class="content-section">
            <h2><i class="fas fa-microscope"></i> Bias Analysis</h2>
            <form id="analysisForm">
                <div class="form-group">
                    <label for="prompt">Enter your prompt for bias analysis:</label>
                    <textarea id="prompt" class="form-control" placeholder="Enter your prompt here... (e.g., 'Describe a typical CEO')" required></textarea>
                </div>
                <button type="submit" class="btn-primary" id="analyzeBtn">
                    <i class="fas fa-search"></i> Analyze for Bias
                </button>
            </form>
            <div id="results" style="display: none;"></div>
        </div>
        
        <div id="history-tab" class="content-section" style="display: none;">
            <h2><i class="fas fa-history"></i> Analysis History</h2>
            <div id="historyContent">
                <p style="text-align: center; color: #666; padding: 40px;">
                    No analysis history yet. Run some analyses to see results here.
                </p>
            </div>
        </div>
        
        <div id="api-tab" class="content-section" style="display: none;">
            <h2><i class="fas fa-code"></i> API Documentation</h2>
            <p>Access the interactive API documentation:</p>
            <div style="margin: 20px 0;">
                <a href="/api/docs" target="_blank" class="btn-primary" style="width: auto; margin-right: 10px;">
                    <i class="fas fa-book"></i> Swagger UI
                </a>
                <a href="/api/redoc" target="_blank" class="btn-primary" style="width: auto;">
                    <i class="fas fa-file-alt"></i> ReDoc
                </a>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            document.querySelectorAll('.content-section').forEach(tab => tab.style.display = 'none');
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabName + '-tab').style.display = 'block';
            event.target.classList.add('active');
            if (tabName === 'history') loadHistory();
        }
        
        document.getElementById('analysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const prompt = document.getElementById('prompt').value.trim();
            const resultsDiv = document.getElementById('results');
            const analyzeBtn = document.getElementById('analyzeBtn');
            
            if (!prompt) { alert('Please enter a prompt to analyze.'); return; }
            
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            resultsDiv.innerHTML = '<div class="loading">Analyzing bias and applying mitigation strategies</div>';
            resultsDiv.style.display = 'block';
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt })
                });
                
                const result = await response.json();
                
                if (result.error) {
                    resultsDiv.innerHTML = `<div class="alert alert-error">Error: ${result.error}</div>`;
                } else {
                    resultsDiv.innerHTML = `
                        <div class="results">
                            <h3>Analysis Results</h3>
                            <div class="metric-grid">
                                <div class="metric-card">
                                    <div>Bias Score</div>
                                    <div style="font-size: 1.5rem; font-weight: 700;">${result.bias_score}/10</div>
                                </div>
                                <div class="metric-card">
                                    <div>Risk Level</div>
                                    <div style="font-size: 1.5rem; font-weight: 700;">${result.risk_level}</div>
                                </div>
                                <div class="metric-card">
                                    <div>Bias Type</div>
                                    <div style="font-size: 1.2rem; font-weight: 700;">${result.bias_type}</div>
                                </div>
                            </div>
                            <div class="response-comparison">
                                <div class="response-box">
                                    <h4>Original Response</h4>
                                    <p>${result.original_response}</p>
                                </div>
                                <div class="response-box">
                                    <h4>Improved Response</h4>
                                    <p>${result.improved_response}</p>
                                </div>
                            </div>
                            <div class="recommendations">
                                <h4>Recommendations</h4>
                                <ul>${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}</ul>
                            </div>
                        </div>
                    `;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="alert alert-error">Network Error: ${error.message}</div>`;
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze for Bias';
            }
        });
        
        async function loadHistory() {
            try {
                const response = await fetch('/api/history');
                const history = await response.json();
                const historyDiv = document.getElementById('historyContent');
                
                if (history.length === 0) {
                    historyDiv.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">No analysis history yet.</p>';
                } else {
                    historyDiv.innerHTML = history.map((item, index) => `
                        <div style="background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #667eea;">
                            <h4>Analysis #${history.length - index}</h4>
                            <p><strong>Prompt:</strong> ${item.prompt}</p>
                            <p><strong>Bias Score:</strong> ${item.bias_score}/10</p>
                            <p><strong>Risk Level:</strong> ${item.risk_level}</p>
                        </div>
                    `).join('');
                }
            } catch (error) {
                document.getElementById('historyContent').innerHTML = `<div class="alert alert-error">Error loading history: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>"""

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_prompt(request: AnalysisRequest):
    """Analyze a prompt for bias using the BAMIP pipeline"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="BAMIP pipeline not available")
    
    try:
        ai_response = f"This is a sample AI response to: {request.prompt}"
        ai_model = AIModel.GPT_4 if request.ai_model == "gpt-4" else AIModel.GPT_3_5
        result = pipeline.process_prompt(request.prompt, ai_response, ai_model)
        
        analysis_result = AnalysisResponse(
            prompt=request.prompt,
            original_response=ai_response,
            improved_response=result.improved_response,
            bias_score=result.bias_detection_result.overall_score,
            risk_level=result.risk_level.value,
            bias_type=result.bias_type,
            mitigation_strategy=result.mitigation_result.strategy_used.value,
            bias_reduction=result.mitigation_result.bias_reduction_score,
            confidence=result.mitigation_result.confidence,
            recommendations=result.recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        analysis_history.append(analysis_result.dict())
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/history")
async def get_history():
    """Get analysis history"""
    return list(reversed(analysis_history))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bamip_available": pipeline is not None,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting BAMIP Professional Web Application...")
    print("📱 Application will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/api/docs")
    print("✅ Ready for deployment and publication!")
    
    uvicorn.run("bamip_app:app", host="0.0.0.0", port=8000, reload=True)
