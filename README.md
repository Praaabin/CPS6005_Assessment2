# CPS6005 Assessment 2 - TerraFlow Analytics

## Project Overview
This project analyzes large-scale GTFS (General Transit Feed Specification) public transport data to uncover insights into urban mobility patterns, congestion hotspots, and service reliability for TerraFlow Analytics.

## Objectives
- Identify urban congestion hotspots and contributing factors
- Understand temporal variability in transport patterns
- Evaluate service reliability and predict delays
- Assess route efficiency and propose optimizations
- Forecast passenger demand for dynamic scheduling

## Technology Stack
- **Big Data Processing**: PySpark (DataFrames & RDDs)
- **Storage**: HDFS (Hadoop Distributed File System) via Docker
- **Machine Learning**: Spark MLlib
- **Statistical Analysis**: Inferential statistics & Bayesian methods
- **Visualization**: Python (Plotly, Dash, Bokeh) + D3.js
- **Development**: Jupyter Notebooks, Python 3.11+

## Project Structure
```
CPS6005-Assessment2/
├── data/               # Raw and processed datasets
├── notebooks/          # Jupyter notebooks for analysis pipeline
├── src/                # Python source modules
├── dashboard/          # Interactive visualization dashboard
├── docker/             # Docker configurations for HDFS, Spark, Jupyter
└── scripts/            # Automation scripts
```

## Setup Instructions
1. Ensure Docker is installed and running
2. Install Python 3.11+ and required dependencies: `pip install -r requirements.txt`
3. Start the Docker stack: `bash scripts/start_stack.sh`
4. Upload data to HDFS: `bash scripts/upload_to_hdfs.sh`
5. Run analysis notebooks in sequence (01-06)
6. Launch dashboard: `python dashboard/app.py`

## Analysis Pipeline
1. **Data Ingestion** - Load GTFS data into HDFS and Spark
2. **Data Cleaning** - Transform and structure data
3. **EDA & Visualization** - Exploratory data analysis
4. **Statistical Analysis** - Hypothesis testing and Bayesian modeling
5. **Machine Learning** - Predict congestion levels using Spark MLlib
6. **Dashboard** - Interactive visualizations with D3.js

## Author
Prabir - CPS6005 Assessment 2

## License
Academic Project - 2026
