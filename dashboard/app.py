"""
TerraFlow Analytics Interactive Dashboard
Built with Dash and Plotly for data visualization
"""

import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(
    __name__,
    title="TerraFlow Analytics Dashboard",
    update_title="Loading...",
    external_stylesheets=[
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap'
    ]
)

# Dashboard layout
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("🚌 TerraFlow Analytics Dashboard", className="dashboard-title"),
            html.P("Urban Transport Data Intelligence Platform", className="dashboard-subtitle")
        ], className="dashboard-header"),
        
        # Metrics cards (to be populated with real data)
        html.Div([
            html.Div([
                html.H3("Total Trips"),
                html.Div("Loading...", className="metric-value", id="total-trips")
            ], className="metric-card"),
            
            html.Div([
                html.H3("Avg Congestion"),
                html.Div("Loading...", className="metric-value", id="avg-congestion")
            ], className="metric-card"),
            
            html.Div([
                html.H3("Peak Hour Trips"),
                html.Div("Loading...", className="metric-value", id="peak-trips")
            ], className="metric-card"),
            
            html.Div([
                html.H3("Service Reliability"),
                html.Div("Loading...", className="metric-value", id="reliability")
            ], className="metric-card"),
        ], className="metrics-grid"),
        
        # Placeholder for charts
        html.Div([
            html.H2("Congestion Heatmap", className="chart-title"),
            dcc.Graph(id="congestion-heatmap")
        ], className="chart-container"),
        
        html.Div([
            html.H2("Route Performance", className="chart-title"),
            dcc.Graph(id="route-performance")
        ], className="chart-container"),
        
        html.Div([
            html.H2("Temporal Patterns", className="chart-title"),
            dcc.Graph(id="temporal-patterns")
        ], className="chart-container"),
        
    ], className="dashboard-container")
], style={
    'fontFamily': 'Inter, sans-serif',
    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'minHeight': '100vh',
    'padding': '20px'
})


def create_sample_chart():
    """Create a sample chart for testing"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[1, 2, 3, 4, 5],
        y=[1, 4, 2, 5, 3],
        mode='lines+markers',
        name='Sample Data'
    ))
    fig.update_layout(
        template='plotly_white',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


# Callbacks will be added here to update the dashboard with real data

if __name__ == '__main__':
    logger.info("Starting TerraFlow Analytics Dashboard...")
    logger.info("Dashboard will be available at: http://localhost:8050")
    
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )
