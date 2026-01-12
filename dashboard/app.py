import pandas as pd
import json
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================================
# DATA LOADING
# ============================================================================

# Load pre-aggregated data
try:
    cong_hour = pd.read_parquet("../data/processed/congestion_by_hour.parquet")
    cong_route = pd.read_parquet("../data/processed/congestion_by_route.parquet")
    speed_trend = pd.read_parquet("../data/processed/speed_trend.parquet")
    route_perf = pd.read_parquet("../data/processed/route_performance.parquet")
    
    with open("../data/processed/kpis.json", 'r') as f:
        kpis = json.load(f)
    
    print("✅ All data loaded successfully")
except Exception as e:
    print(f"⚠️  Error loading data: {e}")
    print("Please run Notebook 06 first to export dashboard data")
    exit(1)

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = Dash(__name__, title="TerraFlow Urban Mobility Dashboard")
app._favicon = None

# Get unique values for filters
route_col = cong_route.columns[0]
routes = sorted(cong_route[route_col].unique())
cong_levels = sorted(cong_hour["Degree_of_congestion"].unique())

# ============================================================================
# LAYOUT
# ============================================================================

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🚌 TerraFlow Urban Mobility Dashboard", 
                style={'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Real-time insights into public transport congestion and performance",
               style={'color': '#7f8c8d', 'fontSize': '16px'})
    ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#ecf0f1'}),
    
    # KPI Cards
    html.Div([
        html.Div([
            html.H3(f"{kpis['total_records']:,}", style={'color': '#3498db', 'margin': '0'}),
            html.P("Total Records", style={'color': '#7f8c8d', 'margin': '5px 0'})
        ], className='kpi-card'),
        
        html.Div([
            html.H3(f"{kpis['avg_speed']:.1f} km/h", style={'color': '#2ecc71', 'margin': '0'}),
            html.P("Average Speed", style={'color': '#7f8c8d', 'margin': '5px 0'})
        ], className='kpi-card'),
        
        html.Div([
            html.H3(f"{kpis['avg_sri']:.2f}", style={'color': '#e74c3c', 'margin': '0'}),
            html.P("Service Reliability", style={'color': '#7f8c8d', 'margin': '5px 0'})
        ], className='kpi-card'),
        
        html.Div([
            html.H3(f"{kpis['most_congested_hour']}:00", style={'color': '#f39c12', 'margin': '0'}),
            html.P("Peak Congestion Hour", style={'color': '#7f8c8d', 'margin': '5px 0'})
        ], className='kpi-card'),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'padding': '20px', 'flexWrap': 'wrap'}),
    
    # Filters
    html.Div([
        html.Div([
            html.Label("📍 Select Route:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='route-filter',
                options=[{'label': r, 'value': r} for r in routes],
                value=routes[0],
                clearable=False,
                style={'width': '100%'}
            )
        ], style={'flex': '1', 'marginRight': '20px'}),
        
        html.Div([
            html.Label("🚦 Congestion Levels:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='cong-filter',
                options=[{'label': c, 'value': c} for c in cong_levels],
                value=cong_levels,
                multi=True,
                style={'width': '100%'}
            )
        ], style={'flex': '1'}),
    ], style={'display': 'flex', 'padding': '20px', 'backgroundColor': '#f8f9fa'}),
    
    # Charts Row 1
    html.Div([
        html.Div([
            dcc.Graph(id='speed-trend-chart')
        ], style={'flex': '1', 'marginRight': '10px'}),
        
        html.Div([
            dcc.Graph(id='congestion-hour-chart')
        ], style={'flex': '1', 'marginLeft': '10px'}),
    ], style={'display': 'flex', 'padding': '20px'}),
    
    # Charts Row 2
    html.Div([
        html.Div([
            dcc.Graph(id='route-congestion-chart')
        ], style={'flex': '1', 'marginRight': '10px'}),
        
        html.Div([
            dcc.Graph(id='route-performance-chart')
        ], style={'flex': '1', 'marginLeft': '10px'}),
    ], style={'display': 'flex', 'padding': '20px'}),
    
    # D3.js Visualization Section
    html.Div([
        html.H3("📊 D3.js Interactive Visualization", 
                style={'color': '#2c3e50', 'marginBottom': '15px'}),
        html.Div(id='d3-root', style={'minHeight': '400px'})
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'margin': '20px'}),
    
    # Footer
    html.Div([
        html.P("TerraFlow Analytics | CPS6005 Big Data Assessment | Powered by PySpark, Dash & D3.js",
               style={'textAlign': 'center', 'color': '#95a5a6', 'padding': '20px'})
    ])
    
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#ffffff'})

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    [Output('speed-trend-chart', 'figure'),
     Output('congestion-hour-chart', 'figure'),
     Output('route-congestion-chart', 'figure'),
     Output('route-performance-chart', 'figure')],
    [Input('route-filter', 'value'),
     Input('cong-filter', 'value')]
)
def update_charts(selected_route, selected_cong_levels):
    """Update all charts based on filter selections"""
    
    # Chart 1: Speed Trend by Hour
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=speed_trend['hour'],
        y=speed_trend['avg_speed'],
        mode='lines+markers',
        name='Average Speed',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.2)'
    ))
    
    fig1.update_layout(
        title='Average Speed by Hour of Day',
        xaxis_title='Hour',
        yaxis_title='Speed (km/h)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    # Chart 2: Congestion by Hour (Stacked Bar)
    ch_filtered = cong_hour[cong_hour['Degree_of_congestion'].isin(selected_cong_levels)]
    
    fig2 = px.bar(
        ch_filtered,
        x='hour',
        y='count',
        color='Degree_of_congestion',
        title='Congestion Distribution by Hour',
        labels={'count': 'Number of Records', 'hour': 'Hour of Day'},
        color_discrete_sequence=px.colors.qualitative.Set2,
        barmode='stack'
    )
    
    fig2.update_layout(
        xaxis_title='Hour',
        yaxis_title='Count',
        template='plotly_white',
        height=400,
        legend_title='Congestion Level'
    )
    
    # Chart 3: Route Congestion Breakdown
    cr_filtered = cong_route[
        (cong_route[route_col] == selected_route) &
        (cong_route['Degree_of_congestion'].isin(selected_cong_levels))
    ]
    
    fig3 = px.pie(
        cr_filtered,
        values='count',
        names='Degree_of_congestion',
        title=f'Congestion Breakdown: Route {selected_route}',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4
    )
    
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    fig3.update_layout(template='plotly_white', height=400)
    
    # Chart 4: Top Routes by Performance
    top_routes = route_perf.nlargest(10, 'trip_count')
    
    fig4 = go.Figure()
    
    fig4.add_trace(go.Bar(
        x=top_routes[route_col],
        y=top_routes['avg_speed'],
        name='Avg Speed',
        marker_color='#2ecc71',
        yaxis='y'
    ))
    
    fig4.add_trace(go.Scatter(
        x=top_routes[route_col],
        y=top_routes['congestion_rate'] * 100,
        name='Congestion Rate (%)',
        marker_color='#e74c3c',
        yaxis='y2',
        mode='lines+markers',
        line=dict(width=3)
    ))
    
    fig4.update_layout(
        title='Top 10 Routes: Speed vs Congestion Rate',
        xaxis_title='Route',
        yaxis=dict(title='Average Speed (km/h)', side='left'),
        yaxis2=dict(title='Congestion Rate (%)', side='right', overlaying='y'),
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    
    return fig1, fig2, fig3, fig4

# ============================================================================
# CSS STYLING
# ============================================================================

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .kpi-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin: 10px;
                min-width: 200px;
                text-align: center;
                transition: transform 0.2s;
            }
            .kpi-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 TerraFlow Dashboard Starting...")
    print("="*70)
    print("📊 Dashboard URL: http://localhost:8050")
    print("🔄 Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    app.run_server(debug=True, host='0.0.0.0', port=8050)
