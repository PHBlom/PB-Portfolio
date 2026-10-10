import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from date_selector import dashboard_overview_date, dashboard_timeline_date

ASSET_COLORS = {
    "ABN-AMRO": "#4E79A7",
    "DEGIRO": "#F2C80F",
    "IWMA": "#9C6DB0",
    "Laaken": "#3BAE7E",
    "Coinbase": "#1F3B73",
    "DUO": "#E15759",
    "NuBank": "#8EC7F0",
    "Schiele": "#D98B4E",
}

tab1, tab2 = st.tabs(["Overview", "Timeline"])

with tab1:
    st.header("Dashboard")

    with open("pages/dashboard/dashboard.css") as f:
        dashboard_css = f.read()
    st.markdown(f'<style>{dashboard_css}</style>', unsafe_allow_html=True)

    dashboard_overview_date()
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


with tab2:
    st.header("Timeline")

    dashboard_timeline_date()
    selected_year = st.session_state.selected_year

    df_filtered = df[df["Date"].dt.year.isin(selected_year)]

    pivot = (
        df_filtered
        .pivot(index="Date", columns="Asset", values="Value")
        .fillna(0)
    )

    pivot.index = pivot.index.strftime("%b %Y")

    assets = sorted(
        [c for c in pivot.columns if c != "Total"]
    )

    selected_assets = st.multiselect(
        "Assets",
        assets,
        default=assets
    )

    pivot["FilteredTotal"] = pivot[selected_assets].sum(axis=1)

    def euro_k(x):
        return f"€ {x/1000:.0f}K"

    fig_bar = go.Figure()

    for asset in selected_assets:
        fig_bar.add_trace(
            go.Bar(
                x=pivot.index,
                y=pivot[asset],
                name=asset,
                marker_color=ASSET_COLORS.get(asset)
            )
        )

    fig_bar.add_trace(
        go.Scatter(
            x=pivot.index,
            y=pivot["FilteredTotal"],
            name="Total",
            mode="lines+markers+text",
            text=[
                f"€ {v/1000:.0f}K"
                for v in pivot["FilteredTotal"]
            ],
            textposition="top center",
            line=dict(
                color="black",
                width=4
            )
        )
    )

    fig_bar.update_yaxes(
        tickprefix="€ ",
        tickformat=",.0f"
    )

    fig_bar.update_layout(
        title="Asset Allocation",
        barmode="stack",
        height=500,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_bar,
        width='stretch'
    )


    fig_line = go.Figure()

    for asset in selected_assets:
        fig_line.add_trace(
            go.Scatter(
                x=pivot.index,
                y=pivot[asset],
                name=asset,
                mode="lines+markers+text",
                text=[
                    f"€ {v/1000:.0f}K"
                    for v in pivot[asset]
                ],
                textposition="top center",
                line=dict(
                    color=ASSET_COLORS.get(asset),
                    width=3
                )
            )
        )

    fig_line.add_trace(
        go.Scatter(
            x=pivot.index,
            y=pivot["FilteredTotal"],
            name="Total",
            mode="lines+markers+text",
            text=[
                f"€ {v/1000:.0f}K"
                for v in pivot["FilteredTotal"]
            ],
            textposition="top center",
            line=dict(
                color="black",
                width=5
            )
        )
    )

    fig_line.update_yaxes(
        tickprefix="€ ",
        tickformat=",.0f"
    )

    fig_line.update_layout(
        title="Asset Development",
        height=500,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_line,
        width='stretch'
    )