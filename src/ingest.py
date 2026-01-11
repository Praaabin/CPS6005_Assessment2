"""
Data ingestion utilities for loading GTFS data into HDFS and Spark
"""

import logging
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType
from src.config import HDFS_RAW_PATH, HDFS_PROCESSED_PATH, GTFS_RAW_PATH

logger = logging.getLogger(__name__)


def get_gtfs_schema():
    """
    Define the schema for GTFS data
    
    Returns:
        StructType: Spark schema for GTFS dataset
    """
    schema = StructType([
        StructField("trip_id", StringType(), True),
        StructField("route_id", StringType(), True),
        StructField("stop_id", StringType(), True),
        StructField("stop_sequence", IntegerType(), True),
        StructField("arrival_time", StringType(), True),
        StructField("departure_time", StringType(), True),
        StructField("trip_duration", FloatType(), True),
        StructField("average_speed", FloatType(), True),
        StructField("trip_frequency", IntegerType(), True),
        StructField("service_reliability_index", FloatType(), True),
        StructField("congestion_level", StringType(), True),
        StructField("delay_minutes", FloatType(), True),
    ])
    return schema


def load_csv_to_spark(spark, file_path, schema=None, header=True, infer_schema=False):
    """
    Load CSV file into Spark DataFrame
    
    Args:
        spark (SparkSession): Active Spark session
        file_path (str): Path to CSV file (local or HDFS)
        schema (StructType): Optional schema definition
        header (bool): Whether CSV has header row
        infer_schema (bool): Whether to infer schema automatically
    
    Returns:
        DataFrame: Spark DataFrame
    """
    try:
        logger.info(f"Loading CSV from: {file_path}")
        
        df = spark.read \
            .option("header", str(header).lower()) \
            .option("inferSchema", str(infer_schema).lower()) \
            .option("mode", "PERMISSIVE") \
            .option("columnNameOfCorruptRecord", "_corrupt_record")
        
        if schema:
            df = df.schema(schema)
        
        df = df.csv(file_path)
        
        record_count = df.count()
        logger.info(f"Loaded {record_count} records")
        logger.info(f"Schema: {df.schema}")
        
        return df
    
    except Exception as e:
        logger.error(f"Failed to load CSV: {str(e)}")
        raise


def save_to_hdfs(df, hdfs_path, mode="overwrite", format="parquet"):
    """
    Save Spark DataFrame to HDFS
    
    Args:
        df (DataFrame): Spark DataFrame to save
        hdfs_path (str): HDFS destination path
        mode (str): Write mode (overwrite, append, ignore, error)
        format (str): File format (parquet, csv, json)
    """
    try:
        logger.info(f"Saving DataFrame to HDFS: {hdfs_path}")
        
        df.write \
            .mode(mode) \
            .format(format) \
            .save(hdfs_path)
        
        logger.info(f"Successfully saved to HDFS: {hdfs_path}")
    
    except Exception as e:
        logger.error(f"Failed to save to HDFS: {str(e)}")
        raise


def load_from_hdfs(spark, hdfs_path, format="parquet"):
    """
    Load data from HDFS into Spark DataFrame
    
    Args:
        spark (SparkSession): Active Spark session
        hdfs_path (str): HDFS source path
        format (str): File format (parquet, csv, json)
    
    Returns:
        DataFrame: Spark DataFrame
    """
    try:
        logger.info(f"Loading from HDFS: {hdfs_path}")
        
        df = spark.read \
            .format(format) \
            .load(hdfs_path)
        
        logger.info(f"Loaded {df.count()} records from HDFS")
        
        return df
    
    except Exception as e:
        logger.error(f"Failed to load from HDFS: {str(e)}")
        raise


def ingest_gtfs_data(spark, local_path=None, hdfs_output_path=None):
    """
    Complete ingestion pipeline: Load local CSV -> Save to HDFS
    
    Args:
        spark (SparkSession): Active Spark session
        local_path (str): Local path to GTFS CSV file
        hdfs_output_path (str): HDFS destination path
    
    Returns:
        DataFrame: Loaded Spark DataFrame
    """
    local_path = local_path or str(GTFS_RAW_PATH)
    hdfs_output_path = hdfs_output_path or HDFS_RAW_PATH
    
    logger.info("Starting GTFS data ingestion pipeline")
    
    # Load CSV with schema
    schema = get_gtfs_schema()
    df = load_csv_to_spark(spark, local_path, schema=schema, infer_schema=True)
    
    # Save to HDFS
    save_to_hdfs(df, hdfs_output_path, format="parquet")
    
    logger.info("GTFS data ingestion completed")
    
    return df


# Example usage
if __name__ == "__main__":
    from src.spark_session import create_spark_session, stop_spark_session
    
    logging.basicConfig(level=logging.INFO)
    
    spark = create_spark_session(local_mode=True)
    
    try:
        # Ingest data
        df = ingest_gtfs_data(spark)
        df.show(5)
        df.printSchema()
    finally:
        stop_spark_session(spark)
