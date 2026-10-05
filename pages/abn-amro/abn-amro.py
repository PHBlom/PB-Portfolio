import streamlit as st

tab1, tab2, tab3 = st.tabs(
    ["Overview", "Data", "Transactions"]
)

with tab1:
    st.write("Overview")

with tab2:
    st.write("Data")

with tab3:
    st.write("Transactions")
    
st.title("ABN AMRO")

st.write("Portfolio overview goes here")

