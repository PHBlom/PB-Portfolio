import streamlit as st

st.set_page_config(layout="wide")

st.markdown("""
<style>
.block-container {
    padding-top: 3rem;
    padding-bottom: 1rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}
</style>
""", unsafe_allow_html=True)


pg = st.navigation(
    [
        st.Page("pages/dashboard/dashboard.py", title="Dashboard"),
        st.Page("pages/abn-amro/abn-amro.py", title="ABN AMRO"),
    ],
    position="top",
)

pg.run()