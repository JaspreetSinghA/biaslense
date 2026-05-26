#!/usr/bin/env python3
"""
BAMIP Web Interface - Simple HTTP Server
Direct web interface for BAMIP pipeline that bypasses Streamlit issues
"""

import http.server
import socketserver
import json
import urllib.parse
import sys
import os
from datetime import datetime

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.core.bamip_pipeline import BAMIPPipeline, AIModel

# Initialize BAMIP pipeline
try:
    pipeline = BAMIPPipeline()
    print("✓ BAMIP pipeline initialized successfully")
except Exception as e:
    print(f"✗ BAMIP pipeline initialization failed: {e}")
    pipeline = None

# Store analysis history
analysis_history = []

class BAMIPHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>BAMIP Pipeline - Bias Detection & Mitigation</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 100%);
            color: #fafafa;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { 
            font-size: 3rem; 
            background: linear-gradient(45deg, #1f77b4, #4fc3f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .header p { font-size: 1.2rem; color: #a3a3a3; }
        
        .nav { 
            display: flex; 
            justify-content: center; 
            gap: 20px; 
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        .nav-btn { 
            padding: 12px 24px; 
            background: linear-gradient(45deg, #1f77b4, #1565c0);
            color: white; 
            text-decoration: none; 
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        .nav-btn:hover { 
            background: linear-gradient(45deg, #1565c0, #0d47a1);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3);
        }
        .nav-btn.active { 
            background: linear-gradient(45deg, #4fc3f7, #29b6f6);
        }
        
        .section { 
            background: rgba(30, 30, 30, 0.8);
            padding: 30px; 
            border-radius: 12px; 
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .section h2 { 
            color: #4fc3f7; 
            margin-bottom: 20px; 
            font-size: 1.8rem;
        }
        .section h3 { 
            color: #81c784; 
            margin: 20px 0 10px 0; 
            font-size: 1.3rem;
        }
        
        .form-group { margin-bottom: 20px; }
        .form-group label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 500;
            color: #e0e0e0;
        }
        textarea { 
            width: 100%; 
            min-height: 120px; 
            padding: 15px; 
            background: rgba(46, 46, 46, 0.8);
            color: #fafafa; 
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            font-size: 16px;
            resize: vertical;
            transition: border-color 0.3s ease;
        }
        textarea:focus { 
            outline: none;
            border-color: #4fc3f7;
            box-shadow: 0 0 0 3px rgba(79, 195, 247, 0.1);
        }
        
        .analyze-btn { 
            background: linear-gradient(45deg, #4caf50, #66bb6a);
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
        }
        .analyze-btn:hover { 
            background: linear-gradient(45deg, #388e3c, #4caf50);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        }
        .analyze-btn:disabled { 
            background: #555; 
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .results { 
            margin-top: 30px; 
            padding: 25px; 
            background: rgba(46, 46, 46, 0.6);
            border-radius: 8px;
            border-left: 4px solid #4fc3f7;
        }
        .results h3 { color: #4fc3f7; margin-bottom: 15px; }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            margin: 10px 0;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .metric:last-child { border-bottom: none; }
        .metric-label { font-weight: 500; }
        .metric-value { 
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
        }
        .risk-low { background: rgba(76, 175, 80, 0.2); color: #81c784; }
        .risk-medium { background: rgba(255, 193, 7, 0.2); color: #ffb74d; }
        .risk-high { background: rgba(244, 67, 54, 0.2); color: #e57373; }
        
        .response-comparison { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 20px; 
            margin-top: 20px;
        }
        @media (max-width: 768px) {
            .response-comparison { grid-template-columns: 1fr; }
        }
        .response-box { 
            background: rgba(30, 30, 30, 0.8);
            padding: 20px; 
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .response-box h4 { 
            color: #4fc3f7; 
            margin-bottom: 10px; 
        }
        
        .recommendations { 
            margin-top: 20px;
        }
        .recommendations ul { 
            list-style: none; 
            padding: 0;
        }
        .recommendations li { 
            background: rgba(79, 195, 247, 0.1);
            margin: 8px 0; 
            padding: 12px 15px; 
            border-radius: 6px;
            border-left: 3px solid #4fc3f7;
        }
        .recommendations li:before { 
            content: "💡 "; 
            margin-right: 8px;
        }
        
        .loading { 
            text-align: center; 
            color: #4fc3f7;
            font-size: 18px;
            margin: 20px 0;
        }
        .loading:after {
            content: '';
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #4fc3f7;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .error { 
            background: rgba(244, 67, 54, 0.1);
            color: #e57373; 
            padding: 15px; 
            border-radius: 8px;
            border-left: 4px solid #f44336;
            margin: 20px 0;
        }
        .success { 
            background: rgba(76, 175, 80, 0.1);
            color: #81c784; 
            padding: 15px; 
            border-radius: 8px;
            border-left: 4px solid #4caf50;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 BAMIP Pipeline</h1>
            <p>Bias-Aware Mitigation and Intervention Pipeline</p>
        </div>
        
        <div class="nav">
            <button class="nav-btn active" onclick="showSection('home')">🏠 Home</button>
            <button class="nav-btn" onclick="showSection('test')">🧪 Test BAMIP</button>
            <button class="nav-btn" onclick="showSection('history')">📜 History</button>
        </div>
        
        <div id="home-section" class="section">
            <h2>🔬 BAMIP Framework</h2>
            <p>The BAMIP (Bias-Aware Mitigation and Intervention Pipeline) framework implements a comprehensive two-layer methodology for detecting and mitigating bias in AI-generated content.</p>
            
            <h3>Two-Layer Detection Methodology</h3>
            <ul style="margin-left: 20px; line-height: 1.6;">
                <li><strong>Layer 1: Bias Detection</strong>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li>Rubric-based scoring (Accuracy, Fairness, Representation, Neutrality, Relevance)</li>
                        <li>Embedding-based similarity to stereotype anchors</li>
                    </ul>
                </li>
                <li><strong>Layer 2: BAMIP Classification & Intervention</strong>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li>Bias type classification (Historical, Representational, Measurement, Aggregation, Evaluation)</li>
                        <li>Strategy selection and mitigation application</li>
                    </ul>
                </li>
            </ul>
            
            <h3>Mitigation Strategies</h3>
            <ul style="margin-left: 20px; line-height: 1.6;">
                <li><strong>Instructional Prompting</strong> - Clear, explicit instructions to avoid bias</li>
                <li><strong>Contextual Reframing</strong> - Reframe prompts to encourage balanced perspectives</li>
                <li><strong>Retrieval-Based Grounding</strong> - Provide factual grounding with trusted sources</li>
            </ul>
        </div>
        
        <div id="test-section" class="section" style="display: none;">
            <h2>🧪 Test BAMIP Pipeline</h2>
            <div class="form-group">
                <label for="prompt">Enter your prompt for bias analysis:</label>
                <textarea id="prompt" placeholder="Enter your prompt here... (e.g., 'Describe a typical CEO')"></textarea>
            </div>
            <button class="analyze-btn" onclick="analyzePrompt()">🔍 Analyze for Bias</button>
            
            <div id="results" style="display: none;"></div>
        </div>
        
        <div id="history-section" class="section" style="display: none;">
            <h2>📜 Analysis History</h2>
            <div id="history-content">
                <p style="color: #a3a3a3; text-align: center; padding: 40px;">No analysis history yet. Test some prompts to see results here.</p>
            </div>
        </div>
    </div>
    
    <script>
        function showSection(section) {
            // Hide all sections
            document.getElementById('home-section').style.display = 'none';
            document.getElementById('test-section').style.display = 'none';
            document.getElementById('history-section').style.display = 'none';
            
            // Remove active class from all nav buttons
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            
            // Show selected section and activate button
            document.getElementById(section + '-section').style.display = 'block';
            event.target.classList.add('active');
            
            // Load history if history section is selected
            if (section === 'history') {
                loadHistory();
            }
        }
        
        async function analyzePrompt() {
            const prompt = document.getElementById('prompt').value.trim();
            const resultsDiv = document.getElementById('results');
            const analyzeBtn = document.querySelector('.analyze-btn');
            
            if (!prompt) {
                alert('Please enter a prompt to analyze.');
                return;
            }
            
            // Show loading state
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = '🔄 Analyzing...';
            resultsDiv.innerHTML = '<div class="loading">Analyzing bias and applying mitigation</div>';
            resultsDiv.style.display = 'block';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt: prompt })
                });
                
                const result = await response.json();
                
                if (result.error) {
                    resultsDiv.innerHTML = `<div class="error">❌ Error: ${result.error}</div>`;
                } else {
                    displayResults(result);
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">❌ Network Error: ${error.message}</div>`;
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = '🔍 Analyze for Bias';
            }
        }
        
        function displayResults(result) {
            const riskClass = result.risk_level.toLowerCase();
            const resultsHTML = `
                <div class="results">
                    <h3>📊 Bias Analysis Results</h3>
                    
                    <div class="metric">
                        <span class="metric-label">Bias Score:</span>
                        <span class="metric-value">${result.bias_score}/10</span>
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">Risk Level:</span>
                        <span class="metric-value risk-${riskClass}">${result.risk_level.toUpperCase()}</span>
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">Bias Type:</span>
                        <span class="metric-value">${result.bias_type}</span>
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">Mitigation Strategy:</span>
                        <span class="metric-value">${result.mitigation_strategy.replace(/_/g, ' ')}</span>
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">Bias Reduction:</span>
                        <span class="metric-value">${(result.bias_reduction * 100).toFixed(1)}%</span>
                    </div>
                    
                    <div class="response-comparison">
                        <div class="response-box">
                            <h4>💬 Original Response</h4>
                            <p>${result.original_response}</p>
                        </div>
                        <div class="response-box">
                            <h4>✨ Improved Response</h4>
                            <p>${result.improved_response}</p>
                        </div>
                    </div>
                    
                    <div class="recommendations">
                        <h4>📋 Recommendations</h4>
                        <ul>
                            ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
            
            document.getElementById('results').innerHTML = resultsHTML;
        }
        
        async function loadHistory() {
            try {
                const response = await fetch('/history');
                const history = await response.json();
                
                const historyDiv = document.getElementById('history-content');
                
                if (history.length === 0) {
                    historyDiv.innerHTML = '<p style="color: #a3a3a3; text-align: center; padding: 40px;">No analysis history yet. Test some prompts to see results here.</p>';
                } else {
                    const historyHTML = history.map((item, index) => `
                        <div class="response-box" style="margin-bottom: 20px;">
                            <h4>Analysis #${history.length - index}</h4>
                            <div class="metric">
                                <span class="metric-label">Prompt:</span>
                                <span>${item.prompt}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Bias Score:</span>
                                <span>${item.bias_score}/10</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Risk Level:</span>
                                <span class="risk-${item.risk_level.toLowerCase()}">${item.risk_level}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Improved Response:</span>
                                <span>${item.improved_response}</span>
                            </div>
                        </div>
                    `).join('');
                    
                    historyDiv.innerHTML = historyHTML;
                }
            } catch (error) {
                document.getElementById('history-content').innerHTML = `<div class="error">Error loading history: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
            '''
            
            self.wfile.write(html_content.encode())
            
        elif self.path == '/analyze':
            # This will be handled by do_POST
            pass
        elif self.path == '/history':
            # This will be handled by do_POST
            pass
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/analyze':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                prompt = data.get('prompt', '')
                
                if not prompt:
                    self.send_json_response({'error': 'No prompt provided'})
                    return
                
                if not pipeline:
                    self.send_json_response({'error': 'BAMIP pipeline not initialized'})
                    return
                
                # Generate a simple AI response (you can integrate OpenAI here)
                ai_response = f"This is a sample AI response to: {prompt}"
                
                # Process through BAMIP pipeline
                result = pipeline.process_prompt(prompt, ai_response, AIModel.GPT_4)
                
                # Prepare response data
                response_data = {
                    'prompt': prompt,
                    'original_response': ai_response,
                    'improved_response': result.improved_response,
                    'bias_score': result.bias_detection_result.overall_score,
                    'risk_level': result.risk_level.value,
                    'mitigation_strategy': result.mitigation_result.strategy_used.value,
                    'bias_type': result.bias_type,
                    'bias_reduction': result.mitigation_result.bias_reduction_score,
                    'recommendations': result.recommendations,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Store in history
                analysis_history.append(response_data)
                
                self.send_json_response(response_data)
                
            except Exception as e:
                self.send_json_response({'error': str(e)})
        
        elif self.path == '/history':
            self.send_json_response(list(reversed(analysis_history)))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    PORT = 8080
    
    print("🧠 Starting BAMIP Web Interface...")
    print(f"📱 Opening web application on http://localhost:{PORT}")
    print("✅ BAMIP pipeline ready for bias analysis!")
    
    with socketserver.TCPServer(("", PORT), BAMIPHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 BAMIP Web Interface stopped")
