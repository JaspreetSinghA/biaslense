"""
BAMIP Flask Web Application - Alternative to Streamlit
Simple Flask-based web interface for BAMIP pipeline
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
import json

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from src.core.bamip_pipeline import BAMIPPipeline, AIModel
    print("✓ BAMIP imports successful")
except Exception as e:
    print(f"✗ BAMIP import error: {e}")

app = Flask(__name__)

# Initialize BAMIP pipeline
try:
    pipeline = BAMIPPipeline()
    print("✓ BAMIP pipeline initialized")
except Exception as e:
    print(f"✗ BAMIP pipeline initialization error: {e}")
    pipeline = None

# Store analysis history
analysis_history = []

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>BAMIP Pipeline</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #0e1117; color: #fafafa; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #1f77b4; text-align: center; }
            .nav { margin: 20px 0; text-align: center; }
            .nav a { margin: 0 15px; padding: 10px 20px; background: #1f77b4; color: white; text-decoration: none; border-radius: 5px; }
            .nav a:hover { background: #1a6aa0; }
            .section { margin: 30px 0; padding: 20px; background: #1e1e1e; border-radius: 8px; }
            textarea { width: 100%; height: 100px; padding: 10px; background: #2e2e2e; color: #fafafa; border: 1px solid #444; border-radius: 4px; }
            button { padding: 10px 20px; background: #1f77b4; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #1a6aa0; }
            .result { margin: 20px 0; padding: 15px; background: #2e2e2e; border-radius: 5px; }
            .error { background: #3d1a1a; color: #f8d7da; }
            .success { background: #1a3d1a; color: #d4edda; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 BAMIP Pipeline</h1>
            <p style="text-align: center; color: #a3a3a3;">Bias-Aware Mitigation and Intervention Pipeline</p>
            
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/test">🧪 Test BAMIP</a>
                <a href="/history">📜 History</a>
            </div>
            
            <div class="section">
                <h2>🔬 BAMIP Framework</h2>
                <p>The BAMIP (Bias-Aware Mitigation and Intervention Pipeline) framework implements a comprehensive two-layer methodology for detecting and mitigating bias in AI-generated content.</p>
                
                <h3>Two-Layer Detection Methodology</h3>
                <ul>
                    <li><strong>Layer 1: Bias Detection</strong>
                        <ul>
                            <li>Rubric-based scoring (Accuracy, Fairness, Representation, Neutrality, Relevance)</li>
                            <li>Embedding-based similarity to stereotype anchors</li>
                        </ul>
                    </li>
                    <li><strong>Layer 2: BAMIP Classification & Intervention</strong>
                        <ul>
                            <li>Bias type classification (Historical, Representational, Measurement, Aggregation, Evaluation)</li>
                            <li>Strategy selection and mitigation application</li>
                        </ul>
                    </li>
                </ul>
                
                <h3>Mitigation Strategies</h3>
                <ul>
                    <li><strong>Instructional Prompting</strong> - Clear, explicit instructions to avoid bias</li>
                    <li><strong>Contextual Reframing</strong> - Reframe prompts to encourage balanced perspectives</li>
                    <li><strong>Retrieval-Based Grounding</strong> - Provide factual grounding with trusted sources</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/test')
def test_page():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test BAMIP - BAMIP Pipeline</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #0e1117; color: #fafafa; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #1f77b4; text-align: center; }
            .nav { margin: 20px 0; text-align: center; }
            .nav a { margin: 0 15px; padding: 10px 20px; background: #1f77b4; color: white; text-decoration: none; border-radius: 5px; }
            .nav a:hover { background: #1a6aa0; }
            .section { margin: 30px 0; padding: 20px; background: #1e1e1e; border-radius: 8px; }
            textarea { width: 100%; height: 100px; padding: 10px; background: #2e2e2e; color: #fafafa; border: 1px solid #444; border-radius: 4px; }
            button { padding: 10px 20px; background: #1f77b4; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #1a6aa0; }
            .result { margin: 20px 0; padding: 15px; background: #2e2e2e; border-radius: 5px; }
            .error { background: #3d1a1a; color: #f8d7da; }
            .success { background: #1a3d1a; color: #d4edda; }
            #results { display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 Test BAMIP Pipeline</h1>
            
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/test">🧪 Test BAMIP</a>
                <a href="/history">📜 History</a>
            </div>
            
            <div class="section">
                <h2>Enter Prompt for Bias Analysis</h2>
                <form id="biasForm">
                    <textarea id="prompt" placeholder="Enter your prompt here..." required></textarea>
                    <br><br>
                    <button type="submit">🔍 Analyze for Bias</button>
                </form>
                
                <div id="results" class="result">
                    <h3>📊 Analysis Results</h3>
                    <div id="resultContent"></div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('biasForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const prompt = document.getElementById('prompt').value;
                const resultsDiv = document.getElementById('results');
                const contentDiv = document.getElementById('resultContent');
                
                if (!prompt.trim()) {
                    alert('Please enter a prompt to analyze.');
                    return;
                }
                
                contentDiv.innerHTML = '<p>🔄 Analyzing bias and applying mitigation...</p>';
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
                        contentDiv.innerHTML = `<div class="error">❌ Error: ${result.error}</div>`;
                    } else {
                        contentDiv.innerHTML = `
                            <div class="success">✅ Analysis Complete</div>
                            <p><strong>Bias Score:</strong> ${result.bias_score}/10</p>
                            <p><strong>Risk Level:</strong> ${result.risk_level}</p>
                            <p><strong>Bias Type:</strong> ${result.bias_type}</p>
                            <p><strong>Mitigation Strategy:</strong> ${result.mitigation_strategy}</p>
                            <p><strong>Original Response:</strong> ${result.original_response}</p>
                            <p><strong>Improved Response:</strong> ${result.improved_response}</p>
                        `;
                    }
                } catch (error) {
                    contentDiv.innerHTML = `<div class="error">❌ Network Error: ${error.message}</div>`;
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'})
        
        if not pipeline:
            return jsonify({'error': 'BAMIP pipeline not initialized'})
        
        # Generate a simple AI response (you can integrate OpenAI here)
        ai_response = f"This is a sample AI response to: {prompt}"
        
        # Process through BAMIP pipeline
        result = pipeline.process_prompt(prompt, ai_response, AIModel.GPT_4)
        
        # Store in history
        analysis_data = {
            'prompt': prompt,
            'original_response': ai_response,
            'improved_response': result.improved_response,
            'bias_score': result.bias_detection_result.overall_score,
            'risk_level': result.risk_level.value,
            'mitigation_strategy': result.mitigation_result.strategy_used.value,
            'bias_type': result.mitigation_result.bias_type,
        }
        analysis_history.append(analysis_data)
        
        return jsonify(analysis_data)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/history')
def history():
    history_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>History - BAMIP Pipeline</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #0e1117; color: #fafafa; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #1f77b4; text-align: center; }
            .nav { margin: 20px 0; text-align: center; }
            .nav a { margin: 0 15px; padding: 10px 20px; background: #1f77b4; color: white; text-decoration: none; border-radius: 5px; }
            .nav a:hover { background: #1a6aa0; }
            .section { margin: 30px 0; padding: 20px; background: #1e1e1e; border-radius: 8px; }
            .history-item { margin: 20px 0; padding: 15px; background: #2e2e2e; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📜 Analysis History</h1>
            
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/test">🧪 Test BAMIP</a>
                <a href="/history">📜 History</a>
            </div>
            
            <div class="section">
    '''
    
    if not analysis_history:
        history_html += '<p>No analysis history yet. Test some prompts on the Test BAMIP page to see results here.</p>'
    else:
        for i, analysis in enumerate(reversed(analysis_history)):
            history_html += f'''
                <div class="history-item">
                    <h3>Analysis #{len(analysis_history) - i}</h3>
                    <p><strong>Prompt:</strong> {analysis['prompt']}</p>
                    <p><strong>Bias Score:</strong> {analysis['bias_score']}/10</p>
                    <p><strong>Risk Level:</strong> {analysis['risk_level']}</p>
                    <p><strong>Bias Type:</strong> {analysis['bias_type']}</p>
                    <p><strong>Mitigation Strategy:</strong> {analysis['mitigation_strategy']}</p>
                    <p><strong>Improved Response:</strong> {analysis['improved_response']}</p>
                </div>
            '''
    
    history_html += '''
            </div>
        </div>
    </body>
    </html>
    '''
    
    return history_html

if __name__ == '__main__':
    print("🧠 Starting BAMIP Flask Application...")
    print("📱 Opening web application on http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
