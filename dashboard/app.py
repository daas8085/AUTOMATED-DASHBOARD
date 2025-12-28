"""
Main dashboard application
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt
import json
from sqlalchemy import create_engine
from typing import Dict, Any, Optional
import logging
from pathlib import Path

# Local imports
from dashboard.components.metrics import create_metrics
from dashboard.components.charts import create_charts
from dashboard.components.filters import create_filters
from dashboard.utils.data_loader import DataLoader
from dashboard.utils.helpers import format_currency, format_number

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Automated Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/daas8085/automated-dashboard',
        'Report a bug': "https://github.com/daas8085/automated-dashboard/issues",
        'About': "# Automated Dashboard v1.0"
    }
)

# Custom CSS
def load_css():
    """Load custom CSS styles"""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .metric-card {
            padding: 20px;
            border-radius: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stAlert {
            border-radius: 10px;
            border-left: 5px solid #1E88E5;
        }
        .stButton button {
            width: 100%;
            border-radius: 5px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
        }
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #2c3e50 0%, #1a252f 100%);
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    if 'real_time_updates' not in st.session_state:
        st.session_state.real_time_updates = True

def main():
    """Main dashboard application"""
    
    # Load CSS
    load_css()
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📈 Automated Business Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Real-time analytics and insights for your business")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")
        
        # Refresh control
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", key="refresh_button"):
                st.cache_data.clear()
                st.session_state.last_refresh = datetime.now()
                st.rerun()
        
        with col2:
            auto_refresh = st.checkbox("Auto-refresh", value=True)
            if auto_refresh:
                refresh_rate = st.selectbox("Refresh rate", ["5 seconds", "30 seconds", "1 minute", "5 minutes"])
        
        # Data source selection
        st.subheader("Data Source")
        data_source = st.radio(
            "Select data source:",
            ["Database", "API", "Local File", "Sample Data"],
            index=0
        )
        
        # Theme selector
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=2)
        if theme != st.session_state.theme:
            st.session_state.theme = theme
        
        # Display info
        st.divider()
        st.info(f"Last refresh: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Export options
        st.subheader("Export")
        export_format = st.selectbox("Format", ["CSV", "Excel", "JSON", "PDF"])
        if st.button("📥 Export Dashboard"):
            st.success("Export initiated...")
    
    # Main content area
    try:
        # Load data
        data_loader = DataLoader(source=data_source.lower())
        df = data_loader.load_data()
        
        if df.empty:
            st.warning("No data available. Please check your data source.")
            return
        
        # Display metrics
        st.header("📊 Key Metrics")
        create_metrics(df)
        
        # Charts section
        st.header("📈 Visualizations")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Trends", "Distribution", "Forecast"])
        
        with tab1:
            create_charts(df, chart_type="overview")
        
        with tab2:
            create_charts(df, chart_type="trends")
        
        with tab3:
            create_charts(df, chart_type="distribution")
        
        with tab4:
            create_charts(df, chart_type="forecast")
        
        # Data table
        with st.expander("🔍 View Raw Data", expanded=False):
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "timestamp": st.column_config.DatetimeColumn(
                        "Timestamp",
                        format="YYYY-MM-DD HH:mm:ss"
                    ),
                    "value": st.column_config.NumberColumn(
                        "Value",
                        format="$%.2f"
                    )
                }
            )
        
        # Data summary
        st.header("📋 Data Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(df))
        
        with col2:
            st.metric("Date Range", 
                     f"{df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}")
        
        with col3:
            st.metric("Data Size", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # Real-time updates indicator
        if st.session_state.real_time_updates:
            st.sidebar.success("🟢 Real-time updates active")
        
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        logger.error(f"Dashboard error: {e}", exc_info=True)
        
        # Show sample data on error
        st.info("Showing sample data due to error...")
        sample_data = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'value': np.random.randn(30).cumsum() + 100,
            'category': np.random.choice(['A', 'B', 'C'], 30)
        })
        create_metrics(sample_data)
        create_charts(sample_data)

if __name__ == "__main__":
    main()