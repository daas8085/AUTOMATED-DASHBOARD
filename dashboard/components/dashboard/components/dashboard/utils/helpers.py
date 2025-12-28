"""
Helper functions for the dashboard
"""

import pandas as pd
import numpy as np
from typing import Union, Optional, List, Dict, Any
from datetime import datetime, timedelta
import streamlit as st

def format_currency(value: Union[int, float], currency: str = "$") -> str:
    """
    Format a number as currency
    
    Args:
        value: Numeric value to format
        currency: Currency symbol
    
    Returns:
        Formatted currency string
    """
    if pd.isna(value):
        return f"{currency}0"
    
    if abs(value) >= 1_000_000_000:
        return f"{currency}{value/1_000_000_000:.1f}B"
    elif abs(value) >= 1_000_000:
        return f"{currency}{value/1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"{currency}{value/1_000:.1f}K"
    else:
        return f"{currency}{value:,.0f}"

def format_number(value: Union[int, float], decimals: int = 0) -> str:
    """
    Format a number with proper commas and decimals
    
    Args:
        value: Numeric value to format
        decimals: Number of decimal places
    
    Returns:
        Formatted number string
    """
    if pd.isna(value):
        return "0"
    
    return f"{value:,.{decimals}f}"

def calculate_percentage_change(current: float, previous: float) -> float:
    """
    Calculate percentage change between two values
    
    Args:
        current: Current value
        previous: Previous value
    
    Returns:
        Percentage change
    """
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100

def calculate_moving_average(data: pd.Series, window: int = 7) -> pd.Series:
    """
    Calculate moving average
    
    Args:
        data: Time series data
        window: Window size for moving average
    
    Returns:
        Moving average series
    """
    return data.rolling(window=window, min_periods=1).mean()

def detect_anomalies(data: pd.Series, threshold: float = 2.0) -> pd.Series:
    """
    Detect anomalies using z-score method
    
    Args:
        data: Time series data
        threshold: Z-score threshold
    
    Returns:
        Boolean series indicating anomalies
    """
    z_scores = (data - data.mean()) / data.std()
    return abs(z_scores) > threshold

def get_color_for_value(value: float, threshold: float = 0.0) -> str:
    """
    Get color based on value (green for positive, red for negative)
    
    Args:
        value: Numeric value
        threshold: Threshold for neutral
    
    Returns:
        Color string
    """
    if value > threshold:
        return "green"
    elif value < -threshold:
        return "red"
    else:
        return "gray"

def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """
    Validate date range
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        True if valid, False otherwise
    """
    if start_date >= end_date:
        return False
    if (end_date - start_date).days > 365:  # Max 1 year
        return False
    return True

def create_time_periods() -> Dict[str, timedelta]:
    """
    Create common time periods for filtering
    
    Returns:
        Dictionary of time periods
    """
    return {
        "Last 7 days": timedelta(days=7),
        "Last 30 days": timedelta(days=30),
        "Last 90 days": timedelta(days=90),
        "Last year": timedelta(days=365),
        "Month to date": timedelta(days=datetime.now().day - 1),
        "Year to date": timedelta(days=(datetime.now() - datetime(datetime.now().year, 1, 1)).days)
    }

def create_sample_data(rows: int = 100) -> pd.DataFrame:
    """
    Create sample data for testing
    
    Args:
        rows: Number of rows to generate
    
    Returns:
        Sample DataFrame
    """
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=rows),
        end=datetime.now(),
        periods=rows
    )
    
    data = {
        'timestamp': dates,
        'revenue': np.random.randn(rows).cumsum() * 1000 + 10000,
        'users': np.random.randint(800, 1200, rows),
        'orders': np.random.randint(50, 150, rows),
        'conversion_rate': np.random.uniform(0.02, 0.05, rows),
        'category': np.random.choice(['A', 'B', 'C', 'D'], rows),
        'region': np.random.choice(['North', 'South', 'East', 'West'], rows)
    }
    
    return pd.DataFrame(data)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_data_loader(data_loader) -> pd.DataFrame:
    """
    Cached data loader for Streamlit
    
    Args:
        data_loader: DataLoader instance
    
    Returns:
        Loaded DataFrame
    """
    return data_loader.load_data()