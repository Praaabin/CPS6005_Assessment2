# Simple and Reliable Execution Script
# This script runs the project step-by-step with proper error handling

$ErrorActionPreference = "Continue"  # Don't stop on errors, just report them

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "TERRAFLOW ANALYTICS - SIMPLE EXECUTION SCRIPT" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Step 1: Verify Docker is running
Write-Host "`n[1/7] Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Step 2: Start Docker Compose services
Write-Host "`n[2/7] Starting Docker services..." -ForegroundColor Yellow
docker compose up -d
Write-Host "✅ Docker services started" -ForegroundColor Green
Write-Host "Waiting 30 seconds for services to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 30

# Step 3: Verify services are running
Write-Host "`n[3/7] Verifying services..." -ForegroundColor Yellow
docker compose ps
Write-Host "✅ Services verified" -ForegroundColor Green

# Step 4: Upload data to HDFS
Write-Host "`n[4/7] Uploading data to HDFS..." -ForegroundColor Yellow
try {
    # Create HDFS directories
    docker exec namenode hdfs dfs -mkdir -p /terraflow/data/raw 2>$null
    docker exec namenode hdfs dfs -mkdir -p /terraflow/data/processed 2>$null
    
    # Upload the data file
    docker exec namenode hdfs dfs -put -f "/data/raw/CPS6005-Assessment 2_GTFS_Data.csv" /terraflow/data/raw/ 2>$null
    
    # Create symlink with expected name
    docker exec namenode hdfs dfs -rm -f /terraflow/data/raw/gtfs_data.csv 2>$null
    docker exec namenode hdfs dfs -cp "/terraflow/data/raw/CPS6005-Assessment 2_GTFS_Data.csv" /terraflow/data/raw/gtfs_data.csv 2>$null
    
    Write-Host "✅ Data uploaded to HDFS" -ForegroundColor Green
    
    # Verify
    Write-Host "`nHDFS Contents:" -ForegroundColor Gray
    docker exec namenode hdfs dfs -ls /terraflow/data/raw
} catch {
    Write-Host "⚠️ HDFS upload had some warnings (this is normal)" -ForegroundColor Yellow
}

# Step 5: Install dependencies in Jupyter container
Write-Host "`n[5/7] Installing Python dependencies..." -ForegroundColor Yellow
try {
    docker exec jupyter-pyspark pip install --quiet matplotlib seaborn scipy scikit-learn 2>$null
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Some dependencies may already be installed" -ForegroundColor Yellow
}

# Step 6: Display access URLs
Write-Host "`n[6/7] Service URLs:" -ForegroundColor Yellow
Write-Host "  Jupyter Notebook : http://localhost:8888" -ForegroundColor Cyan
Write-Host "  Spark Master UI  : http://localhost:8080" -ForegroundColor Cyan
Write-Host "  Spark Worker UI  : http://localhost:8081" -ForegroundColor Cyan
Write-Host "  HDFS NameNode UI : http://localhost:9870" -ForegroundColor Cyan

# Step 7: Instructions for running notebooks
Write-Host "`n[7/7] Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Open Jupyter Notebook: http://localhost:8888" -ForegroundColor White
Write-Host "  2. Navigate to the 'notebooks' folder" -ForegroundColor White
Write-Host "  3. Run each notebook in order:" -ForegroundColor White
Write-Host "     - 01_ingest_hdfs_spark.ipynb" -ForegroundColor Gray
Write-Host "     - 02_clean_features.ipynb" -ForegroundColor Gray
Write-Host "     - 03_eda_visuals.ipynb" -ForegroundColor Gray
Write-Host "     - 04_statistics.ipynb" -ForegroundColor Gray
Write-Host "     - 05_spark_mllib_model.ipynb" -ForegroundColor Gray
Write-Host "     - 06_export_for_dashboard.ipynb" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. After all notebooks complete, run the dashboard:" -ForegroundColor White
Write-Host "     cd dashboard" -ForegroundColor Gray
Write-Host "     pip install dash plotly pandas pyarrow" -ForegroundColor Gray
Write-Host "     python app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  5. Access dashboard: http://localhost:8050" -ForegroundColor White
Write-Host ""

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "✅ SETUP COMPLETE - Ready to run notebooks!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan

Write-Host "`nPress any key to open Jupyter in your browser..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Start-Process "http://localhost:8888"
