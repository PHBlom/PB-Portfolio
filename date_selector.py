import streamlit as st
import pandas as pd

def show_date_selector():
    years = [2021, 2022, 2023, 2024, 2025, 2026]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    st.session_state.selected_year = st.segmented_control(
        "Years",
        years,
        default=max(years),
        label_visibility="collapsed"
    )

    select_month = st.segmented_control(
        "Months",
        months,
        default=months[pd.Timestamp.now().month - 2], # -2 to show the previous month as default
        label_visibility="collapsed"
    )
    st.session_state.selected_month = months.index(select_month) + 1