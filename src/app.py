"""
BiasLens - Main Streamlit Application
Comprehensive AI bias detection tool
"""

import streamlit as st
import pandas as pd
import altair as alt
import json
import time
from typing import Dict, List
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.rubric_scoring import BiasRubricScorer, BiasAnalysisResult
from core.embedding_checker import EmbeddingChecker, SimilarityResult
from core.bias_mitigator import BAMIPMitigator, MitigationResult, MitigationStrategy


# Page configuration
st.set_page_config(
    page_title="BiasLens - AI Bias Detection",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
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
        background-color: #d4edda;
        color: #155724;
        border: 2px solid #c3e6cb;
    }
    .medium-bias {
        background-color: #fff3cd;
        color: #856404;
        border: 2px solid #ffeaa7;
    }
    .high-bias {
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #f5c6cb;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .explanation-box {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_models():
    """Load and cache the bias detection models"""
    try:
        with st.spinner("Loading bias detection models..."):
            scorer = BiasRubricScorer()
            embedder = EmbeddingChecker()
            mitigator = BAMIPMitigator()
            st.success("Models loaded successfully!")
            return scorer, embedder, mitigator
    except Exception as e:
        st.error(f"Failed to load models: {e}")
        return None, None, None


def get_bias_severity(score: float) -> str:
    """Determine bias severity level"""
    if score >= 7.0:
        return "low"
    elif score >= 4.0:
        return "medium"
    else:
        return "high"


def get_severity_color(severity: str) -> str:
    """Get color for severity level"""
    colors = {
        "low": "#28a745",
        "medium": "#ffc107", 
        "high": "#dc3545"
    }
    return colors.get(severity, "#6c757d")


def create_bias_chart(scores: Dict[str, float]) -> alt.Chart:
    """Create Altair chart for bias scores"""
    data = pd.DataFrame([
        {"Dimension": k.replace("_", " ").title(), "Score": v}
        for k, v in scores.items()
    ])
    
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('Dimension:N', title='Bias Dimensions'),
        y=alt.Y('Score:Q', title='Score (0-10)', scale=alt.Scale(domain=[0, 10])),
        color=alt.condition(
            alt.datum.Score >= 7,
            alt.value('#28a745'),  # Green for good scores
            alt.condition(
                alt.datum.Score >= 4,
                alt.value('#ffc107'),  # Yellow for medium scores
                alt.value('#dc3545')   # Red for poor scores
            )
        ),
        tooltip=['Dimension', 'Score']
    ).properties(
        title='Bias Analysis Breakdown',
        width=600,
        height=400
    )
    
    return chart


def create_similarity_chart(similarity_scores: Dict[str, float]) -> alt.Chart:
    """Create Altair chart for similarity scores"""
    if not similarity_scores:
        return None
    
    # Get top 10 similar phrases
    top_similarities = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    
    data = pd.DataFrame([
        {"Phrase": phrase[:30] + "..." if len(phrase) > 30 else phrase, "Similarity": score}
        for phrase, score in top_similarities
    ])
    
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('Similarity:Q', title='Similarity Score'),
        y=alt.Y('Phrase:N', title='Stereotype Phrase', sort='-x'),
        color=alt.condition(
            alt.datum.Similarity >= 0.8,
            alt.value('#dc3545'),  # Red for high similarity
            alt.condition(
                alt.datum.Similarity >= 0.5,
                alt.value('#ffc107'),  # Yellow for medium similarity
                alt.value('#28a745')   # Green for low similarity
            )
        ),
        tooltip=['Phrase', 'Similarity']
    ).properties(
        title='Top Similar Stereotype Phrases',
        width=600,
        height=400
    )
    
    return chart


def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🧠 BiasLens</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Comprehensive AI Bias Detection Tool</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    # Load models
    scorer, embedder, mitigator = load_models()
    
    if scorer is None or embedder is None or mitigator is None:
        st.error("Failed to load bias detection models. Please check your installation.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model settings
        st.subheader("Detection Settings")
        similarity_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.1,
            max_value=0.9,
            value=0.35,
            step=0.05,
            help="Threshold for flagging similar stereotype phrases"
        )
        
        # Update embedder threshold
        embedder.update_thresholds({'default': similarity_threshold})
        
        # Analysis options
        st.subheader("Analysis Options")
        include_similarity = st.checkbox("Include Similarity Analysis", value=True)
        include_breakdown = st.checkbox("Show Detailed Breakdown", value=True)
        include_mitigation = st.checkbox("Include BAMIP Mitigation", value=True)
        
        # Export options
        st.subheader("Export Options")
        if st.button("Export Analysis History"):
            if st.session_state.analysis_history:
                df = pd.DataFrame(st.session_state.analysis_history)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="bias_analysis_history.csv",
                    mime="text/csv"
                )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Text Analysis")
        
        # Text input
        text_input = st.text_area(
            "Enter AI-generated text to analyze for bias:",
            height=200,
            placeholder="Paste your text here...",
            help="Enter text from ChatGPT, Claude, or other AI models to detect potential bias"
        )
        
        # Analysis button
        if st.button("🔍 Analyze Bias", type="primary"):
            if text_input.strip():
                with st.spinner("Analyzing text for bias..."):
                    # Perform analysis
                    start_time = time.time()
                    
                    # Rubric scoring
                    rubric_result = scorer.score_text(text_input)
                    
                    # Similarity analysis
                    similarity_result = None
                    if include_similarity:
                        similarity_result = embedder.compute_similarity(text_input)
                    
                    # BAMIP mitigation
                    mitigation_result = None
                    if include_mitigation:
                        mitigation_result = mitigator.mitigate_bias(text_input)
                    
                    analysis_time = time.time() - start_time
                    
                    # Store results in session state
                    analysis_data = {
                        'text': text_input[:100] + "..." if len(text_input) > 100 else text_input,
                        'overall_score': rubric_result.overall_score,
                        'severity': get_bias_severity(rubric_result.overall_score),
                        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                        'analysis_time': round(analysis_time, 2)
                    }
                    
                    st.session_state.analysis_history.append(analysis_data)
                    
                    # Display results
                    display_results(rubric_result, similarity_result, mitigation_result, include_breakdown)
            else:
                st.warning("Please enter some text to analyze.")
    
    with col2:
        st.header("📊 Quick Stats")
        
        if st.session_state.analysis_history:
            df = pd.DataFrame(st.session_state.analysis_history)
            
            # Average score
            avg_score = df['overall_score'].mean()
            st.metric("Average Bias Score", f"{avg_score:.2f}/10")
            
            # Severity distribution
            severity_counts = df['severity'].value_counts()
            st.subheader("Severity Distribution")
            for severity, count in severity_counts.items():
                color = get_severity_color(severity)
                st.markdown(f"<span style='color: {color}; font-weight: bold;'>{severity.title()}: {count}</span>", unsafe_allow_html=True)
            
            # Recent analyses
            st.subheader("Recent Analyses")
            for i, analysis in enumerate(st.session_state.analysis_history[-5:]):
                severity_color = get_severity_color(analysis['severity'])
                st.markdown(
                    f"<div style='border-left: 3px solid {severity_color}; padding-left: 10px; margin: 5px 0;'>"
                    f"<strong>{analysis['severity'].title()}</strong> ({analysis['overall_score']:.1f}/10)<br>"
                    f"<small>{analysis['timestamp']}</small></div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No analyses yet. Enter some text to get started!")


def display_results(rubric_result: BiasAnalysisResult, similarity_result: SimilarityResult, mitigation_result: MitigationResult, include_breakdown: bool):
    """Display analysis results"""
    
    # Overall bias score
    severity = get_bias_severity(rubric_result.overall_score)
    severity_color = get_severity_color(severity)
    
    st.markdown(f"""
    <div class="bias-score {severity}-bias">
        Bias Score: {rubric_result.overall_score:.1f}/10
        <br><small>{severity.upper()} BIAS DETECTED</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Confidence indicator
    confidence_color = "#28a745" if rubric_result.confidence > 0.7 else "#ffc107" if rubric_result.confidence > 0.4 else "#dc3545"
    st.markdown(f"<p style='text-align: center; color: {confidence_color};'><strong>Confidence: {rubric_result.confidence:.1%}</strong></p>", unsafe_allow_html=True)
    
    # Detailed breakdown
    if include_breakdown:
        st.subheader("📊 Detailed Analysis")
        
        # Create columns for metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4>🎯 Accuracy</h4>
                <p>Factual correctness and reliability</p>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Score", f"{rubric_result.accuracy_score:.1f}/10")
            
            st.markdown("""
            <div class="metric-card">
                <h4>⚖️ Fairness</h4>
                <p>Equal treatment across groups</p>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Score", f"{rubric_result.fairness_score:.1f}/10")
            
            st.markdown("""
            <div class="metric-card">
                <h4>👥 Representation</h4>
                <p>Depth and nuance in portrayal</p>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Score", f"{rubric_result.representation_score:.1f}/10")
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h4>🗣️ Linguistic Balance</h4>
                <p>Tone and language neutrality</p>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Score", f"{rubric_result.linguistic_balance_score:.1f}/10")
            
            st.markdown("""
            <div class="metric-card">
                <h4>🌍 Cultural Framing</h4>
                <p>Cultural context awareness</p>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Score", f"{rubric_result.cultural_framing_score:.1f}/10")
        
        # Visualizations
        st.subheader("📈 Visual Analysis")
        
        # Bias breakdown chart
        scores = {
            'accuracy': rubric_result.accuracy_score,
            'fairness': rubric_result.fairness_score,
            'representation': rubric_result.representation_score,
            'linguistic_balance': rubric_result.linguistic_balance_score,
            'cultural_framing': rubric_result.cultural_framing_score
        }
        
        chart = create_bias_chart(scores)
        st.altair_chart(chart, use_container_width=True)
        
        # Similarity analysis
        if similarity_result and similarity_result.similarity_scores:
            st.subheader("🔍 Similarity Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Max Similarity", f"{similarity_result.max_similarity:.3f}")
                st.metric("Severity Level", similarity_result.severity_level.title())
            
            with col2:
                st.metric("Similar Phrases", len(similarity_result.similar_phrases))
                st.metric("Threshold Exceeded", "Yes" if similarity_result.threshold_exceeded else "No")
            
            # Similarity chart
            similarity_chart = create_similarity_chart(similarity_result.similarity_scores)
            if similarity_chart:
                st.altair_chart(similarity_chart, use_container_width=True)
        
        # Explanations
        if rubric_result.explanations:
            st.subheader("💡 Bias Explanations")
            for explanation in rubric_result.explanations:
                st.markdown(f"""
                <div class="explanation-box">
                    {explanation}
                </div>
                """, unsafe_allow_html=True)
        
        # Flagged patterns
        if rubric_result.flagged_patterns:
            st.subheader("🚩 Flagged Patterns")
            for pattern in rubric_result.flagged_patterns:
                st.markdown(f"- `{pattern}`")
        
        # BAMIP Mitigation Results
        if mitigation_result:
            st.subheader("🛠️ BAMIP Mitigation Results")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Bias Reduction", f"{mitigation_result.bias_reduction_score:.1%}")
                st.metric("Strategy Used", mitigation_result.strategy_used.value.replace('_', ' ').title())
            
            with col2:
                st.metric("Mitigation Confidence", f"{mitigation_result.confidence:.1%}")
                st.metric("Strategy Type", mitigation_result.strategy_used.value.split('_')[0].title())
            
            # Original vs Mitigated Text
            st.subheader("📝 Text Comparison")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original Text:**")
                st.text_area("", value=mitigation_result.original_text, height=150, disabled=True)
            
            with col2:
                st.markdown("**Mitigated Text:**")
                st.text_area("", value=mitigation_result.mitigated_text, height=150, disabled=True)
            
            # Mitigation Explanations
            if mitigation_result.explanations:
                st.subheader("💡 Mitigation Strategy")
                for explanation in mitigation_result.explanations:
                    st.markdown(f"""
                    <div class="explanation-box">
                        {explanation}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Suggested Prompts
            if mitigation_result.suggested_prompts:
                st.subheader("🎯 Suggested Bias-Free Prompts")
                for i, prompt in enumerate(mitigation_result.suggested_prompts, 1):
                    st.markdown(f"**Option {i}:**")
                    st.code(prompt, language="text")


if __name__ == "__main__":
    main() 