"""
Chart components for the dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
import altair as alt

def create_charts(df: pd.DataFrame, chart_type: str = "overview") -> None:
    """
    Create and display charts based on chart type
    
    Args:
        df: DataFrame containing the data
        chart_type: Type of charts to create
    """
    if df.empty:
        st.warning("No data available for charts")
        return
    
    # Ensure timestamp column exists
    if 'timestamp' not in df.columns and not df.empty:
        if pd.api.types.is_datetime64_any_dtype(df.index):
            df = df.reset_index()
            df.rename(columns={'index': 'timestamp'}, inplace=True)
        else:
            df['timestamp'] = pd.date_range(start='2024-01-01', periods=len(df), freq='D')
    
    if chart_type == "overview":
        create_overview_charts(df)
    elif chart_type == "trends":
        create_trend_charts(df)
    elif chart_type == "distribution":
        create_distribution_charts(df)
    elif chart_type == "forecast":
        create_forecast_charts(df)

def create_overview_charts(df: pd.DataFrame) -> None:
    """Create overview charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue trend
        if 'revenue' in df.columns:
            fig = px.line(
                df,
                x='timestamp',
                y='revenue',
                title='Revenue Trend',
                template='plotly_white',
                line_shape='spline'
            )
            fig.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="Revenue ($)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Revenue data not available")
    
    with col2:
        # Category distribution
        if 'category' in df.columns:
            category_data = df.groupby('category').size().reset_index(name='count')
            fig = px.pie(
                category_data,
                values='count',
                names='category',
                title='Category Distribution',
                hole=0.4,
                template='plotly_white'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Category data not available")
    
    # Time series with multiple metrics
    st.subheader("Performance Over Time")
    metric_cols = [col for col in df.columns if col not in ['timestamp', 'category', 'id']]
    
    if metric_cols:
        selected_metrics = st.multiselect(
            "Select metrics to display:",
            metric_cols,
            default=metric_cols[:min(3, len(metric_cols))]
        )
        
        if selected_metrics:
            fig = go.Figure()
            for metric in selected_metrics:
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df[metric],
                    name=metric,
                    mode='lines',
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                height=500,
                title="Multiple Metrics Over Time",
                xaxis_title="Date",
                yaxis_title="Value",
                hovermode='x unified',
                template='plotly_white',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig, use_container_width=True)

def create_trend_charts(df: pd.DataFrame) -> None:
    """Create trend analysis charts"""
    # Moving averages
    if 'value' in df.columns:
        df['7_day_ma'] = df['value'].rolling(window=7).mean()
        df['30_day_ma'] = df['value'].rolling(window=30).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['value'],
            name='Actual',
            mode='lines',
            line=dict(color='lightblue', width=1)
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['7_day_ma'],
            name='7-Day MA',
            mode='lines',
            line=dict(color='blue', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['30_day_ma'],
            name='30-Day MA',
            mode='lines',
            line=dict(color='darkblue', width=3)
        ))
        
        fig.update_layout(
            height=500,
            title="Trend Analysis with Moving Averages",
            xaxis_title="Date",
            yaxis_title="Value",
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

def create_distribution_charts(df: pd.DataFrame) -> None:
    """Create distribution charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            selected_col = st.selectbox("Select column for histogram:", numeric_cols)
            fig = px.histogram(
                df,
                x=selected_col,
                nbins=30,
                title=f'Distribution of {selected_col}',
                template='plotly_white'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Box plot
        if len(numeric_cols) > 0 and 'category' in df.columns:
            fig = px.box(
                df,
                x='category',
                y=numeric_cols[0],
                title=f'{numeric_cols[0]} by Category',
                template='plotly_white'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def create_forecast_charts(df: pd.DataFrame) -> None:
    """Create forecast charts"""
    st.info("Forecast feature is under development")
    
    # Simple linear trend projection
    if 'value' in df.columns and len(df) > 10:
        from sklearn.linear_model import LinearRegression
        
        # Prepare data
        df = df.sort_values('timestamp')
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['value'].values
        
        # Fit model
        model = LinearRegression()
        model.fit(X, y)
        
        # Create forecast
        future_periods = 30
        X_future = np.arange(len(df), len(df) + future_periods).reshape(-1, 1)
        y_future = model.predict(X_future)
        
        # Create dates for future
        last_date = df['timestamp'].iloc[-1]
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=future_periods,
            freq='D'
        )
        
        # Plot
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=y,
            name='Historical',
            mode='lines',
            line=dict(color='blue', width=2)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=y_future,
            name='Forecast',
            mode='lines',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig.update_layout(
            height=500,
            title="30-Day Forecast",
            xaxis_title="Date",
            yaxis_title="Value",
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)