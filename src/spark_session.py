"""
Spark Session initialization and configuration
"""

from pyspark.sql import SparkSession
from pyspark import SparkConf
import logging
from src.config import (
    SPARK_MASTER_URL, SPARK_APP_NAME,
    SPARK_EXECUTOR_MEMORY, SPARK_DRIVER_MEMORY,
    SPARK_EXECUTOR_CORES, HDFS_URL
)

logger = logging.getLogger(__name__)


def create_spark_session(app_name=SPARK_APP_NAME, master=None, local_mode=False):
    """
    Create and configure a Spark session for TerraFlow Analytics
    
    Args:
        app_name (str): Name of the Spark application
        master (str): Spark master URL (None for auto-detection)
        local_mode (bool): If True, run in local mode for testing
    
    Returns:
        SparkSession: Configured Spark session
    """
    try:
        # Configure Spark
        conf = SparkConf()
        conf.setAppName(app_name)
        
        if local_mode:
            conf.setMaster("local[*]")
            logger.info("Running Spark in local mode")
        elif master:
            conf.setMaster(master)
        else:
            conf.setMaster(SPARK_MASTER_URL)
        
        # Set memory and core configurations
        conf.set("spark.executor.memory", SPARK_EXECUTOR_MEMORY)
        conf.set("spark.driver.memory", SPARK_DRIVER_MEMORY)
        conf.set("spark.executor.cores", str(SPARK_EXECUTOR_CORES))
        
        # HDFS configuration
        conf.set("spark.hadoop.fs.defaultFS", HDFS_URL)
        
        # Performance optimizations
        conf.set("spark.sql.adaptive.enabled", "true")
        conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
        conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        
        # Create Spark session
        spark = SparkSession.builder \
            .config(conf=conf) \
            .enableHiveSupport() \
            .getOrCreate()
        
        # Set log level
        spark.sparkContext.setLogLevel("WARN")
        
        logger.info(f"Spark session created: {app_name}")
        logger.info(f"Spark version: {spark.version}")
        logger.info(f"Master: {spark.sparkContext.master}")
        
        return spark
    
    except Exception as e:
        logger.error(f"Failed to create Spark session: {str(e)}")
        raise


def stop_spark_session(spark):
    """
    Stop the Spark session gracefully
    
    Args:
        spark (SparkSession): Spark session to stop
    """
    try:
        if spark:
            spark.stop()
            logger.info("Spark session stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping Spark session: {str(e)}")


def get_spark_context(spark):
    """
    Get the Spark context from a Spark session
    
    Args:
        spark (SparkSession): Active Spark session
    
    Returns:
        SparkContext: Spark context
    """
    return spark.sparkContext


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create Spark session
    spark = create_spark_session(local_mode=True)
    
    # Test the session
    print(f"Spark UI available at: {spark.sparkContext.uiWebUrl}")
    
    # Stop session
    stop_spark_session(spark)
