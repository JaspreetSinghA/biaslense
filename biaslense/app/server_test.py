import streamlit as st

# Simple test to verify Streamlit is working
st.title("Server Test")
st.write("If you can see this, Streamlit server is working correctly.")

# Display some debugging info
st.write(f"Current page: {st.experimental_get_query_params()}")
st.write("Session state keys:", list(st.session_state.keys()))
