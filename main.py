import streamlit as st

st.set_page_config(layout="wide")

with open("style.css") as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

pg = st.navigation(
    [
        st.Page("pages/dashboard/dashboard.py", title="Dashboard"),
        st.Page("pages/abn-amro/abn-amro.py", title="ABN AMRO"),
        st.Page("pages/degiro/degiro.py", title="DEGIRO"),
    ],
    position="top",
)

pg.run()