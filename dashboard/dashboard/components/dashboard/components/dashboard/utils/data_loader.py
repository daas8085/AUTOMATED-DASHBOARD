"""
Data loader utility for the dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from typing import Optional, Dict, Any, Union
import logging
import json
import os
from pathlib import Path
import requests
from functools import lru_cache

logger = logging.getLogger(__name__)

class DataLoader:
    """Data loader for dashboard"""
    
    def __init__(self, source: str = "database", config: Optional[Dict] = None):
        """
        Initialize data loader
        
        Args:
            source: Data source type (database, api, file, sample)
            config: Configuration dictionary
        """
        self.source = source
        self.config = config or {}
        self.engine = None
        
        if source == "database":
            self._init_database_connection()
    
    def _init_database_connection(self):
        """Initialize database connection"""
        try:
            # Read from environment variables or config
            db_url = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/dashboard_db')
            self.engine = create_engine(db_url, pool_pre_ping=True)
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            self.engine = None
    
    @lru_cache(maxsize=1)
    def load_data(self) -> pd.DataFrame:
        """
        Load data from configured source
        
        Returns:
            DataFrame with loaded data
        """
        try:
            if self.source == "database":
                return self._load_from_database()
            elif self.source == "api":
                return self._load_from_api()
            elif self.source == "file":
                return self._load_from_file()
            else:
                return self._load_sample_data()
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def _load_from_database(self) -> pd.DataFrame:
        """Load data from database"""
        if not self.engine:
            logger.warning("No database connection available")
            return pd.DataFrame()
        
        try:
            # Try to get data from dashboard_data table
            query = """
            SELECT * FROM dashboard_data 
            WHERE timestamp >= NOW() - INTERVAL '90 days'
            ORDER BY timestamp DESC
            """
            
            df = pd.read_sql_query(text(query), self.engine)
            
            if df.empty:
                logger.info("No data in database, generating sample data")
                df = self._generate_sample_data(days=90)
            
            return df
            
        except Exception as e:
            logger.warning(f"Could not load from database: {e}")
            return self._generate_sample_data(days=90)
    
    def _load_from_api(self) -> pd.DataFrame:
        """Load data from API"""
        try:
            api_url = self.config.get('api_url', 'https://api.example.com/data')
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            return df
            
        except Exception as e:
            logger.error(f"API load failed: {e}")
            return self._generate_sample_data(days=30)
    
    def _load_from_file(self) -> pd.DataFrame:
        """Load data from file"""
        try:
            file_path = self.config.get('file_path', 'data/sample_data.csv')
            
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            elif file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            # Ensure timestamp column
            if 'timestamp' not in df.columns and 'date' in df.columns:
                df['timestamp'] = pd.to_datetime(df['date'])
            
            return df
            
        except Exception as e:
            logger.error(f"File load failed: {e}")
            return self._generate_sample_data(days=30)
    
    def _load_sample_data(self) -> pd.DataFrame:
        """Load sample data"""
        return self._generate_sample_data(days=90)
    
    def _generate_sample_data(self, days: int = 90) -> pd.DataFrame:
        """
        Generate sample data for testing
        
        Args:
            days: Number of days of data to generate
        
        Returns:
            DataFrame with sample data
        """
        np.random.seed(42)
        
        dates = pd.date_range(
            end=datetime.now(),
            periods=days,
            freq='D'
        )
        
        # Generate realistic sample data
        base_revenue = 10000
        trend = np.linspace(0, 0.5, days)  # 50% growth over period
        seasonality = np.sin(np.linspace(0, 4 * np.pi, days)) * 0.2
        noise = np.random.normal(0, 0.1, days)
        
        revenue = base_revenue * (1 + trend + seasonality + noise)
        
        data = {
            'timestamp': dates,
            'revenue': revenue,
            'users': np.random.randint(800, 1200, days) + np.linspace(0, 400, days),
            'orders': np.random.randint(50, 150, days) + np.linspace(0, 50, days),
            'conversion_rate': np.random.uniform(0.02, 0.05, days) + np.linspace(0, 0.01, days),
            'avg_session_duration': np.random.uniform(2, 8, days),
            'bounce_rate': np.random.uniform(0.4, 0.6, days) - np.linspace(0, 0.1, days),
            'category': np.random.choice(['Electronics', 'Clothing', 'Home', 'Books'], days),
            'region': np.random.choice(['North', 'South', 'East', 'West'], days)
        }
        
        df = pd.DataFrame(data)
        
        # Add some null values
        mask = np.random.random(days) < 0.05
        df.loc[mask, 'revenue'] = np.nan
        
        return df
    
    def refresh_cache(self):
        """Clear the data cache"""
        self.load_data.cache_clear()
        logger.info("Data cache cleared")

if __name__ == "__main__":
    # Test the data loader
    loader = DataLoader(source="sample")
    df = loader.load_data()
    print(f"Loaded {len(df)} rows")
    print(df.head())