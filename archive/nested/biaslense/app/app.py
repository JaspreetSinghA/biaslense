"""
LLM Fairness Toolkit - Minimal Streamlit App
Bias detection using cosine similarity and stereotype anchors
"""

import streamlit as st
import pandas as pd
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import os

# Page configuration
st.set_page_config(
    page_title="LLM Fairness Toolkit",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def load_embedding_model():
    """Load and cache the sentence transformer model"""
    return SentenceTransformer('all-mpnet-base-v2')

@st.cache_data
def load_stereotypes():
    """Load and cache the stereotype list from JSON file"""
    # Get the path relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, '..', 'data', 'stereotypes.json')
    
    try:
        with open(data_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Stereotype file not found at: {data_path}")
        return []
    except json.JSONDecodeError:
        st.error("Error reading stereotype file. Please check JSON format.")
        return []

def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)

def analyze_bias(text: str, model: SentenceTransformer, stereotypes: List[str]) -> Tuple[List[Dict], pd.DataFrame]:
    """
    Analyze bias in text using cosine similarity with stereotype anchors
    
    Returns:
        - List of flagged phrases (similarity >= 0.35)
        - DataFrame of all similarity scores sorted by score
    """
    if not text.strip():
        return [], pd.DataFrame()
    
    # Encode the input text
    text_embedding = model.encode([text])[0]
    
    # Encode all stereotype phrases
    stereotype_embeddings = model.encode(stereotypes)
    
    # Compute similarities
    similarities = []
    for i, stereotype in enumerate(stereotypes):
        similarity = compute_cosine_similarity(text_embedding, stereotype_embeddings[i])
        similarities.append({
            'Stereotype': stereotype,
            'Similarity': round(similarity, 4)
        })
    
    # Create DataFrame and sort by similarity
    df = pd.DataFrame(similarities)
    df_sorted = df.sort_values('Similarity', ascending=False)
    
    # Flag phrases with similarity >= 0.35
    flagged = [item for item in similarities if item['Similarity'] >= 0.35]
    
    return flagged, df_sorted

def main():
    """Main application function"""
    
    # Custom CSS for beautiful styling
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .header-title {
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.4rem;
        font-weight: 300;
        margin-bottom: 0;
    }
    
    .input-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .results-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .flagged-item {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(255,107,107,0.3);
        border-left: 5px solid #ff4757;
    }
    
    .success-item {
        background: linear-gradient(135deg, #2ed573 0%, #1e90ff 100%);
        color: white;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(46,213,115,0.3);
        border-left: 5px solid #2ed573;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(116,185,255,0.3);
    }
    
    .section-header {
        color: #2d3436;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #74b9ff;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102,126,234,0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102,126,234,0.6);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #ddd;
        font-size: 1rem;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102,126,234,0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Beautiful Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🧠 LLM Fairness Toolkit</h1>
        <p class="header-subtitle">✨ Case Study: Bias Against Sikhs ✨</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load models and data
    with st.spinner("Loading embedding model..."):
        model = load_embedding_model()
    
    stereotypes = load_stereotypes()
    
    if not stereotypes:
        st.error("No stereotypes loaded. Please check the data file.")
        return
    
    st.markdown(f"""
    <div class="success-item">
        <h3 style="margin: 0; font-size: 1.2rem;">🎉 System Ready!</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Model loaded successfully! Using {len(stereotypes)} stereotype anchors for analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input section with beautiful container
    st.markdown("""
    <div class="input-container">
        <h2 class="section-header">📝 Enter AI-Generated Text</h2>
    </div>
    """, unsafe_allow_html=True)
    
    user_text = st.text_area(
        "Paste the AI-generated text you want to analyze for bias:",
        height=200,
        placeholder="Enter your AI-generated text here for bias analysis...",
        help="Paste any text generated by AI models like ChatGPT, Claude, or Gemini"
    )
    
    # Analysis button with custom styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_clicked = st.button("🔍 Analyze for Bias", type="primary", use_container_width=True)
    
    if analyze_clicked:
        if not user_text.strip():
            st.warning("Please enter some text to analyze.")
            return
        
        with st.spinner("Analyzing bias..."):
            flagged_phrases, all_similarities = analyze_bias(user_text, model, stereotypes)
        
        # Results section with beautiful styling
        st.markdown("""
        <div class="results-container">
            <h2 class="section-header">📊 Analysis Results</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Flagged phrases section with beautiful styling
        st.markdown("""
        <div class="results-container">
            <h3 class="section-header">🚩 Flagged Phrases (Similarity ≥ 0.35)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if flagged_phrases:
            st.markdown(f"""
            <div class="flagged-item">
                <h3 style="margin: 0; font-size: 1.3rem;">⚠️ Bias Alert!</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Found {len(flagged_phrases)} potentially biased phrases with high similarity scores:</p>
            </div>
            """, unsafe_allow_html=True)
            
            for i, phrase in enumerate(flagged_phrases, 1):
                st.markdown(f"""
                <div class="flagged-item">
                    <h4 style="margin: 0; font-size: 1.1rem;">#{i} "{phrase['Stereotype']}"</h4>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; font-weight: bold;">Similarity Score: {phrase['Similarity']:.4f}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-item">
                <h3 style="margin: 0; font-size: 1.3rem;">✅ No Bias Detected!</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">No phrases flagged above the 0.35 similarity threshold. The text appears to be bias-free!</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Full similarity table with beautiful styling
        st.markdown("""
        <div class="results-container">
            <h3 class="section-header">📋 Complete Similarity Analysis</h3>
            <p style="color: #636e72; font-size: 1.1rem; margin-bottom: 1.5rem;">Complete ranking of all stereotype similarities (highest to lowest):</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Style the dataframe
        def highlight_high_similarity(val):
            if val >= 0.35:
                return 'background-color: #ffebee; color: #d32f2f; font-weight: bold'
            elif val >= 0.25:
                return 'background-color: #fff3e0; color: #f57c00'
            else:
                return ''
        
        styled_df = all_similarities.style.applymap(
            highlight_high_similarity, 
            subset=['Similarity']
        ).format({'Similarity': '{:.4f}'})
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=400
        )
        
        # Summary statistics with beautiful cards
        st.markdown("""
        <div class="results-container">
            <h3 class="section-header">📈 Analysis Summary</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        max_similarity = all_similarities['Similarity'].max()
        avg_similarity = all_similarities['Similarity'].mean()
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 2rem;">📚</h3>
                <h2 style="margin: 0.5rem 0; font-size: 2rem;">{len(stereotypes)}</h2>
                <p style="margin: 0; opacity: 0.9;">Total Stereotypes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 2rem;">🚩</h3>
                <h2 style="margin: 0.5rem 0; font-size: 2rem;">{len(flagged_phrases)}</h2>
                <p style="margin: 0; opacity: 0.9;">Flagged Phrases</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 2rem;">📊</h3>
                <h2 style="margin: 0.5rem 0; font-size: 2rem;">{max_similarity:.3f}</h2>
                <p style="margin: 0; opacity: 0.9;">Max Similarity</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 2rem;">📈</h3>
                <h2 style="margin: 0.5rem 0; font-size: 2rem;">{avg_similarity:.3f}</h2>
                <p style="margin: 0; opacity: 0.9;">Avg Similarity</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
