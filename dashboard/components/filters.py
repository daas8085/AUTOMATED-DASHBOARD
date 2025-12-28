"""
Filter components for the dashboard
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, List, Optional, Any
import pandas as pd

def create_filters(df: pd.DataFrame) -> Tuple[Any, List[str], str]:
    """
    Create interactive filters for the dashboard
    
    Args:
        df: DataFrame containing the data
    
    Returns:
        Tuple of (date_range, selected_categories, selected_metric)
    """
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Date Range Filter
        st.subheader("Date Range")
        
        if 'timestamp' in df.columns:
            min_date = df['timestamp'].min().date()
            max_date = df['timestamp'].max().date()
            
            date_range = st.date_input(
                "Select date range:",
                value=(max_date - timedelta(days=30), max_date),
                min_value=min_date,
                max_value=max_date,
                help="Select the date range for analysis"
            )
        else:
            date_range = st.date_input(
                "Select date range:",
                value=(datetime.now().date() - timedelta(days=30), datetime.now().date())
            )
        
        # Category Filter
        st.subheader("Categories")
        
        if 'category' in df.columns:
            categories = sorted(df['category'].dropna().unique().tolist())
            selected_categories = st.multiselect(
                "Select categories:",
                options=categories,
                default=categories[:min(3, len(categories))] if categories else [],
                help="Filter data by categories"
            )
        else:
            selected_categories = []
        
        # Metric Selection
        st.subheader("Metrics")
        
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            selected_metric = st.selectbox(
                "Primary metric:",
                options=numeric_cols,
                index=0 if len(numeric_cols) > 0 else None,
                help="Select the primary metric to analyze"
            )
        else:
            selected_metric = None
        
        # Region Filter (if available)
        if 'region' in df.columns:
            st.subheader("Region")
            regions = sorted(df['region'].dropna().unique().tolist())
            selected_regions = st.multiselect(
                "Select regions:",
                options=regions,
                default=regions,
                help="Filter data by regions"
            )
        
        # Additional Options
        st.subheader("Options")
        
        show_forecast = st.checkbox("Show forecast", value=False)
        show_anomalies = st.checkbox("Detect anomalies", value=True)
        smooth_data = st.checkbox("Smooth data", value=False)
        
        if smooth_data:
            window_size = st.slider("Smoothing window:", 3, 30, 7)
        
        # Reset Filters Button
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset Filters", type="secondary"):
                st.session_state.clear()
                st.rerun()
        
        with col2:
            if st.button("💾 Save View", type="secondary"):
                st.success("View saved!")
        
        # Export Options
        st.divider()
        st.subheader("Export")
        
        export_format = st.radio(
            "Export format:",
            ["CSV", "Excel", "JSON"],
            horizontal=True
        )
        
        if st.button("📥 Export Data", type="primary"):
            st.info("Export functionality coming soon!")
    
    return date_range, selected_categories, selected_metric

def apply_filters(df: pd.DataFrame, date_range: Any, categories: List[str]) -> pd.DataFrame:
    """
    Apply filters to dataframe
    
    Args:
        df: Original dataframe
        date_range: Date range tuple (start, end)
        categories: List of selected categories
    
    Returns:
        Filtered dataframe
    """
    filtered_df = df.copy()
    
    # Apply date filter
    if 'timestamp' in filtered_df.columns and date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['timestamp'].dt.date >= start_date) &
            (filtered_df['timestamp'].dt.date <= end_date)
        ]
    
    # Apply category filter
    if categories and 'category' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['category'].isin(categories)]
    
    return filtered_df