"""
Utility functions for TerraFlow Analytics project
"""

import logging
from datetime import datetime
import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql.functions import col

logger = logging.getLogger(__name__)


def setup_logging(log_level="INFO"):
    """
    Configure logging for the project
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def spark_df_to_pandas(spark_df, sample_size=None):
    """
    Convert Spark DataFrame to Pandas DataFrame
    
    Args:
        spark_df (DataFrame): Spark DataFrame
        sample_size (int): Optional sample size for large datasets
    
    Returns:
        pd.DataFrame: Pandas DataFrame
    """
    try:
        if sample_size:
            spark_df = spark_df.limit(sample_size)
        
        pandas_df = spark_df.toPandas()
        logger.info(f"Converted Spark DataFrame to Pandas: {len(pandas_df)} rows")
        
        return pandas_df
    
    except Exception as e:
        logger.error(f"Failed to convert to Pandas: {str(e)}")
        raise


def print_df_info(df, name="DataFrame"):
    """
    Print comprehensive information about a DataFrame
    
    Args:
        df: Spark or Pandas DataFrame
        name (str): Name for logging
    """
    logger.info(f"\n{'='*50}")
    logger.info(f"{name} Information")
    logger.info(f"{'='*50}")
    
    if isinstance(df, DataFrame):  # Spark DataFrame
        logger.info(f"Type: Spark DataFrame")
        logger.info(f"Row count: {df.count()}")
        logger.info(f"Column count: {len(df.columns)}")
        logger.info(f"Columns: {df.columns}")
        logger.info("\nSchema:")
        df.printSchema()
        logger.info("\nSample data:")
        df.show(5, truncate=False)
    
    elif isinstance(df, pd.DataFrame):  # Pandas DataFrame
        logger.info(f"Type: Pandas DataFrame")
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Columns: {df.columns.tolist()}")
        logger.info(f"\nData types:\n{df.dtypes}")
        logger.info(f"\nMissing values:\n{df.isnull().sum()}")
        logger.info(f"\nSample data:\n{df.head()}")
    
    logger.info(f"{'='*50}\n")


def check_null_values(df):
    """
    Check for null values in DataFrame
    
    Args:
        df (DataFrame): Spark DataFrame
    
    Returns:
        dict: Column names and null counts
    """
    null_counts = {}
    
    for column in df.columns:
        null_count = df.filter(col(column).isNull()).count()
        if null_count > 0:
            null_counts[column] = null_count
    
    if null_counts:
        logger.warning(f"Null values found: {null_counts}")
    else:
        logger.info("No null values found")
    
    return null_counts


def get_timestamp():
    """
    Get current timestamp as string
    
    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_model_metadata(model_name, metrics, output_path):
    """
    Save model metadata and metrics to file
    
    Args:
        model_name (str): Name of the model
        metrics (dict): Model performance metrics
        output_path (str): Path to save metadata
    """
    try:
        metadata = {
            'model_name': model_name,
            'timestamp': get_timestamp(),
            'metrics': metrics
        }
        
        import json
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        logger.info(f"Model metadata saved to: {output_path}")
    
    except Exception as e:
        logger.error(f"Failed to save metadata: {str(e)}")


def calculate_percentage(part, whole):
    """
    Calculate percentage
    
    Args:
        part (float): Part value
        whole (float): Whole value
    
    Returns:
        float: Percentage
    """
    if whole == 0:
        return 0
    return round((part / whole) * 100, 2)


# Example usage
if __name__ == "__main__":
    setup_logging("INFO")
    logger.info("Utilities module loaded successfully")
