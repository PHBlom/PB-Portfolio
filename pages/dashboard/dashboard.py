import streamlit as st
import pandas as pd
import plotly.express as px
from date_selector import show_date_selector

show_date_selector()
selected_year = st.session_state.selected_year
selected_month = st.session_state.selected_month


# -----------------------
# LOAD DATA
# -----------------------

df = pd.read_excel(
    "pages/dashboard/Dashboard.xlsx",
    sheet_name="Raw calcs"
)

df["Date"] = pd.to_datetime(df["Date"])

df["Asset"] = df["Asset"].astype(str).str.strip()

# -----------------------
# MONTH / YEAR SELECTION
# -----------------------

available_dates = sorted(df["Date"].unique())

filtered = df[
    (df["Date"].dt.year == selected_year)
    & (df["Date"].dt.month == selected_month)
]

# -----------------------
# SPLIT DATA
# -----------------------

assets = filtered[
    (~filtered["Asset"].isin(["DUO", "Total"]))
    & (filtered["Value"] > 0)
]

liabilities = filtered[
    filtered["Asset"] == "DUO"
]

total_assets = assets["Value"].sum()
total_liabilities = abs(liabilities["Value"].sum())

equity = total_assets - total_liabilities

# -----------------------
# CARDs
# -----------------------

with st.container(border=True, width='stretch', horizontal_alignment='center'):
    with st.container(border=True, width='content'):
        st.metric("Equity", f"€ {equity:,.0f}")

    with st.container(width='content', horizontal=True):
        with st.container(border=True, width='content'):
            st.metric("Assets", f"€ {total_assets:,.0f}")
        with st.container(border=True, width='content'):
            st.metric("Liabilities", f"€ {total_liabilities:,.0f}")

# -----------------------
# PIE CHARTS
# -----------------------

col1, col2 = st.columns(2)

with col1:

    fig_assets = px.pie(
        assets,
        values="Value",
        names="Asset",
        hole=0.55
    )

    fig_assets.update_traces(
        textposition="outside",
        textinfo="label+percent"
    )

    fig_assets.update_layout(
        title="Asset Allocation"
    )

    st.plotly_chart(
        fig_assets,
        width='stretch'
    )

with col2:

    liquidity = (
        assets
        .groupby("Liquidity", as_index=False)["Value"]
        .sum()
    )

    fig_liquidity = px.pie(
        liquidity,
        values="Value",
        names="Liquidity"
    )

    fig_liquidity.update_traces(
        textposition="outside",
        textinfo="label+percent"
    )

    fig_liquidity.update_layout(
        title="Liquidity Split"
    )

    st.plotly_chart(
        fig_liquidity,
        width='stretch'
    )

# -----------------------
# TABLES
# -----------------------

assets_table = assets[["Asset", "Value"]].copy()

assets_table["Percentage"] = (
    assets_table["Value"] / assets_table["Value"].sum()
)

asset_total = assets_table["Value"].sum()

total_row = pd.DataFrame({
    "Asset": ["Total"],
    "Value": [asset_total],
    "Percentage": [1.0]
})

assets_table = pd.concat(
    [assets_table, total_row],
    ignore_index=True
)

assets_table["Value"] = assets_table["Value"].map(
    lambda x: f"€ {x:,.2f}"
)

assets_table["Percentage"] = assets_table["Percentage"].map(
    lambda x: f"{x:.1%}"
)

liabilities_table = liabilities[
    ["Asset", "Value"]
].copy()

liabilities_table["Percentage"] = (
    liabilities_table["Value"].abs()
    / liabilities_table["Value"].abs().sum()
)

liabilities_table["Value"] = (
    liabilities_table["Value"]
    .map(lambda x: f"€ {x:,.2f}")
)

liabilities_table["Percentage"] = (
    liabilities_table["Percentage"]
    .map(lambda x: f"{x:.1%}")
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Liabilities")
    st.dataframe(
        liabilities_table,
        hide_index=True,
        width='stretch'
    )

with col2:
    st.subheader("Assets")
    st.dataframe(
        assets_table,
        hide_index=True,
        width='stretch'
    )