$NAMENODE_CONTAINER = "namenode"
$LOCAL_DATA_PATH = "/data/raw/CPS6005-Assessment 2_GTFS_Data.csv"
$HDFS_BASE_PATH = "/terraflow"
$HDFS_RAW_PATH = "$HDFS_BASE_PATH/data/raw"
$HDFS_PROCESSED_PATH = "$HDFS_BASE_PATH/data/processed"

Write-Host "Creating HDFS directory structure..."
docker exec $NAMENODE_CONTAINER hdfs dfs -mkdir -p $HDFS_RAW_PATH
docker exec $NAMENODE_CONTAINER hdfs dfs -mkdir -p $HDFS_PROCESSED_PATH

Write-Host "Uploading CSV file to HDFS..."
# Using quotes for paths with spaces
docker exec $NAMENODE_CONTAINER hdfs dfs -put -f "$LOCAL_DATA_PATH" "$HDFS_RAW_PATH/"

Write-Host "`nVerifying upload..."
docker exec $NAMENODE_CONTAINER hdfs dfs -ls $HDFS_RAW_PATH

Write-Host "`nFile size in HDFS:"
docker exec $NAMENODE_CONTAINER hdfs dfs -du -h $HDFS_RAW_PATH
