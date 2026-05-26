import streamlit as st

st.title("Basic Test App")
st.write("This is a basic Streamlit app to test if the server is working correctly.")

if st.button("Click me"):
    st.write("Button clicked!")
