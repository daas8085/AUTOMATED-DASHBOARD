"""
ETL pipeline for automated dashboard
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from pipelines.data_processor import DataProcessor