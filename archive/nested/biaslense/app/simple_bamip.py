import streamlit as st

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
    st.title("🧠 BAMIP Pipeline")
    st.subheader("Bias-Aware Mitigation and Intervention Pipeline")
    st.write("Welcome to the BAMIP Pipeline application!")
    st.write("This tool helps detect and mitigate bias in AI-generated content.")

# Test BAMIP page
elif page == "🧪 Test BAMIP":
    st.title("🧪 Test BAMIP Pipeline")
    st.write("This is the test page where you can analyze prompts for bias.")

# History page
elif page == "📜 History":
    st.title("📜 Analysis History")
    st.write("This page shows the history of your bias analyses.")
