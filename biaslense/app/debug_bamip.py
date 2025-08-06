"""
Debug version of BAMIP app to isolate the issue
"""
import streamlit as st
import sys
import os

print("DEBUG: Starting BAMIP debug app...")

# Add src to path for imports
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"DEBUG: Current dir from __file__: {current_dir}")
except NameError:
    current_dir = os.getcwd()
    print(f"DEBUG: Current dir from getcwd: {current_dir}")
    if 'app' in current_dir:
        current_dir = os.path.dirname(current_dir)
        print(f"DEBUG: Adjusted current dir: {current_dir}")

sys.path.append(current_dir)
print(f"DEBUG: Added to sys.path: {current_dir}")

# Test basic Streamlit functionality
st.title("🧠 BAMIP Debug Test")
st.write("If you see this, basic Streamlit is working!")

# Test imports one by one
try:
    from src.core.bamip_pipeline import BAMIPPipeline
    st.success("✓ BAMIPPipeline import successful")
    print("DEBUG: BAMIPPipeline import successful")
except Exception as e:
    st.error(f"✗ BAMIPPipeline import failed: {e}")
    print(f"DEBUG: BAMIPPipeline import failed: {e}")

try:
    from src.core.rubric_scoring import BiasRubricScorer
    st.success("✓ BiasRubricScorer import successful")
    print("DEBUG: BiasRubricScorer import successful")
except Exception as e:
    st.error(f"✗ BiasRubricScorer import failed: {e}")
    print(f"DEBUG: BiasRubricScorer import failed: {e}")

# Test pipeline initialization
try:
    pipeline = BAMIPPipeline()
    st.success("✓ BAMIPPipeline initialization successful")
    print("DEBUG: BAMIPPipeline initialization successful")
except Exception as e:
    st.error(f"✗ BAMIPPipeline initialization failed: {e}")
    print(f"DEBUG: BAMIPPipeline initialization failed: {e}")

st.write("Debug app completed successfully!")
print("DEBUG: Debug app completed successfully!")
