#!/bin/bash
# Upload GTFS data to HDFS

echo "Uploading GTFS data to HDFS..."
echo "=============================================="

# Configuration
NAMENODE_CONTAINER="namenode"
LOCAL_DATA_PATH="/data/raw/CPS6005-Assessment 2_GTFS_Data.csv"
HDFS_BASE_PATH="/terraflow"
HDFS_RAW_PATH="${HDFS_BASE_PATH}/data/raw"
HDFS_PROCESSED_PATH="${HDFS_BASE_PATH}/data/processed"

# Create HDFS directories
echo "Creating HDFS directory structure..."
docker exec $NAMENODE_CONTAINER hdfs dfs -mkdir -p $HDFS_RAW_PATH
docker exec $NAMENODE_CONTAINER hdfs dfs -mkdir -p $HDFS_PROCESSED_PATH

# Upload CSV file
echo "Uploading CSV file to HDFS..."
docker exec $NAMENODE_CONTAINER hdfs dfs -put -f $LOCAL_DATA_PATH $HDFS_RAW_PATH/

# Verify upload
echo ""
echo "Verifying upload..."
docker exec $NAMENODE_CONTAINER hdfs dfs -ls $HDFS_RAW_PATH

echo ""
echo "File size in HDFS:"
docker exec $NAMENODE_CONTAINER hdfs dfs -du -h $HDFS_RAW_PATH

echo ""
echo "Upload completed successfully!"
echo "HDFS path: ${HDFS_RAW_PATH}/CPS6005-Assessment 2_GTFS_Data.csv"
