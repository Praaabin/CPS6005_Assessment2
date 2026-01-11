"""
Data cleaning and feature engineering for GTFS data
"""

import logging
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, when, hour, dayofweek, to_timestamp,
    unix_timestamp, lit, regexp_replace, trim
)
from pyspark.sql.types import FloatType, IntegerType

logger = logging.getLogger(__name__)


def clean_missing_values(df):
    """
    Handle missing values in the dataset
    
    Args:
        df (DataFrame): Input Spark DataFrame
    
    Returns:
        DataFrame: Cleaned DataFrame
    """
    logger.info("Cleaning missing values...")
    
    # Drop rows with null trip_id or route_id (critical fields)
    df = df.filter(
        col("trip_id").isNotNull() & 
        col("route_id").isNotNull()
    )
    
    # Fill missing numerical values with median/mean
    # This will be implemented based on actual data distribution
    
    logger.info("Missing values handled")
    return df


def extract_temporal_features(df):
    """
    Extract temporal features from timestamp columns
    
    Args:
        df (DataFrame): Input DataFrame
    
    Returns:
        DataFrame: DataFrame with temporal features
    """
    logger.info("Extracting temporal features...")
    
    # Convert time strings to timestamps
    df = df.withColumn(
        "arrival_timestamp",
        to_timestamp(col("arrival_time"), "HH:mm:ss")
    )
    
    df = df.withColumn(
        "departure_timestamp",
        to_timestamp(col("departure_time"), "HH:mm:ss")
    )
    
    # Extract hour of day
    df = df.withColumn("hour_of_day", hour(col("arrival_timestamp")))
    
    # Extract day of week (1 = Sunday, 7 = Saturday)
    df = df.withColumn("day_of_week", dayofweek(col("arrival_timestamp")))
    
    # Create peak hour indicator (7-9 AM, 5-7 PM)
    df = df.withColumn(
        "is_peak_hour",
        when(
            (col("hour_of_day").between(7, 9)) | 
            (col("hour_of_day").between(17, 19)),
            lit(1)
        ).otherwise(lit(0))
    )
    
    logger.info("Temporal features extracted")
    return df


def encode_congestion_level(df):
    """
    Encode congestion level as numerical values
    
    Args:
        df (DataFrame): Input DataFrame
    
    Returns:
        DataFrame: DataFrame with encoded congestion levels
    """
    logger.info("Encoding congestion levels...")
    
    df = df.withColumn(
        "congestion_encoded",
        when(col("congestion_level") == "low", lit(0))
        .when(col("congestion_level") == "moderate", lit(1))
        .when(col("congestion_level") == "high", lit(2))
        .otherwise(lit(None))
    )
    
    logger.info("Congestion levels encoded")
    return df


def create_derived_features(df):
    """
    Create derived features for analysis
    
    Args:
        df (DataFrame): Input DataFrame
    
    Returns:
        DataFrame: DataFrame with derived features
    """
    logger.info("Creating derived features...")
    
    # Speed category
    df = df.withColumn(
        "speed_category",
        when(col("average_speed") < 20, lit("slow"))
        .when(col("average_speed").between(20, 40), lit("medium"))
        .otherwise(lit("fast"))
    )
    
    # Reliability category
    df = df.withColumn(
        "reliability_category",
        when(col("service_reliability_index") < 0.5, lit("poor"))
        .when(col("service_reliability_index").between(0.5, 0.8), lit("moderate"))
        .otherwise(lit("good"))
    )
    
    logger.info("Derived features created")
    return df


def clean_and_transform(df):
    """
    Complete cleaning and transformation pipeline
    
    Args:
        df (DataFrame): Raw input DataFrame
    
    Returns:
        DataFrame: Cleaned and transformed DataFrame
    """
    logger.info("Starting data cleaning and transformation pipeline")
    
    # Clean missing values
    df = clean_missing_values(df)
    
    # Extract temporal features
    df = extract_temporal_features(df)
    
    # Encode categorical variables
    df = encode_congestion_level(df)
    
    # Create derived features
    df = create_derived_features(df)
    
    logger.info("Data cleaning and transformation completed")
    
    return df


# Example usage
if __name__ == "__main__":
    from src.spark_session import create_spark_session, stop_spark_session
    from src.ingest import load_from_hdfs
    
    logging.basicConfig(level=logging.INFO)
    
    spark = create_spark_session(local_mode=True)
    
    try:
        # Load data
        df = load_from_hdfs(spark, "hdfs://namenode:9000/terraflow/data/raw")
        
        # Clean and transform
        df_clean = clean_and_transform(df)
        
        df_clean.show(5)
        df_clean.printSchema()
    finally:
        stop_spark_session(spark)
