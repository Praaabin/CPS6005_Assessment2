# run_all.ps1
# Full Project Execution Script with Error Handling

$ErrorActionPreference = "Stop"

function Check-LastExitCode {
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Command failed with exit code $LASTEXITCODE. Stopping execution."
        exit $LASTEXITCODE
    }
}

Write-Host "=========================================="
Write-Host " 1. STARTING DOCKER STACK"
Write-Host "=========================================="
docker compose up -d
Check-LastExitCode
Start-Sleep -Seconds 15

Write-Host "`n=========================================="
Write-Host " 2. VERIFYING CONTAINERS"
Write-Host "=========================================="
$containers = docker compose ps -q
if (-not $containers) {
    Write-Error "No containers running!"
    exit 1
}
Write-Host "Docker containers are up."

Write-Host "`n=========================================="
Write-Host " 3. UPLOADING DATA TO HDFS"
Write-Host "=========================================="
if (Test-Path "data/raw/gtfs_data.csv") {
    $dataFile = "/data/raw/gtfs_data.csv"
} elseif (Test-Path "data/raw/CPS6005-Assessment 2_GTFS_Data.csv") {
    $dataFile = "/data/raw/CPS6005-Assessment 2_GTFS_Data.csv"
} else {
    Write-Error "Data file not found in data/raw/"
    exit 1
}

# Ensure directories exist (ignoring error if they already exist)
docker exec namenode hdfs dfs -mkdir -p /terraflow/data/raw
docker exec namenode hdfs dfs -mkdir -p /terraflow/data/processed

# Upload file
Write-Host "Uploading $dataFile..."
docker exec namenode hdfs dfs -put -f "$dataFile" /terraflow/data/raw/gtfs_data.csv
Check-LastExitCode

Write-Host "`n=========================================="
Write-Host " 4. INSTALLING DEPENDENCIES"
Write-Host "=========================================="
Write-Host "Installing pip packages in Jupyter container..."
docker cp requirements.txt jupyter-pyspark:/tmp/requirements.txt
docker exec jupyter-pyspark pip install -r /tmp/requirements.txt --no-cache-dir
Check-LastExitCode
# Pyspark version handled in requirements.txt

Write-Host "`n=========================================="
Write-Host " 5. EXECUTING NOTEBOOKS"
Write-Host "=========================================="
$notebooks = @(
    "01_ingest_hdfs_spark.ipynb", 
    "02_clean_features.ipynb", 
    "03_eda_visuals.ipynb", 
    "04_statistics.ipynb", 
    "05_spark_mllib_model.ipynb", 
    "06_export_for_dashboard.ipynb"
)

foreach ($nb in $notebooks) {
    Write-Host "Running $nb ..."
    docker exec jupyter-pyspark jupyter nbconvert --to notebook --execute --inplace "/home/jovyan/work/notebooks/$nb"
    
    # Custom check because nbconvert might return 0 even on cell error depending on config, but usually 1 on error
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to execute $nb. Check the notebook file for error details."
        exit 1
    }
}

Write-Host "`n=========================================="
Write-Host " 6. STARTING DASHBOARD"
Write-Host "=========================================="
Write-Host "Installing host dependencies..."
pip install dash plotly pandas pyarrow -q

Write-Host "`n--------------------------------------------------"
Write-Host "PROJECT RUNNING SUCCESSFULLY"
Write-Host "Dashboard URL: http://localhost:8050"
Write-Host "Jupyter URL:   http://localhost:8888"
Write-Host "Spark Master:  http://localhost:8080"
Write-Host "--------------------------------------------------"
python dashboard/app.py
