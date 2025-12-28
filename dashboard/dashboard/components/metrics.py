"""
Metrics components for the dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any

def create_metrics(df: pd.DataFrame) -> None:
    """
    Create and display metric cards
    
    Args:
        df: DataFrame containing the data
    """
    if df.empty:
        st.warning("No data available for metrics")
        return
    
    # Calculate metrics
    metrics = calculate_metrics(df)
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=f"${metrics['total_revenue']:,.0f}",
            delta=f"{metrics['revenue_growth']:+.1%}",
            delta_color="normal",
            help="Total revenue with growth percentage"
        )
    
    with col2:
        st.metric(
            label="Active Users",
            value=f"{metrics['active_users']:,.0f}",
            delta=f"{metrics['user_growth']:+.0f}",
            help="Number of active users with growth"
        )
    
    with col3:
        st.metric(
            label="Conversion Rate",
            value=f"{metrics['conversion_rate']:.2%}",
            delta=f"{metrics['conversion_change']:+.2%}",
            help="Conversion rate with change"
        )
    
    with col4:
        st.metric(
            label="Avg. Session",
            value=f"{metrics['avg_session']:.1f}m",
            delta=f"{metrics['session_change']:+.1f}m",
            help="Average session duration"
        )
    
    # Additional metrics in second row
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            label="Bounce Rate",
            value=f"{metrics['bounce_rate']:.1%}",
            delta=f"{metrics['bounce_change']:+.1%}",
            delta_color="inverse"
        )
    
    with col6:
        st.metric(
            label="Customer Satisfaction",
            value=f"{metrics['satisfaction']:.1f}/5.0",
            delta=f"{metrics['satisfaction_change']:+.1f}",
            help="CSAT score"
        )
    
    with col7:
        st.metric(
            label="Orders",
            value=f"{metrics['total_orders']:,.0f}",
            delta=f"{metrics['order_growth']:+.1%}"
        )
    
    with col8:
        st.metric(
            label="Profit Margin",
            value=f"{metrics['profit_margin']:.1%}",
            delta=f"{metrics['margin_change']:+.1%}"
        )

def calculate_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate all metrics from the dataframe
    
    Args:
        df: DataFrame containing the data
    
    Returns:
        Dictionary of calculated metrics
    """
    # Mock calculations - replace with actual logic
    metrics = {
        'total_revenue': df.get('revenue', 0).sum() if 'revenue' in df.columns else np.random.randint(10000, 100000),
        'revenue_growth': np.random.uniform(-0.1, 0.2),
        'active_users': df.get('users', 0).sum() if 'users' in df.columns else np.random.randint(1000, 10000),
        'user_growth': np.random.randint(-100, 500),
        'conversion_rate': np.random.uniform(0.01, 0.05),
        'conversion_change': np.random.uniform(-0.01, 0.01),
        'avg_session': np.random.uniform(2, 10),
        'session_change': np.random.uniform(-1, 1),
        'bounce_rate': np.random.uniform(0.3, 0.6),
        'bounce_change': np.random.uniform(-0.05, 0.05),
        'satisfaction': np.random.uniform(3.5, 4.8),
        'satisfaction_change': np.random.uniform(-0.3, 0.3),
        'total_orders': np.random.randint(500, 5000),
        'order_growth': np.random.uniform(-0.05, 0.15),
        'profit_margin': np.random.uniform(0.1, 0.3),
        'margin_change': np.random.uniform(-0.03, 0.03)
    }
    
    return metrics