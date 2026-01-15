import json
import pandas as pd
import numpy as np

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go


# =============================================================================
# DATA LOADING (pre-aggregated outputs from Notebook 06)
# =============================================================================
DATA_DIR = "../data/processed"

def detect_columns(df, route_candidates, cong_candidates, count_candidates):
    route_col = next((c for c in route_candidates if c in df.columns), None)
    cong_col  = next((c for c in cong_candidates if c in df.columns), None)
    count_col = next((c for c in count_candidates if c in df.columns), None)
    return route_col, cong_col, count_col

def load_parquet(path):
    return pd.read_parquet(path)

try:
    cong_hour = load_parquet(f"{DATA_DIR}/congestion_by_hour.parquet")
    cong_route = load_parquet(f"{DATA_DIR}/congestion_by_route.parquet")
    speed_trend = load_parquet(f"{DATA_DIR}/speed_trend.parquet")
except Exception as e:
    raise RuntimeError(
        f"❌ Could not load required dashboard parquet outputs from {DATA_DIR}. "
        f"Run Notebook 06 first. Error: {e}"
    )

# Optional but highly recommended for route efficiency chart + D3 network
route_perf = None
try:
    route_perf = load_parquet(f"{DATA_DIR}/route_performance.parquet")
except Exception:
    route_perf = None

# Optional KPIs
kpis = None
try:
    with open(f"{DATA_DIR}/kpis.json", "r") as f:
        kpis = json.load(f)
except Exception:
    kpis = None


# =============================================================================
# COLUMN DETECTION (robust)
# =============================================================================
# congestion_by_hour expected: hour, Degree_of_congestion, count
_, cong_col_hour, count_col_hour = detect_columns(
    cong_hour,
    route_candidates=["route_id", "route"],
    cong_candidates=["Degree_of_congestion", "congestion_level", "congestion"],
    count_candidates=["count", "records", "num_records", "total"]
)
if "hour" not in cong_hour.columns:
    raise ValueError("congestion_by_hour.parquet must include 'hour' column.")
if cong_col_hour is None or count_col_hour is None:
    raise ValueError("congestion_by_hour.parquet must include congestion level + count columns.")

# congestion_by_route expected: route + Degree_of_congestion + count
route_col, cong_col_route, count_col_route = detect_columns(
    cong_route,
    route_candidates=["route_id", "route", "route_short_name", "Route", "trip_id"],
    cong_candidates=["Degree_of_congestion", "congestion_level", "congestion"],
    count_candidates=["count", "records", "num_records", "total"]
)
if route_col is None or cong_col_route is None or count_col_route is None:
    raise ValueError("congestion_by_route.parquet must include route + congestion level + count columns.")

# speed_trend expected: hour, avg_speed
if "hour" not in speed_trend.columns:
    raise ValueError("speed_trend.parquet must include 'hour'.")
if "avg_speed" not in speed_trend.columns:
    # try fallback
    speed_candidates = ["mean_speed", "speed_avg", "speed"]
    speed_col = next((c for c in speed_candidates if c in speed_trend.columns), None)
    if speed_col:
        speed_trend = speed_trend.rename(columns={speed_col: "avg_speed"})
    else:
        raise ValueError("speed_trend.parquet must include avg_speed (or equivalent).")

# route_performance expected: route, avg_speed, congestion_rate, trip_count
if route_perf is not None:
    # detect route column if different
    rp_route = next((c for c in ["route_id", "route", "route_short_name", "Route", route_col] if c in route_perf.columns), None)
    if rp_route and rp_route != route_col:
        route_perf = route_perf.rename(columns={rp_route: route_col})
    needed = {route_col, "avg_speed", "congestion_rate", "trip_count"}
    if not needed.issubset(set(route_perf.columns)):
        route_perf = None  # fallback: disable efficiency scatter


# =============================================================================
# BASIC FILTER VALUES
# =============================================================================
routes = sorted(cong_route[route_col].dropna().astype(str).unique().tolist())
cong_levels = sorted(cong_hour[cong_col_hour].dropna().astype(str).unique().tolist())

min_hour = int(cong_hour["hour"].min())
max_hour = int(cong_hour["hour"].max())


# =============================================================================
# APP
# =============================================================================
app = Dash(
    __name__,
    title="TerraFlow Urban Mobility Dashboard",
    external_scripts=["https://d3js.org/d3.v7.min.js"],
)
server = app.server


# =============================================================================
# HELPERS
# =============================================================================
def kpi_card(title, value, subtitle=""):
    return html.Div([
        html.H3(title),
        html.Div(value, className="metric-value"),
        html.Div(subtitle, className="metric-subtitle") if subtitle else None
    ], className="metric-card")

def safe_div(a, b):
    return a / b if b and b != 0 else 0


# =============================================================================
# LAYOUT
# =============================================================================
app.layout = html.Div([
    html.Div([

        html.Div([
            html.H1("🚌 TerraFlow Urban Mobility Dashboard"),
            html.P("Dynamic dashboards for congestion hotspots, route efficiency, and temporal patterns (Dash/Plotly + D3.js)."),
        ], className="dashboard-header"),

        html.Div([
            html.Div([
                html.Label("📍 Route", className="filter-label"),
                dcc.Dropdown(
                    id="route-filter",
                    options=[{"label": r, "value": r} for r in routes],
                    value=routes[0] if routes else None,
                    clearable=False
                )
            ], className="filter-block"),

            html.Div([
                html.Label("🚦 Congestion Levels", className="filter-label"),
                dcc.Dropdown(
                    id="cong-filter",
                    options=[{"label": c, "value": c} for c in cong_levels],
                    value=cong_levels,
                    multi=True
                )
            ], className="filter-block"),

            html.Div([
                html.Label("🕒 Hour Window", className="filter-label"),
                dcc.RangeSlider(
                    id="hour-range",
                    min=min_hour, max=max_hour, step=1,
                    value=[min_hour, max_hour],
                    marks={h: str(h) for h in range(min_hour, max_hour + 1, 2)},
                    tooltip={"placement": "bottom", "always_visible": False},
                )
            ], className="filter-block filter-wide"),
        ], className="chart-container"),

        html.Div(id="kpi-row", className="metrics-grid"),

        html.Div([
            html.Div([dcc.Graph(id="speed-trend-chart")], className="chart-container"),
            html.Div([dcc.Graph(id="congestion-hour-chart")], className="chart-container"),
        ], className="grid-2"),

        html.Div([
            html.Div([dcc.Graph(id="route-congestion-chart")], className="chart-container"),
            html.Div([dcc.Graph(id="route-efficiency-chart")], className="chart-container"),
        ], className="grid-2"),

        html.Div([
            html.Div([dcc.Graph(id="hotspot-heatmap-plotly")], className="chart-container"),
            html.Div([
                html.Div("Interactive Network: Topology & Efficiency Analysis", className="chart-title"),
                html.Div(id="d3-network-root", style={"minHeight": "480px"}),
                html.Div("Use controls (top-right) to switch between Topology Map and Efficiency Matrix views.", className="chart-note"),
            ], className="chart-container"),
        ], className="grid-2"),

        html.Div([
            html.Div("Interactive Congestion Heatmap: Temporal Patterns", className="chart-title"),
            html.Div(id="d3-heatmap-root", style={"minHeight": "520px"}),
            html.Div("Analyze temporal hotspots by Traffic Volume or Average Speed using the toggle controls.", className="chart-note"),
        ], className="chart-container"),

        html.Div([
            html.P("TerraFlow Analytics | CPS6005 Big Data Assessment | PySpark + HDFS + Spark MLlib + Dash/Plotly + D3.js")
        ], className="footer"),

    ], className="dashboard-container")
])


# =============================================================================
# CALLBACKS
# =============================================================================
@app.callback(
    Output("kpi-row", "children"),
    Output("speed-trend-chart", "figure"),
    Output("congestion-hour-chart", "figure"),
    Output("route-congestion-chart", "figure"),
    Output("route-efficiency-chart", "figure"),
    Output("hotspot-heatmap-plotly", "figure"),
    Input("route-filter", "value"),
    Input("cong-filter", "value"),
    Input("hour-range", "value"),
)
def update_dashboard(selected_route, selected_levels, hour_range):
    hmin, hmax = hour_range

    # Filter: congestion by hour
    ch = cong_hour.copy()
    ch["Degree"] = ch[cong_col_hour].astype(str)
    ch = ch[ch["hour"].between(hmin, hmax)]
    ch = ch[ch["Degree"].isin([str(x) for x in selected_levels])]

    # Filter: speed trend
    st = speed_trend.copy()
    st = st[st["hour"].between(hmin, hmax)]

    # Filter: congestion by route for selected route
    cr = cong_route.copy()
    cr["Degree"] = cr[cong_col_route].astype(str)
    cr[route_col] = cr[route_col].astype(str)
    cr = cr[(cr[route_col] == str(selected_route)) & (cr["Degree"].isin([str(x) for x in selected_levels]))]

    total_records = int(ch[count_col_hour].sum()) if len(ch) else 0
    avg_speed = float(st["avg_speed"].mean()) if len(st) else 0.0

    if len(ch):
        peak_hour = int(ch.groupby("hour")[count_col_hour].sum().sort_values(ascending=False).index[0])
    else:
        peak_hour = None

    if len(cr):
        route_total = float(cr[count_col_route].sum())
        high_labels = {"Heavy congestion", "High", "Severe"}
        high_count = float(cr[cr["Degree"].isin(high_labels)][count_col_route].sum())
        high_rate = safe_div(high_count, route_total) * 100
    else:
        high_rate = 0.0

    kpis_out = [
        kpi_card("Total Records (Filtered)", f"{total_records:,}", f"Hours {hmin}–{hmax}"),
        kpi_card("Average Speed", f"{avg_speed:.1f} km/h", "Temporal trend"),
        kpi_card("Peak Hour", f"{peak_hour}:00" if peak_hour is not None else "N/A", "Highest congestion volume"),
        kpi_card("High Congestion Share (Route)", f"{high_rate:.1f}%", f"Route {selected_route}"),
    ]

    # Chart 1: speed trend (temporal)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=st["hour"], y=st["avg_speed"],
        mode="lines+markers",
        line=dict(width=3),
        marker=dict(size=7),
        name="Avg speed"
    ))
    fig1.update_layout(
        title="Temporal Patterns: Average Speed by Hour",
        xaxis_title="Hour of Day",
        yaxis_title="Speed (km/h)",
        template="plotly_white",
        height=420,
        hovermode="x unified"
    )

    # Chart 2: congestion distribution by hour (stacked)
    fig2 = px.bar(
        ch, x="hour", y=count_col_hour, color="Degree",
        barmode="stack",
        title="Temporal Patterns: Congestion Distribution by Hour",
        labels={count_col_hour: "Records", "hour": "Hour", "Degree": "Congestion Level"},
    )
    fig2.update_layout(template="plotly_white", height=420)

    # Chart 3: route congestion composition
    if len(cr) == 0:
        fig3 = go.Figure()
        fig3.add_annotation(text="No data for selected filters", showarrow=False)
        fig3.update_layout(title="Route Composition: Congestion Levels", template="plotly_white", height=420)
    else:
        fig3 = px.pie(
            cr, values=count_col_route, names="Degree",
            hole=0.45,
            title=f"Route Efficiency (Proxy): Congestion Mix — Route {selected_route}"
        )
        fig3.update_traces(textposition="inside", textinfo="percent+label")
        fig3.update_layout(template="plotly_white", height=420)

    # Chart 4: route efficiency scatter (speed vs congestion rate)
    if route_perf is None:
        fig4 = go.Figure()
        fig4.add_annotation(
            text="route_performance.parquet not found. Export it in Notebook 06 for full efficiency chart.",
            showarrow=False
        )
        fig4.update_layout(title="Route Efficiency: Speed vs Congestion Rate", template="plotly_white", height=420)
    else:
        rp = route_perf.copy()
        rp[route_col] = rp[route_col].astype(str)
        top = rp.nlargest(25, "trip_count")

        fig4 = px.scatter(
            top, x="avg_speed", y="congestion_rate",
            size="trip_count",
            hover_name=route_col,
            title="Route Efficiency: Avg Speed vs Congestion Rate (Top Routes)",
            labels={"avg_speed": "Avg Speed (km/h)", "congestion_rate": "Congestion Rate (0–1)", "trip_count": "Trips"}
        )
        fig4.update_layout(template="plotly_white", height=420)

    # Chart 5: hotspot heatmap (plotly) hour × congestion
    pivot = ch.pivot_table(index="Degree", columns="hour", values=count_col_hour, aggfunc="sum", fill_value=0)
    fig5 = px.imshow(
        pivot,
        aspect="auto",
        title="Congestion Hotspots (Plotly): Hour × Level Intensity",
        labels=dict(x="Hour", y="Congestion Level", color="Count")
    )
    fig5.update_layout(template="plotly_white", height=420)

    return kpis_out, fig1, fig2, fig3, fig4, fig5


# =============================================================================
# RUN
# =============================================================================
if __name__ == "__main__":
    print("🚀 TerraFlow Dashboard: http://localhost:8050")
    app.run(debug=True, host="0.0.0.0", port=8050)
