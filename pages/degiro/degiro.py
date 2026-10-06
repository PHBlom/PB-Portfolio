import streamlit as st

tab1, tab2 = st.tabs(
    ["Overview", "Data"]
)

with tab1:
    st.write("Overview")

with tab2:
    st.write("Data")
    
st.title("DEGIRO")


