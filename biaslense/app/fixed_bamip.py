"""
BAMIP Pipeline - Multi-page Streamlit Application
Bias-Aware Mitigation and Intervention Pipeline with research-based framework
"""

import streamlit as st
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

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

# Sidebar navigation
st.sidebar.title("🧭 BAMIP Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "🧪 Test BAMIP", "📜 History"], index=0)

# Home page
if page == "🏠 Home":
    st.markdown("# 🧠 BAMIP Pipeline")
    st.markdown("## Bias-Aware Mitigation and Intervention Pipeline")
    
    st.markdown("""
    ### What is BAMIP?
    The Bias-Aware Mitigation and Intervention Pipeline (BAMIP) is a research-based framework for detecting and mitigating bias in AI-generated content. 
    It follows a systematic approach to identify bias and apply appropriate mitigation strategies.
    """)

# Test BAMIP page
elif page == "🧪 Test BAMIP":
    st.markdown("# 🧪 Test BAMIP Pipeline")
    st.markdown("## Analyze AI-generated responses for bias and apply mitigation")
    
    st.write("This page allows you to test the BAMIP pipeline with your own prompts and AI responses.")

# History page
elif page == "📜 History":
    st.markdown("# 📜 Analysis History")
    st.markdown("## Past bias analyses and mitigation results")
    
    if not st.session_state.analysis_history:
        st.info("No analysis history yet. Test some prompts on the 'Test BAMIP' page to see results here.")
    else:
        st.write("History will be displayed here.")