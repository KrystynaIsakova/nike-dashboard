"""
Nike Sales Performance Dashboard — Streamlit
============================================
Run:
    pip install streamlit plotly pandas
    streamlit run nike_dashboard.py

Upload any CSV with these columns:
    Date, Product, Region, Channel, Units_Sold, Unit_Price,
    Production_Cost, Marketing_Spend, Customer_Rating,
    Return_Rate, Revenue, Profit, Profit_Margin
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nike Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── PALETTE ───────────────────────────────────────────────────────────────────
BLACK   = "#000000"
TEAL    = "#005147"
RED     = "#ba2b2b"
ORANGE  = "#ea553b"
WHITE   = "#ffffff"
CARD    = "#0e0e0e"
MUTED   = "rgba(255,255,255,0.38)"
SUBTLE  = "rgba(255,255,255,0.62)"
GRID    = "rgba(255,255,255,0.05)"

PRODUCT_COLORS = {
    "Accessories":      ORANGE,
    "Athletic Apparel": TEAL,
    "Basketball Shoes": RED,
    "Running Shoes":    "rgba(255,255,255,0.72)",
}
REGION_COLORS = [ORANGE, TEAL, RED, "#c47a5a"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor=CARD,
    plot_bgcolor=CARD,
    font=dict(family="DM Sans, sans-serif", color=SUBTLE, size=11),
    margin=dict(l=10, r=10, t=10, b=10),
    hoverlabel=dict(
        bgcolor="#080808",
        bordercolor=TEAL,
        font=dict(family="DM Sans, sans-serif", color=WHITE, size=12),
    ),
)

# Reusable legend style — applied per-chart, not in shared layout
LEGEND_STYLE = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=SUBTLE, size=11))

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');

/* ── Page & app shell ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #000000 !important;
}
[data-testid="stAppViewContainer"] > .main {
    background-color: #000000 !important;
}
[data-testid="block-container"] {
    padding: 2rem 2rem 3rem !important;
    max-width: 1200px;
}
section[data-testid="stSidebar"] { display: none; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
#[data-testid="stToolbar"] { display: none; }
#[data-testid="stDecoration"] { display: none; }

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: #0e0e0e !important;
    border: 1px dashed rgba(0,81,71,0.55) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
}
[data-testid="stFileUploader"] label { color: rgba(255,255,255,0.62) !important; }
[data-testid="stFileUploader"] button {
    background: rgba(0,81,71,0.18) !important;
    border: 1px solid rgba(0,81,71,0.55) !important;
    color: #005147 !important;
    border-radius: 6px !important;
}

/* ── Select box (product filter) ── */
[data-testid="stSelectbox"] > div > div {
    background: #0e0e0e !important;
    border-color: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.62) !important;
    border-radius: 8px !important;
}

/* ── Badge ── */
.badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 10px; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: #005147; background: rgba(0,81,71,0.18);
    border: 1px solid rgba(0,81,71,0.55);
    padding: 3px 11px; border-radius: 4px;
    margin-bottom: 10px;
}

/* ── H1 ── */
.dash-title {
    font-family: 'Syne', sans-serif;
    font-size: 28px; font-weight: 800;
    letter-spacing: -0.03em; color: #ffffff;
    margin: 6px 0 4px;
}
.dash-subtitle { font-size: 13px; color: rgba(255,255,255,0.38); margin-bottom: 0; }

/* ── KPI cards ── */
.kpi-card {
    background: #0e0e0e;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 16px;
    border-top-width: 2px;
    border-top-style: solid;
}
.kpi-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px; font-weight: 500;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: rgba(255,255,255,0.38); margin-bottom: 4px;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 22px; font-weight: 800;
    margin-bottom: 3px; line-height: 1.1;
}
.kpi-sub { font-size: 11px; color: rgba(255,255,255,0.38); }

/* ── Chart card ── */
.chart-card {
    background: #0e0e0e;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px 22px 14px;
    margin-bottom: 0;
}
.chart-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px; font-weight: 500;
    letter-spacing: 0.14em; text-transform: uppercase;
    color: #005147; margin-bottom: 3px;
}
.chart-title {
    font-family: 'Syne', sans-serif;
    font-size: 16px; font-weight: 700;
    color: #ffffff; margin-bottom: 2px;
}
.chart-desc { font-size: 12px; color: rgba(255,255,255,0.38); margin-bottom: 0; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 1.2rem 0 !important; }

/* ── Plotly chart container ── */
[data-testid="stPlotlyChart"] {
    border-radius: 10px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt_b(val):
    if val >= 1e12: return f"${val/1e12:.2f}T"
    if val >= 1e9:  return f"${val/1e9:.1f}B"
    if val >= 1e6:  return f"${val/1e6:.0f}M"
    return f"${val:,.0f}"

def kpi_card(label, value, sub, accent):
    return f"""
    <div class="kpi-card" style="border-top-color:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color:{accent}">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""

def chart_header(num, title, desc):
    st.markdown(f"""
    <div class="chart-label">Chart {num:02d}</div>
    <div class="chart-title">{title}</div>
    <div class="chart-desc">{desc}</div>
    <div style="margin-bottom:12px"></div>
    """, unsafe_allow_html=True)

def card_open():
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

def card_close():
    st.markdown('</div>', unsafe_allow_html=True)


# ── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"])
    df["YearMonth"] = df["Date"].dt.to_period("M")
    # Total marketing spend per row
    df["Total_Mkt_Spend"] = df["Marketing_Spend"] * df["Units_Sold"]
    return df


# ── CHARTS ────────────────────────────────────────────────────────────────────
def make_line_chart(monthly: pd.DataFrame, avg_rev: float) -> go.Figure:
    fig = go.Figure()

    # Gradient fill via area trace + line trace
    fig.add_trace(go.Scatter(
        x=monthly["Label"], y=monthly["Revenue_B"],
        fill="tozeroy",
        fillcolor="rgba(0,81,71,0.18)",
        line=dict(color="rgba(0,0,0,0)", width=0),
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=monthly["Label"], y=monthly["Revenue_B"],
        mode="lines",
        line=dict(color=TEAL, width=2.5, shape="spline", smoothing=0.8),
        name="Revenue",
        customdata=monthly[["Revenue_B", "vs_avg", "vs_avg_sign"]].values,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Revenue: <b>$%{customdata[0]:.1f}B</b><br>"
            "vs avg: <b>%{customdata[2]}%{customdata[1]:.1f}B</b>"
            "<extra></extra>"
        ),
        hoverlabel=dict(bgcolor="#080808", bordercolor=TEAL),
    ))
    # Average reference line
    fig.add_hline(
        y=avg_rev, line_dash="dot",
        line_color="rgba(255,255,255,0.28)", line_width=1.5,
        annotation_text=f"Avg ${avg_rev:.1f}B",
        annotation_font=dict(color="rgba(255,255,255,0.38)", size=10),
        annotation_position="top right",
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        legend=LEGEND_STYLE,
        height=300,
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=SUBTLE, size=10),
            linecolor="rgba(255,255,255,0.1)",
            nticks=12,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=GRID,
            zeroline=False,
            tickfont=dict(color=SUBTLE, size=10),
            tickprefix="$", ticksuffix="B",
            range=[
                monthly["Revenue_B"].min() * 0.85,
                monthly["Revenue_B"].max() * 1.05,
            ],
        ),
    )
    return fig


def make_bar_chart(region_df: pd.DataFrame, total_profit: float) -> go.Figure:
    colors = [REGION_COLORS[i % len(REGION_COLORS)] for i in range(len(region_df))]
    fig = go.Figure(go.Bar(
        x=region_df["Region"],
        y=region_df["Profit_B"],
        marker=dict(
            color=colors,
            line=dict(width=0),
            cornerradius=6,
        ),
        customdata=region_df[["Profit_B", "Share_pct"]].values,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Profit: <b>$%{customdata[0]:.1f}B</b><br>"
            "Share: <b>%{customdata[1]:.1f}%</b>"
            "<extra></extra>"
        ),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        legend=LEGEND_STYLE,
        height=300,
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=SUBTLE, size=10),
            linecolor="rgba(255,255,255,0.1)",
        ),
        yaxis=dict(
            showgrid=True, gridcolor=GRID,
            zeroline=False,
            tickfont=dict(color=SUBTLE, size=10),
            tickprefix="$", ticksuffix="B",
            range=[0, region_df["Profit_B"].max() * 1.18],
        ),
    )
    return fig


def make_scatter_chart(scatter_df: pd.DataFrame, product_filter: str) -> go.Figure:
    fig = go.Figure()

    # Break-even diagonal line (ROI = 1×)
    max_axis = max(scatter_df["Mkt_B"].max(), scatter_df["Rev_B"].max()) * 1.1
    fig.add_trace(go.Scatter(
        x=[0, max_axis], y=[0, max_axis],
        mode="lines",
        line=dict(color="rgba(255,255,255,0.25)", width=1.5, dash="dot"),
        name="Break-even (ROI = 1×)",
        hoverinfo="skip",
    ))

    products = sorted(scatter_df["Product"].unique())
    for prod in products:
        if product_filter != "All" and prod != product_filter:
            continue
        sub = scatter_df[scatter_df["Product"] == prod]
        color = PRODUCT_COLORS.get(prod, WHITE)
        fig.add_trace(go.Scatter(
            x=sub["Mkt_B"], y=sub["Rev_B"],
            mode="markers",
            name=prod,
            marker=dict(
                color=color,
                size=7,
                opacity=0.85,
                line=dict(width=0),
            ),
            customdata=sub[["Product", "Rev_B", "Mkt_B", "ROI"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Revenue: <b>$%{customdata[1]:.2f}B</b><br>"
                "Mkt Spend: <b>$%{customdata[2]:.2f}B</b><br>"
                "ROI: <b>%{customdata[3]:.1f}× rev per $ mkt</b>"
                "<extra></extra>"
            ),
        ))

    scatter_legend = dict(**LEGEND_STYLE, orientation="h",
                          yanchor="bottom", y=-0.28, xanchor="left", x=0)
    fig.update_layout(
        **PLOTLY_LAYOUT,
        legend=scatter_legend,
        height=300,
        xaxis=dict(
            title=dict(text="Total Marketing Spend ($B)", font=dict(color=MUTED, size=11)),
            showgrid=True, gridcolor=GRID,
            tickfont=dict(color=SUBTLE, size=10),
            linecolor="rgba(255,255,255,0.1)",
            tickprefix="$", ticksuffix="B",
            range=[0, scatter_df["Mkt_B"].max() * 1.12],
        ),
        yaxis=dict(
            title=dict(text="Revenue ($B)", font=dict(color=MUTED, size=11)),
            showgrid=True, gridcolor=GRID,
            zeroline=False,
            tickfont=dict(color=SUBTLE, size=10),
            tickprefix="$", ticksuffix="B",
            range=[0, scatter_df["Rev_B"].max() * 1.12],
        ),
    )
    return fig


# ── MAIN APP ──────────────────────────────────────────────────────────────────
def main():

    # ── Upload screen ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="badge">Nike Analytics</div>
    <div class="dash-title">Sales Performance Dashboard</div>
    <div class="dash-subtitle">Revenue trends &nbsp;·&nbsp; Regional profit &nbsp;·&nbsp; Marketing ROI</div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Load & validate ────────────────────────────────────────────────────────
    try:
        df = load_data('https://docs.google.com/spreadsheets/d/e/2PACX-1vS2UUYRo7pH-Ly64jFzi-JfVahZM2G-gCOgOJ91XpGIyRxim6AAidfJTpAljw_tbEdfBRc2yUDHMNgi/pub?gid=292821970&single=true&output=csv')
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        return

    required = {"Date","Product","Region","Revenue","Profit",
                "Marketing_Spend","Units_Sold","Profit_Margin"}
    missing  = required - set(df.columns)
    if missing:
        st.error(f"CSV is missing columns: {', '.join(missing)}")
        return

    # ── Compute KPIs ──────────────────────────────────────────────────────────
    total_revenue = df["Revenue"].sum()
    total_profit  = df["Profit"].sum()
    avg_margin    = (total_profit / total_revenue * 100)

    # Monthly revenue
    monthly_rev = (
        df.groupby("YearMonth")["Revenue"]
        .sum()
        .reset_index()
        .sort_values("YearMonth")
    )
    monthly_rev["Revenue_B"]   = monthly_rev["Revenue"] / 1e9
    monthly_rev["Label"]       = monthly_rev["YearMonth"].dt.strftime("%b '%y")
    avg_rev_b                  = monthly_rev["Revenue_B"].mean()
    monthly_rev["vs_avg"]      = monthly_rev["Revenue_B"] - avg_rev_b
    monthly_rev["vs_avg_sign"] = monthly_rev["vs_avg"].apply(lambda x: "+" if x >= 0 else "")
    peak_row                   = monthly_rev.loc[monthly_rev["Revenue_B"].idxmax()]

    # Region profit
    region_profit = (
        df.groupby("Region")["Profit"]
        .sum()
        .reset_index()
        .sort_values("Profit", ascending=False)
    )
    region_profit["Profit_B"]  = region_profit["Profit"] / 1e9
    region_profit["Share_pct"] = region_profit["Profit"] / total_profit * 100
    top_region                 = region_profit.iloc[0]

    # Best ROI product (profit / total_mkt_spend)
    prod_agg = df.groupby("Product").agg(
        Profit=("Profit","sum"),
        Total_Mkt=("Total_Mkt_Spend","sum"),
    ).reset_index()
    prod_agg["ROI"] = prod_agg["Profit"] / prod_agg["Total_Mkt"].replace(0, float("nan"))
    best_roi_row    = prod_agg.loc[prod_agg["ROI"].idxmax()]

    # Scatter data
    scatter = (
        df.groupby(["YearMonth","Product","Region"])
        .agg(Revenue=("Revenue","sum"), Mkt=("Total_Mkt_Spend","sum"))
        .reset_index()
    )
    scatter["Rev_B"] = scatter["Revenue"] / 1e9
    scatter["Mkt_B"] = scatter["Mkt"] / 1e9
    scatter["ROI"]   = (scatter["Rev_B"] / scatter["Mkt_B"].replace(0, float("nan"))).round(2)
    scatter.rename(columns={"Product":"Product"}, inplace=True)

    # Date range badge
    min_date = df["Date"].min().strftime("%b %Y")
    max_date = df["Date"].max().strftime("%b %Y")
    st.markdown(
        f'<div class="badge">Nike Analytics · {min_date} – {max_date}</div>',
        unsafe_allow_html=True,
    )

    # ── KPI STRIP ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5, gap="small")
    with k1:
        st.markdown(kpi_card(
            "Total Revenue", fmt_b(total_revenue),
            "All regions & products", TEAL,
        ), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card(
            "Total Profit", fmt_b(total_profit),
            f"Avg margin ~{avg_margin:.1f}%", ORANGE,
        ), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card(
            "Peak Month", fmt_b(peak_row["Revenue"]),
            peak_row["Label"], RED,
        ), unsafe_allow_html=True)
    with k4:
        top_r_label = top_region["Region"].replace(
            "Asia Pacific & Latin America","Asia Pac & LatAm"
        )
        st.markdown(kpi_card(
            "Top Region", top_r_label,
            f"{fmt_b(top_region['Profit'])} profit", ORANGE,
        ), unsafe_allow_html=True)
    with k5:
        roi_label = best_roi_row["Product"].replace(
            "Basketball Shoes","Bball Shoes"
        ).replace("Athletic Apparel","Ath. Apparel")
        st.markdown(kpi_card(
            "Best ROI Product", roi_label,
            "Highest profit per $ mkt spend", TEAL,
        ), unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── CHART 1: Monthly Revenue Line ─────────────────────────────────────────
    card_open()
    chart_header(
        1,
        "Monthly Revenue Trend",
        f"{min_date} – {max_date} &nbsp;·&nbsp; dashed = period average ({fmt_b(avg_rev_b * 1e9)})",
    )
    st.plotly_chart(
        make_line_chart(monthly_rev, avg_rev_b),
        use_container_width=True,
        config={"displayModeBar": False},
    )
    card_close()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── CHARTS 2 + 3 side by side ─────────────────────────────────────────────
    col_bar, col_scatter = st.columns([1, 1.45], gap="medium")

    with col_bar:
        card_open()
        chart_header(
            2,
            "Total Profit by Region",
            f"Cumulative {min_date} – {max_date} &nbsp;·&nbsp; total {fmt_b(total_profit)}",
        )
        # Legend
        legend_html = '<div style="display:flex;flex-wrap:wrap;gap:6px 16px;margin-bottom:12px">'
        for i, row in region_profit.iterrows():
            c = REGION_COLORS[list(region_profit.index).index(i) % len(REGION_COLORS)]
            legend_html += (
                f'<div style="display:flex;align-items:center;gap:6px">'
                f'<span style="width:10px;height:10px;border-radius:3px;'
                f'background:{c};flex-shrink:0;display:inline-block"></span>'
                f'<span style="font-size:11px;color:rgba(255,255,255,0.62)">'
                f'{row["Region"]}</span></div>'
            )
        legend_html += '</div>'
        st.markdown(legend_html, unsafe_allow_html=True)
        st.plotly_chart(
            make_bar_chart(region_profit, total_profit),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        card_close()

    with col_scatter:
        card_open()
        chart_header(
            3,
            "Revenue vs Marketing Spend — ROI View",
            "Each point = product × region × month &nbsp;·&nbsp; dashed = break-even (ROI = 1×)",
        )
        products_list = ["All"] + sorted(df["Product"].unique().tolist())
        product_filter = st.selectbox(
            "Filter by product",
            options=products_list,
            label_visibility="collapsed",
        )
        st.plotly_chart(
            make_scatter_chart(scatter, product_filter),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        card_close()


if __name__ == "__main__":
    main()