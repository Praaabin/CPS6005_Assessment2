"""
Configuration file for TerraFlow Analytics project
Contains all project-level constants and configurations
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"

# HDFS Configuration
HDFS_NAMENODE_HOST = "namenode"
HDFS_NAMENODE_PORT = 9000
HDFS_URL = f"hdfs://{HDFS_NAMENODE_HOST}:{HDFS_NAMENODE_PORT}"
HDFS_RAW_PATH = "/terraflow/data/raw"
HDFS_PROCESSED_PATH = "/terraflow/data/processed"

# Spark Configuration
SPARK_MASTER_URL = "spark://spark-master:7077"
SPARK_APP_NAME = "TerraFlow_Analytics"
SPARK_EXECUTOR_MEMORY = "4g"
SPARK_DRIVER_MEMORY = "2g"
SPARK_EXECUTOR_CORES = 2

# Data Configuration
GTFS_FILENAME = "CPS6005-Assessment 2_GTFS_Data.csv"
GTFS_RAW_PATH = RAW_DATA_DIR / GTFS_FILENAME

# Feature columns
TEMPORAL_FEATURES = [
    'arrival_time', 'departure_time', 'trip_duration',
    'hour_of_day', 'day_of_week', 'is_peak_hour'
]

SPATIAL_FEATURES = [
    'route_id', 'stop_id', 'stop_sequence'
]

PERFORMANCE_FEATURES = [
    'average_speed', 'trip_frequency', 'service_reliability_index',
    'congestion_level', 'delay_minutes'
]

TARGET_VARIABLE = 'congestion_level'

# Congestion level mapping
CONGESTION_MAPPING = {
    'low': 0,
    'moderate': 1,
    'high': 2
}

# Statistical analysis parameters
CONFIDENCE_LEVEL = 0.95
ALPHA = 0.05

# Machine Learning parameters
TEST_SIZE = 0.2
RANDOM_STATE = 42
CV_FOLDS = 5

# Model evaluation metrics
CLASSIFICATION_METRICS = ['accuracy', 'precision', 'recall', 'f1']
REGRESSION_METRICS = ['rmse', 'mae', 'r2']

# Visualization settings
PLOT_STYLE = 'seaborn-v0_8-darkgrid'
FIGURE_SIZE = (12, 6)
DPI = 100

# Dashboard configuration
DASHBOARD_HOST = '0.0.0.0'
DASHBOARD_PORT = 8050
DASHBOARD_DEBUG = True

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
