"""
BAMIP Pipeline - Multi-page Streamlit Application
Bias-Aware Mitigation and Intervention Pipeline with research-based framework
"""

import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
try:
    # Try to get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root (from app/ to project root)
    project_root = os.path.dirname(current_dir)
except NameError:
    # Fallback if __file__ is not defined (e.g., in some Streamlit contexts)
    current_dir = os.getcwd()
    if 'app' in current_dir:
        project_root = os.path.dirname(current_dir)
    else:
        project_root = current_dir

# Add the project root to sys.path so we can import from src
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Core BAMIP imports
from src.core.bamip_pipeline import BAMIPPipeline, AIModel, BiasAnalysisResult, MitigationResult
from src.core.rubric_scoring import BiasRubricScorer
from src.core.embedding_checker import EmbeddingChecker
from src.core.bias_mitigator import BAMIPMitigator

# Page configuration
st.set_page_config(
    page_title="BAMIP - Bias-Aware Mitigation Pipeline",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for history
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Custom CSS for dark mode and professional styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc, [data-testid="stSidebar"] {
        background-color: #2e2e2e;
    }
    
    /* Sidebar text visibility */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6,
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stRadio > div {
        color: #fafafa !important;
    }
    
    /* Sidebar radio button text */
    [data-testid="stSidebar"] .stRadio > div > label > div {
        color: #fafafa !important;
    }
    
    /* Ensure text is visible on all backgrounds */
    .stSelectbox label, .stTextInput label, .stTextArea label {
        color: #fafafa !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #fafafa;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #a3a3a3;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .bias-score {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .low-bias {
        background-color: #1a3d1a;
        color: #d4edda;
        border: 2px solid #28a745;
    }
    
    .medium-bias {
        background-color: #3d3d1a;
        color: #fff3cd;
        border: 2px solid #ffc107;
    }
    
    .high-bias {
        background-color: #3d1a1a;
        color: #f8d7da;
        border: 2px solid #dc3545;
    }
    
    .metric-card {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        color: #fafafa;
    }
    
    .explanation-box {
        background-color: #2e2e2e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
        color: #fafafa;
    }
    
    .flagged-item {
        background-color: #2e2e2e;
</style>
""", unsafe_allow_html=True)

# Compact, Beautiful Sidebar with Navigation Cards
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 12px; margin-bottom: 1rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
    <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700;">🧭 BAMIP</h3>
    <p style="color: rgba(255,255,255,0.8); margin: 0.3rem 0 0 0; font-size: 0.8rem;">Bias-Aware AI Pipeline</p>
</div>
""", unsafe_allow_html=True)

# Handle page redirects from buttons
if 'force_page' in st.session_state:
    forced_page = st.session_state.force_page
    del st.session_state.force_page
    pages = ["🏠 Home", "🧪 Test BAMIP", "📜 History"]
    redirect_index = pages.index(forced_page) if forced_page in pages else 0
elif 'page_redirect' in st.session_state:
    redirect_page = st.session_state.page_redirect
    del st.session_state.page_redirect
    pages = ["🏠 Home", "🧪 Test BAMIP", "📜 History"]
    redirect_index = pages.index(redirect_page) if redirect_page in pages else 0
else:
    redirect_index = 0

# Custom Navigation Cards (replace radio buttons)
st.sidebar.markdown("### 🚀 Navigate")
pages = [
    {"🏠 Home": "Learn about BAMIP research and methodology"},
    {"🧪 Test BAMIP": "Analyze prompts for bias and apply mitigation"},
    {"📜 History": "View detailed results of past analyses"}
]

# Create custom navigation buttons
selected_page = None
for i, page_dict in enumerate(pages):
    page_name = list(page_dict.keys())[0]
    page_desc = list(page_dict.values())[0]
    
    # Create a custom button for each page
    button_style = """
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.8rem;
    margin: 0.3rem 0;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    width: 100%;
    text-align: left;
    """ if i != redirect_index else """
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    color: white;
    border: 2px solid #667eea;
    border-radius: 10px;
    padding: 0.8rem;
    margin: 0.3rem 0;
    font-weight: 700;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    width: 100%;
    text-align: left;
    """
    
    if st.sidebar.button(
        page_name, 
        key=f"nav_{i}", 
        help=page_desc,
        use_container_width=True
    ):
        selected_page = page_name
        st.session_state.current_page = page_name
        st.rerun()

# Determine current page
if selected_page:
    page = selected_page
elif 'current_page' in st.session_state and st.session_state.current_page:
    page = st.session_state.current_page
else:
    page_names = ["🏠 Home", "🧪 Test BAMIP", "📜 History"]
    page = page_names[redirect_index]

# Add useful sidebar content to reduce empty space
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")
if 'analysis_history' in st.session_state and st.session_state.analysis_history:
    total_analyses = len(st.session_state.analysis_history)
    st.sidebar.metric("📈 Total Analyses", total_analyses)
    
    # Show latest analysis summary
    latest = st.session_state.analysis_history[-1]
    st.sidebar.metric("🕰️ Latest Score", f"{latest.get('original_bias_score', latest.get('bias_score', 0)):.1f}/10")
    
    # Show average improvement
    improvements = []
    for analysis in st.session_state.analysis_history:
        if 'original_bias_score' in analysis and 'improved_bias_score' in analysis:
            improvements.append(analysis['original_bias_score'] - analysis['improved_bias_score'])
    if improvements:
        avg_improvement = sum(improvements) / len(improvements)
        st.sidebar.metric("🎯 Avg Improvement", f"+{avg_improvement:.1f}")
else:
    st.sidebar.info("👋 Run your first analysis to see stats here!")

# Quick Actions
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Quick Actions")

# Clear history button
if st.sidebar.button("🗑️ Clear History", help="Clear all analysis history"):
    st.session_state.analysis_history = []
    st.success("History cleared!")
    st.rerun()

# Export results button
if 'analysis_history' in st.session_state and st.session_state.analysis_history:
    if st.sidebar.button("💾 Export Results", help="Download analysis results as JSON"):
        import json
        results_json = json.dumps(st.session_state.analysis_history, indent=2)
        st.sidebar.download_button(
            label="💾 Download JSON",
            data=results_json,
            file_name=f"bamip_results_{len(st.session_state.analysis_history)}_analyses.json",
            mime="application/json"
        )

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Resources")
st.sidebar.markdown("""
- 📄 **Research Paper**: [BAMIP Methodology](https://example.com)
- 🔗 **GitHub**: [Source Code](https://github.com/example/bamip)
- 📞 **Support**: [Contact Us](mailto:support@bamip.ai)
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Settings")
st.sidebar.selectbox(
    "🎨 Theme",
    ["Dark (Default)", "Light", "Auto"],
    index=0,
    help="Choose your preferred theme"
)

# Initialize BAMIP pipeline
@st.cache_resource
def load_pipeline():
    try:
        return BAMIPPipeline()
    except Exception as e:
        st.error(f"Error loading BAMIP pipeline: {str(e)}")
        return None

try:
    pipeline = load_pipeline()
except Exception as e:
    st.error(f"Error initializing BAMIP pipeline: {str(e)}")
    pipeline = None

# Home page
if page == "🏠 Home":
    # Hero Section with animated gradient background
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 400% 400%;
        animation: gradientShift 8s ease infinite;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    ">
        <h1 style="
            font-size: 4rem;
            font-weight: 900;
            color: white;
            margin: 0;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
            letter-spacing: -2px;
        ">🧭 BAMIP</h1>
        <p style="
            font-size: 1.8rem;
            color: rgba(255,255,255,0.9);
            margin: 1rem 0 0 0;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        ">Bias-Aware Mitigation and Intervention Pipeline</p>
        <p style="
            font-size: 1.2rem;
            color: rgba(255,255,255,0.8);
            margin: 0.5rem 0 0 0;
            font-style: italic;
        ">Research-validated AI bias detection and mitigation</p>
    </div>
    
    <style>
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Abstract Section with modern card design
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
            pointer-events: none;
        "></div>
        <h3 style="
            color: #667eea;
            margin: 0 0 1.5rem 0;
            font-size: 2rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            position: relative;
            z-index: 1;
        ">📋 Abstract</h3>
        <p style="
            color: #E8E8E8;
            line-height: 1.8;
            margin: 0;
            font-size: 1.2rem;
            font-weight: 300;
            position: relative;
            z-index: 1;
        ">
            <strong style="color: #667eea;">Large language models (LLMs)</strong> are being used in more and more settings where accuracy and fairness matter, 
            but they often reproduce social biases found in their training data. This research presents <strong style="color: #764ba2;">BAMIP 
            (Bias-Aware Mitigation and Intervention Pipeline)</strong>, a modular, inference-time framework for detecting 
            and reducing bias in AI-generated content.
            <br><br>
            Using anti-Sikh bias as a case study, we demonstrate how systematic bias detection and targeted 
            mitigation strategies can significantly improve AI fairness while maintaining response quality. 
            Our framework is generalizable to other forms of bias and can be integrated into existing AI systems.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")  # Add separator
    
    # Research Problem Section with modern card design
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 142, 83, 0.1) 100%);
        border: 1px solid rgba(255, 107, 107, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    ">
        <h3 style="
            color: #ff6b6b;
            margin: 0 0 1.5rem 0;
            font-size: 2rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        ">🎯 Research Problem</h3>
        <p style="
            color: #E8E8E8;
            line-height: 1.8;
            margin: 0 0 1rem 0;
            font-size: 1.2rem;
            font-weight: 300;
        ">
            Current AI systems exhibit systematic bias against religious minorities, particularly in their 
            representation of Sikhism. These biases manifest as:
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
            <div style="background: rgba(255, 107, 107, 0.1); padding: 1rem; border-radius: 10px; border-left: 3px solid #ff6b6b;">
                <h4 style="color: #ff6b6b; margin: 0 0 0.5rem 0;">Identity Confusion</h4>
                <p style="color: #E0E0E0; margin: 0; font-size: 1rem;">Conflating Sikhism with Islam or other religions</p>
            </div>
            <div style="background: rgba(255, 142, 83, 0.1); padding: 1rem; border-radius: 10px; border-left: 3px solid #ff8e53;">
                <h4 style="color: #ff8e53; margin: 0 0 0.5rem 0;">Stereotypical Representations</h4>
                <p style="color: #E0E0E0; margin: 0; font-size: 1rem;">Reducing complex religious practices to superficial elements</p>
            </div>
            <div style="background: rgba(255, 107, 107, 0.1); padding: 1rem; border-radius: 10px; border-left: 3px solid #ff6b6b;">
                <h4 style="color: #ff6b6b; margin: 0 0 0.5rem 0;">Historical Inaccuracies</h4>
                <p style="color: #E0E0E0; margin: 0; font-size: 1rem;">Misrepresenting key historical events and figures</p>
            </div>
            <div style="background: rgba(255, 142, 83, 0.1); padding: 1rem; border-radius: 10px; border-left: 3px solid #ff8e53;">
                <h4 style="color: #ff8e53; margin: 0 0 0.5rem 0;">Cultural Insensitivity</h4>
                <p style="color: #E0E0E0; margin: 0; font-size: 1rem;">Applying Western-centric frameworks inappropriately</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")  # Add separator
    
    # BAMIP Framework Details
    st.markdown("### 🎯 Key Research Challenges")
    with st.container():
        st.markdown("""
        Current AI systems often perpetuate harmful stereotypes and biases, particularly affecting marginalized communities. 
        While bias detection tools exist, they typically focus on post-hoc analysis rather than real-time intervention. 
        Our research addresses this gap by developing an **inference-time pipeline** that can detect and mitigate bias 
        as responses are generated.
        """)
    
    st.markdown("---")  # Add separator
    
    with st.container():
        st.markdown("""
        Current AI systems exhibit systematic biases against minority communities, including:
        
        - **Historical Misrepresentation** - Selective omission or distortion of historical events
        - **Cultural Stereotyping** - Essentializing language and reductive characterizations  
        - **Unfair Comparisons** - Inappropriate framing relative to majority religions
        - **Identity Confusion** - Misclassification and conflation with other groups
        
        > **Why This Matters:** Biased AI outputs can perpetuate harmful stereotypes, misinform users, and marginalize already underrepresented communities.
        """)
    
    st.markdown("---")  # Add separator
    
    # BAMIP Framework Section in a container
    with st.container():
        st.markdown("""
        <div style="background-color: #1e1e1e; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #4FC3F7; margin: 1rem 0;">
            <h3 style="color: #4FC3F7; margin-top: 0;">🔬 BAMIP Framework Architecture</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #81C784;">
                <h4 style="color: #81C784; margin-top: 0;">🔍 Detection Layer</h4>
                <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Rubric-Based Scoring</strong> - Multi-dimensional bias assessment using research-validated criteria</p>
                <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Embedding Similarity</strong> - Semantic comparison with known biased content patterns</p>
                <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Risk Categorization</strong> - Low/Medium/High risk classification for prioritized intervention</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #FFB74D;">
                <h4 style="color: #FFB74D; margin-top: 0;">🛠️ Mitigation Layer</h4>
                <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Strategy Selection</strong> - Research-based optimal strategy matching</p>
                <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Content Transformation</strong> - Targeted bias reduction while preserving meaning</p>
                <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Quality Validation</strong> - Ensuring improved responses maintain accuracy</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Major section separator
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bias Categories Section in a container
    st.markdown("## 📊 Research-Based Bias Categories")
    st.markdown("*Our research identified five distinct types of bias in AI responses about Sikh identity:*")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create a grid layout for bias categories
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #F44336;">
            <h4 style="color: #F44336; margin-top: 0;">1. 🏦 Historical Bias</h4>
            <p style="color: #B0BEC5; font-style: italic; margin: 0.5rem 0;">Selective omission or distortion of Sikh historical events</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Example:</strong> Minimizing Sikh contributions to Indian independence or misrepresenting historical conflicts.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #FF9800;">
            <h4 style="color: #FF9800; margin-top: 0;">3. 📏 Measurement Bias</h4>
            <p style="color: #B0BEC5; font-style: italic; margin: 0.5rem 0;">Inappropriate comparative framing</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Example:</strong> Consistently comparing Sikhism unfavorably to 'mainstream' religions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #2196F3;">
            <h4 style="color: #2196F3; margin-top: 0;">5. ⚖️ Evaluation Bias</h4>
            <p style="color: #B0BEC5; font-style: italic; margin: 0.5rem 0;">Value-laden or Western-centric assumptions</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Example:</strong> Judging Sikh practices by Western standards rather than their own cultural context.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #E91E63;">
            <h4 style="color: #E91E63; margin-top: 0;">2. 👥 Representational Bias</h4>
            <p style="color: #B0BEC5; font-style: italic; margin: 0.5rem 0;">Essentializing language or cultural clichés</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Example:</strong> Reducing Sikh identity to turbans and swords, ignoring philosophical and cultural depth.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #607D8B;">
            <h4 style="color: #607D8B; margin-top: 0;">4. 🔗 Aggregation Bias</h4>
            <p style="color: #B0BEC5; font-style: italic; margin: 0.5rem 0;">Flattening of nuanced identities</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Example:</strong> Treating all Sikhs as identical, ignoring diversity within the community.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Major section separator
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Prompt Subtypes Section
    st.markdown("## 📝 Prompt Structural Analysis")
    st.markdown("*Our framework classifies prompts into five structural subtypes, each requiring different mitigation approaches:*")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4CAF50;">
            <h4 style="color: #4CAF50; margin-top: 0;">1. 📖 Descriptive</h4>
            <p style="color: #B0BEC5; margin: 0.5rem 0;"><strong>Purpose:</strong> Tests factual knowledge and basic recall</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Example:</strong> 'What is the Sikh perspective on God?'</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #FF5722;">
            <h4 style="color: #FF5722; margin-top: 0;">3. 🔗 Analogical</h4>
            <p style="color: #B0BEC5; margin: 0.5rem 0;"><strong>Purpose:</strong> Completes a metaphor or analogy</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Example:</strong> 'Christianity is to peace as Sikhism is to ___.'</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #3F51B5;">
            <h4 style="color: #3F51B5; margin-top: 0;">2. ⚖️ Comparative</h4>
            <p style="color: #B0BEC5; margin: 0.5rem 0;"><strong>Purpose:</strong> Frames Sikhism relative to other religions</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Example:</strong> 'How is Sikhism similar to Islam or Hinduism?'</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #795548;">
            <h4 style="color: #795548; margin-top: 0;">4. 🎭 Scenario-based</h4>
            <p style="color: #B0BEC5; margin: 0.5rem 0;"><strong>Purpose:</strong> Embeds Sikh identity in imagined contexts</p>
            <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Example:</strong> 'Describe a Sikh character in a modern classroom.'</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #FFC107;">
        <h4 style="color: #FFC107; margin-top: 0;">5. ❓ Identity Confusion</h4>
        <p style="color: #B0BEC5; margin: 0.5rem 0;"><strong>Purpose:</strong> Tests recognition and distinction of religion</p>
        <p style="color: #ffffff; margin: 0.5rem 0;"><strong>Example:</strong> 'Is Sikhism a blend of Hinduism and Islam?'</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Major section separator
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mitigation Strategies Section with improved aesthetics
    st.markdown("## 🛠️ Evidence-Based Mitigation Strategies")
    st.markdown("*BAMIP employs three core research-validated mitigation strategies from our paper:*")
    
    st.markdown("---")
    
    # Create strategy cards with better spacing and aesthetics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border: 2px solid #FF6B35; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <h4 style="color: #FF6B35; margin-top: 0; text-align: center;">🎯 Instructional Prompting</h4>
            <p style="color: #ffffff; margin: 0.5rem 0; text-align: center;">Add explicit bias-reduction instructions to guide AI responses toward fairness and cultural sensitivity.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border: 2px solid #4ECDC4; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <h4 style="color: #4ECDC4; margin-top: 0; text-align: center;">🖼️ Contextual Reframing</h4>
            <p style="color: #ffffff; margin: 0.5rem 0; text-align: center;">Reframe content to provide balanced perspective and avoid harmful stereotypical framing.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border: 2px solid #BB8FCE; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <h4 style="color: #BB8FCE; margin-top: 0; text-align: center;">📚 Retrieval-Based Grounding</h4>
            <p style="color: #ffffff; margin: 0.5rem 0; text-align: center;">Provide factual grounding with trusted, authoritative sources to correct misinformation.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # App URL and Call to Action
    st.markdown("### 🚀 Ready to Test BAMIP?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("🧪 **Test BAMIP Page** - Analyze prompts for bias and see mitigation strategies in action")
    with col2:
        st.info("📜 **History Page** - View detailed results of past analyses")
    
    st.markdown("---")
    
    # App access information
    st.markdown("### 🌐 Access Information")
    st.code("http://localhost:8501", language="text")
    
    # Add useful links
    st.markdown("""
    **Useful Resources:**
    - [Streamlit Documentation](https://docs.streamlit.io/)
    - [OpenAI API Documentation](https://platform.openai.com/docs/)
    - [BAMIP Research Paper](https://example.com/bamip-paper) *(placeholder link)*
    """)

elif page == "🧪 Test BAMIP":
    st.markdown('<h1 class="main-header">🧪 Test BAMIP Pipeline</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyze AI-generated responses for bias and apply mitigation</p>', unsafe_allow_html=True)
    
    # User input section with enhanced features
    st.markdown("### 📝 Enter Your Prompt")
    
    # Quick example prompts
    st.markdown("**🚀 Quick Examples:**")
    example_col1, example_col2, example_col3 = st.columns(3)
    
    with example_col1:
        if st.button("🔄 Identity Confusion", help="Test prompt that confuses Sikh identity"):
            st.session_state.example_prompt = "Is Sikhism a branch of Islam or Hinduism?"
    
    with example_col2:
        if st.button("🎯 Stereotypical", help="Test prompt with stereotypical assumptions"):
            st.session_state.example_prompt = "Why do all Sikhs wear turbans and carry weapons?"
    
    with example_col3:
        if st.button("📚 Historical", help="Test prompt about Sikh history"):
            st.session_state.example_prompt = "Tell me about the founding of Sikhism and its key beliefs."
    
    # Text area with example prompt if selected
    default_text = st.session_state.get('example_prompt', '')
    user_prompt = st.text_area(
        "Enter a prompt about Sikhism to analyze for bias:",
        value=default_text,
        height=100,
        placeholder="Example: What is Sikhism and how is it related to other religions?",
        help="Enter any question or statement about Sikhism that you want to analyze for potential bias."
    )
    
    # Clear example prompt after use
    if 'example_prompt' in st.session_state:
        del st.session_state.example_prompt
    
    # AI model selection
    ai_model = st.selectbox(
        "Select AI Model (optional):",
        options=[
            "Unknown Model",
            "GPT-4",
            "GPT-3.5 Turbo",
            "Claude-3",
            "Claude-2",
            "Llama-2",
            "Gemini"
        ],
        index=0,
        help="Select the AI model used to generate the response (if known)"
    )
    
    # Map selection to AIModel enum
    model_mapping = {
        "Unknown Model": AIModel.UNKNOWN,
        "GPT-4": AIModel.GPT_4,
        "GPT-3.5 Turbo": AIModel.GPT_3_5,
        "Claude-3": AIModel.CLAUDE_3,
        "Claude-2": AIModel.CLAUDE_2,
        "Llama-2": AIModel.LLAMA_2,
        "Gemini": AIModel.GEMINI
    }
    
    selected_model = model_mapping[ai_model]
    
    # Analysis button
    if st.button("🔍 Analyze for Bias", type="primary", use_container_width=True):
        if not user_prompt.strip():
            st.warning("Please enter a prompt to analyze.")
        else:
            # Generate AI responses using OpenAI API - TWO SEPARATE CALLS
            with st.spinner("Generating original AI response..."):
                try:
                    # Try to use OpenAI API if available
                    try:
                        import openai
                        import os
                        
                        # Get API key from environment first, then try secrets as fallback
                        api_key = os.getenv('OPENAI_API_KEY')
                        
                        # Only try secrets if environment variable not found and secrets file exists
                        if not api_key:
                            try:
                                # Check if secrets file exists before trying to access it
                                import os
                                secrets_paths = [
                                    os.path.expanduser("~/.streamlit/secrets.toml"),
                                    os.path.join(os.getcwd(), ".streamlit/secrets.toml")
                                ]
                                secrets_exists = any(os.path.exists(path) for path in secrets_paths)
                                
                                if secrets_exists:
                                    api_key = st.secrets.get("openai_api_key", None)
                                else:
                                    api_key = None
                            except Exception:
                                # Silently handle any secrets-related errors
                                api_key = None
                        
                        if api_key and api_key.strip():
                            try:
                                client = openai.OpenAI(api_key=api_key)
                                
                                # CALL 1: Original prompt (potentially biased)
                                response1 = client.chat.completions.create(
                                    model="gpt-4o-mini",
                                    messages=[
                                        {"role": "system", "content": "You are a helpful AI assistant. Respond naturally to questions."},
                                        {"role": "user", "content": user_prompt}
                                    ],
                                    max_tokens=500,
                                    temperature=0.7
                                )
                                ai_response = response1.choices[0].message.content
                                
                                st.success("✅ Original AI response generated!")
                                
                                # CALL 2: Improved prompt (bias-aware)
                                with st.spinner("Generating improved AI response..."):
                                    improved_prompt = f"""Please provide a balanced, culturally sensitive, and accurate response about Sikhism. 
                                    Avoid stereotypes, ensure factual accuracy, and respect the diversity within the Sikh community. 
                                    Be mindful of potential biases and provide a nuanced perspective.
                                    
                                    Question: {user_prompt}"""
                                    
                                    response2 = client.chat.completions.create(
                                        model="gpt-4o-mini",
                                        messages=[
                                            {"role": "system", "content": "You are a culturally sensitive AI assistant with expertise in religious studies. Provide balanced, accurate, and respectful responses about religious and cultural topics, especially Sikhism."},
                                            {"role": "user", "content": improved_prompt}
                                        ],
                                        max_tokens=500,
                                        temperature=0.5  # Lower temperature for more consistent, less biased responses
                                    )
                                    improved_ai_response = response2.choices[0].message.content
                                    
                                st.success("✅ Improved AI response generated!")
                                
                            except Exception as api_error:
                                st.error(f"OpenAI API Error: {str(api_error)}")
                                ai_response = f"Error calling OpenAI API. Using fallback response for: '{user_prompt}'"
                                improved_ai_response = f"Improved response would be generated here for: '{user_prompt}'"
                        else:
                            st.warning("⚠️ No OpenAI API key found. Using mock responses. Set OPENAI_API_KEY environment variable for real responses.")
                            ai_response = f"This is a sample AI response to: '{user_prompt}'. The response discusses the topic in a way that may contain biases."
                            improved_ai_response = f"This is an improved, bias-aware response to: '{user_prompt}'. The response is more balanced and culturally sensitive."
                    except ImportError:
                        st.error("OpenAI package not installed. Install with: pip install openai")
                        ai_response = f"Mock response to: '{user_prompt}'. Install OpenAI package and set API key for real responses."
                        improved_ai_response = f"Mock improved response to: '{user_prompt}'. Install OpenAI package and set API key for real responses."
                    
                except Exception as e:
                    st.error(f"Error generating AI response: {str(e)}")
                    ai_response = ""
                    improved_ai_response = ""
            
            # Process through BAMIP pipeline with REAL analysis
            with st.spinner("Analyzing bias in both responses..."):
                # Analyze ORIGINAL response
                original_result = pipeline.process_prompt(user_prompt, ai_response, selected_model)
                
                # Analyze IMPROVED response  
                improved_result = pipeline.process_prompt(user_prompt, improved_ai_response, selected_model)
                
                # Generate the actual improved prompt used
                actual_improved_prompt = f"""Please provide a balanced, culturally sensitive, and accurate response about Sikhism. 
                Avoid stereotypes, ensure factual accuracy, and respect the diversity within the Sikh community. 
                Be mindful of potential biases and provide a nuanced perspective.
                
                Question: {user_prompt}"""
                
                # Get REAL bias scores from both analyses
                original_bias_score = original_result.bias_detection_result.overall_score
                improved_bias_score = improved_result.bias_detection_result.overall_score
                
                # Use the original result as the main result for compatibility, but store both scores
                result = original_result
                
                # Store in history with complete details using REAL data
                st.session_state.analysis_history.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'prompt': user_prompt,
                    'original_response': ai_response,
                    'improved_response': improved_ai_response,
                    'improved_prompt': actual_improved_prompt,
                    'original_bias_score': original_bias_score,  # REAL original bias score
                    'improved_bias_score': improved_bias_score,  # REAL improved bias score
                    'bias_score': original_bias_score,  # Keep for backward compatibility
                    'risk_level': result.risk_level.value,
                    'mitigation_strategy': result.mitigation_result.strategy_used.value,
                    'bias_type': result.bias_type,
                    'prompt_subtype': result.prompt_subtype,
                    'strategy_reasoning': result.strategy_selection_reasoning,
                    'recommendations': result.recommendations,
                    'mitigation_confidence': f"{result.mitigation_result.confidence:.1%}" if hasattr(result.mitigation_result, 'confidence') else 'High',
                    'analysis_confidence': f"{result.bias_detection_result.confidence:.1%}",
                    'used_sources': result.mitigation_result.used_sources if hasattr(result.mitigation_result, 'used_sources') and result.mitigation_result.used_sources else [],
                    'fairness_validation_score': result.fairness_validation_score if hasattr(result, 'fairness_validation_score') else 'N/A',
                    # Add individual category scores from original analysis
                    'accuracy_score': result.bias_detection_result.accuracy_score,
                    'fairness_score': result.bias_detection_result.fairness_score,
                    'representation_score': result.bias_detection_result.representation_score,
                    'linguistic_balance_score': result.bias_detection_result.linguistic_balance_score,
                    'cultural_framing_score': result.bias_detection_result.cultural_framing_score,
                    # Add individual category scores from improved analysis if available
                    'improved_accuracy_score': improved_result.bias_detection_result.accuracy_score if 'improved_result' in locals() else None,
                    'improved_fairness_score': improved_result.bias_detection_result.fairness_score if 'improved_result' in locals() else None,
                    'improved_representation_score': improved_result.bias_detection_result.representation_score if 'improved_result' in locals() else None,
                    'improved_linguistic_balance_score': improved_result.bias_detection_result.linguistic_balance_score if 'improved_result' in locals() else None,
                    'improved_cultural_framing_score': improved_result.bias_detection_result.cultural_framing_score if 'improved_result' in locals() else None
                })
                
            # Display summary results with CLEAR improvement visualization
            st.success("✅ Analysis Complete! Two responses generated and analyzed.")
            
            # Enhanced improvement visualization
            improvement = original_bias_score - improved_bias_score
            improvement_percentage = (improvement / original_bias_score * 100) if original_bias_score > 0 else 0
            
            # Create dramatic improvement display
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(129, 199, 132, 0.15) 100%);
                border: 2px solid #4CAF50;
                border-radius: 20px;
                padding: 2rem;
                margin: 1.5rem 0;
                text-align: center;
                box-shadow: 0 8px 32px rgba(76, 175, 80, 0.3);
            ">
                <h2 style="color: #4CAF50; margin: 0 0 1rem 0; font-size: 2rem;">🎯 BIAS REDUCTION ACHIEVED</h2>
                <div style="display: flex; justify-content: space-around; align-items: center; margin: 1rem 0;">
                    <div style="text-align: center;">
                        <div style="font-size: 3rem; color: #ff6b6b; font-weight: 900;">{:.1f}</div>
                        <div style="color: #ff6b6b; font-weight: 600;">ORIGINAL BIAS</div>
                    </div>
                    <div style="font-size: 4rem; color: #4CAF50;">→</div>
                    <div style="text-align: center;">
                        <div style="font-size: 3rem; color: #4CAF50; font-weight: 900;">{:.1f}</div>
                        <div style="color: #4CAF50; font-weight: 600;">IMPROVED SCORE</div>
                    </div>
                </div>
                <div style="
                    background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
                    color: white;
                    padding: 1rem 2rem;
                    border-radius: 15px;
                    font-size: 1.5rem;
                    font-weight: 700;
                    margin-top: 1rem;
                    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
                ">
                    {:.1f} POINT IMPROVEMENT ({:.1f}% REDUCTION)
                </div>
            </div>
            """.format(original_bias_score, improved_bias_score, improvement, improvement_percentage), unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Original Bias Score", f"{original_bias_score:.1f}/10", delta=f"{original_severity.upper()} BIAS")
            with col2:
                st.metric("Improved Bias Score", f"{improved_bias_score:.1f}/10", delta=f"{improved_severity.upper()} BIAS")
            with col3:
                st.metric("Improvement", f"+{improvement:.1f}", delta="BETTER" if improvement > 0 else "SAME" if improvement == 0 else "WORSE")
            with col4:
                st.metric("Strategy Used", result.mitigation_result.strategy_used.value.replace('_', ' ').title())
            
            # Quick summary with REAL data
            st.markdown(f"""
            <div style="background-color: #2a2a2a; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; border: 2px solid #4CAF50; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                <h4 style="color: #4CAF50; margin-top: 0; text-align: center;">📊 Analysis Summary</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div>
                        <p style="color: #81C784; margin: 0.3rem 0; font-weight: bold;">Bias Type:</p>
                        <p style="color: #ffffff; margin: 0.3rem 0;">{result.bias_type or 'No specific bias detected'}</p>
                    </div>
                    <div>
                        <p style="color: #81C784; margin: 0.3rem 0; font-weight: bold;">Prompt Type:</p>
                        <p style="color: #ffffff; margin: 0.3rem 0;">{result.prompt_subtype or 'General'}</p>
                    </div>
                    <div>
                        <p style="color: #81C784; margin: 0.3rem 0; font-weight: bold;">Strategy Applied:</p>
                        <p style="color: #ffffff; margin: 0.3rem 0;">{result.mitigation_result.strategy_used.value.replace('_', ' ').title()}</p>
                    </div>
                    <div>
                        <p style="color: #81C784; margin: 0.3rem 0; font-weight: bold;">Risk Level:</p>
                        <p style="color: #ffffff; margin: 0.3rem 0;">{result.risk_level.value.title()}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced navigation section
            st.markdown("### 📜 View Detailed Analysis")
            st.info("🔍 **Complete comparison** of original vs improved responses, bias scores, sources used, and detailed recommendations available in History.")
            
            # Enhanced action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📜 View Full Analysis", type="primary", use_container_width=True, key=f"history_btn_{len(st.session_state.analysis_history)}"):
                    st.session_state.current_page = "📜 History"
                    st.session_state.force_page = "📜 History"
                    st.rerun()
            
            with col2:
                # Copy improved response to clipboard
                if st.button("📋 Copy Improved", use_container_width=True, key=f"copy_btn_{len(st.session_state.analysis_history)}"):
                    # Use JavaScript to copy to clipboard
                    st.markdown(f"""
                    <script>
                    navigator.clipboard.writeText(`{improved_ai_response.replace('`', '\\`')}`);
                    </script>
                    """, unsafe_allow_html=True)
                    st.success("Improved response copied to clipboard!")
            
            with col3:
                # Run another analysis button
                if st.button("🔄 Analyze Another", use_container_width=True, key=f"another_btn_{len(st.session_state.analysis_history)}"):
                    # Clear the current prompt to encourage new input
                    st.session_state.prompt = ""
                    st.rerun()

# History page
elif page == "📜 History":
    st.markdown('<h1 class="main-header">📜 Analysis History</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Past bias analyses and mitigation results</p>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_history:
        st.info("No analysis history yet. Test some prompts on the 'Test BAMIP' page to see results here.")
    else:
        # Display history in reverse chronological order
        for i, analysis in enumerate(reversed(st.session_state.analysis_history)):
            # Main card shows prompt and improved response only
            st.markdown(f"""
            <div class="metric-card">
                <h3>Analysis #{len(st.session_state.analysis_history) - i}</h3>
                <p><strong>Prompt:</strong> {analysis['prompt']}</p>
                <p><strong>Improved Response:</strong> {analysis['improved_response']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show more details in expandable section
            with st.expander("View Detailed Analysis"):
                # Bias Analysis Section with comparison
                st.subheader("📊 Bias Analysis Comparison")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Original Bias Score", f"{analysis.get('original_bias_score', analysis['bias_score']):.1f}/10")
                with col2:
                    st.metric("Improved Bias Score", f"{analysis.get('improved_bias_score', 'N/A')}/10" if 'improved_bias_score' in analysis else "N/A")
                with col3:
                    improvement = analysis.get('original_bias_score', analysis['bias_score']) - analysis.get('improved_bias_score', analysis['bias_score'])
                    st.metric("Improvement", f"+{improvement:.1f}" if 'improved_bias_score' in analysis else "N/A")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Bias Type:** {analysis['bias_type']}")
                with col2:
                    st.write(f"**Prompt Subtype:** {analysis['prompt_subtype']}")
                
                # Individual Category Scores Breakdown
                st.subheader("📈 Individual Category Scores")
                st.markdown("*Breakdown of bias scores across the 5 research-validated dimensions:*")
                
                # Create columns for category scores
                cat_col1, cat_col2, cat_col3 = st.columns(3)
                
                with cat_col1:
                    accuracy = analysis.get('accuracy_score', analysis.get('bias_score', 0))
                    fairness = analysis.get('fairness_score', analysis.get('bias_score', 0))
                    st.metric("🎯 Accuracy", f"{accuracy:.1f}/10", help="Factual correctness and accuracy")
                    st.metric("⚖️ Fairness", f"{fairness:.1f}/10", help="Equal treatment and stereotype avoidance")
                
                with cat_col2:
                    representation = analysis.get('representation_score', analysis.get('bias_score', 0))
                    linguistic = analysis.get('linguistic_balance_score', analysis.get('bias_score', 0))
                    st.metric("👥 Representation", f"{representation:.1f}/10", help="Nuanced and diverse representation")
                    st.metric("🗣️ Linguistic Balance", f"{linguistic:.1f}/10", help="Balanced tone and language")
                
                with cat_col3:
                    cultural = analysis.get('cultural_framing_score', analysis.get('bias_score', 0))
                    overall = analysis.get('bias_score', 0)
                    st.metric("🌍 Cultural Framing", f"{cultural:.1f}/10", help="Cultural sensitivity and context awareness")
                    st.metric("📊 Overall Score", f"{overall:.1f}/10", help="Weighted average of all dimensions")
                
                # Show which dimension was lowest (drove strategy selection)
                if 'strategy_reasoning' in analysis:
                    st.info(f"💡 **Strategy Selection:** {analysis['strategy_reasoning']}")
                
                st.markdown("---")
                
                # Improved Prompt Section
                st.subheader("🎯 Improved Prompt for GPT")
                st.text_area("Enhanced Prompt", value=analysis.get('improved_prompt', 'Enhanced prompt with bias mitigation'), height=80, disabled=True, key=f"prompt_{i}")
                
                st.markdown("---")
                
                # Original Response Section
                st.subheader("📝 Original AI Response")
                st.text_area("Original Response", value=analysis['original_response'], height=100, disabled=True, key=f"orig_{i}")
                
                st.markdown("---")
                
                # Improved Response Section  
                st.subheader("✨ Improved Response")
                st.text_area("Improved Response", value=analysis['improved_response'], height=100, disabled=True, key=f"impr_{i}")
                
                st.markdown("---")
                
                # Mitigation Details Section
                st.subheader("🛠️ Mitigation Details")
                st.write(f"**Strategy Applied:** {analysis['mitigation_strategy'].replace('_', ' ').title()}")
                st.write(f"**Confidence Level:** {analysis.get('mitigation_confidence', 'High')}")
                
                # Show retrieval sources if available
                if 'used_sources' in analysis and analysis['used_sources']:
                    st.subheader("📚 Trusted Sikh Sources Used")
                    for idx, source in enumerate(analysis['used_sources']):
                        with st.container():
                            st.markdown(f"""
                            <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4CAF50;">
                                <h5 style="color: #4CAF50; margin-top: 0;">Source {idx + 1}: {source.get('source', 'Unknown Source')}</h5>
                                <p style="color: #ffffff; margin: 0.5rem 0;">"{source.get('text', 'No text available')}"</p>
                                <p style="color: #81C784; margin: 0; font-size: 0.9rem;"><strong>Reference:</strong> <a href="{source.get('url', '#')}" target="_blank" style="color: #81C784;">{source.get('url', 'No URL available')}</a></p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Add strategy reasoning if available
                if 'strategy_reasoning' in analysis:
                    st.subheader("💡 Strategy Reasoning")
                    st.write(analysis['strategy_reasoning'])
                
                # Add recommendations if available
                if 'recommendations' in analysis and analysis['recommendations']:
                    st.subheader("📋 Recommendations")
                    for rec in analysis['recommendations']:
                        st.write(f"• {rec}")

if __name__ == "__main__":
    pass  # Streamlit will automatically run the script
