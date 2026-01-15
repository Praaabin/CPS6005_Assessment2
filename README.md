# 🚌 TerraFlow Urban Mobility Analytics

**CPS6005 Assessment 2 - Big Data Analytics**

> **Big Data Pipeline & Interactive Dashboard**: PySpark, HDFS, Machine Learning, and Advanced D3.js Visualizations.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/PySpark-3.3-orange.svg)](https://spark.apache.org/)
[![HDFS](https://img.shields.io/badge/Hadoop%20HDFS-3.2-yellow.svg)](https://hadoop.apache.org/)
[![Dash](https://img.shields.io/badge/Dash-Plotly-success.svg)](https://dash.plotly.com/)
[![D3.js](https://img.shields.io/badge/D3.js-v7-orange.svg)](https://d3js.org/)

---

## 📋 Overview

This project analyzes **66,437 GTFS transport records** to address urban mobility challenges. It features a complete distributed data pipeline (HDFS + Spark) and a professional dashboard for decision-making.

**Key Features:**
*   **Big Data Processing**: Distributed analysis using Apache Spark and HDFS.
*   **Predictive ML**: Random Forest model achieving **85%+ accuracy** for congestion forecasting.
*   **Statistical Rigor**: Bayesian inference and hypothesis testing (t-tests).
*   **Interactive Dashboard**: A premium UI integrating Dash (Plotly) with **Custom D3.js Modules**.
    *   *Route Efficiency Matrix*: Interactive clustering of route performance.
    *   *Congestion Hotspots*: Dynamic temporal heatmaps with metric toggles.

---

## 🚀 QUICK START (3 Steps)

### Step 1: Initialize System
This automated script starts the Docker stack (HDFS, Spark, Jupyter), uploads the raw data, and prepares the environment.

```powershell
cd C:\Users\prabi\OneDrive\Desktop\CPs6005
.\start_project.ps1
```

### Step 2: Execute Analysis Pipeline
Open **[http://localhost:8888](http://localhost:8888)** and run the notebooks in order:
1.  **01_ingest_hdfs_spark.ipynb**: Ingests raw data into HDFS.
2.  **02_clean_features.ipynb**: Cleanses data and engineers features.
3.  **03_eda_visuals.ipynb**: Exploratory Data Analysis (8+ charts).
4.  **04_statistics.ipynb**: Hypothesis testing & Bayesian analysis.
5.  **05_spark_mllib_model.ipynb**: Train/Evaluate Random Forest Model.
6.  **06_export_for_dashboard.ipynb**: Exports processed data for the web app.

### Step 3: Launch Interactive Dashboard
Run the dashboard to visualize the results:

```powershell
cd dashboard
pip install dash plotly pandas pyarrow
python app.py
```
> Access Dashboard: **[http://localhost:8050](http://localhost:8050)**

---

## ✅ Assignment Requirements Met

### 1. Distributed Data Processing (PySpark)
*   **Implementation**: Full usage of Spark Cluster (Master/Worker) for all data transformation.
*   **Features**: Custom Schema definition, RDD mappings, Window functions.

### 2. Scalable Storage (HDFS)
*   **Implementation**: Dockerized Hadoop HDFS.
*   **Data Flow**: Raw CSV → HDFS (`/terraflow/data/raw`) → Spark DataFrames → Parquet.

### 3. Predictive Modelling (Spark MLlib)
*   **Model**: Random Forest Classifier (Depth: 10, Trees: 100).
*   **Outcome**: **85% Accuracy**, effectively predicting "Severe" vs "Smooth" traffic conditions.

### 4. Statistical Analysis
*   **Inferential**: Welch's t-test confirms significant difference between Peak/Off-Peak speeds (p < 0.001).
*   **Bayesian**: Posterior probability analysis reveals a **10.15% risk** of severe congestion during peak hours.

### 5. Interactive Visualization (Python + D3.js)
*   **Requirement**: "Visualise congestion hotspots, route efficiency, and temporal patterns".
*   **Solution**: 
    *   **D3 Route Network**: Force-directed graph with a "Efficiency Matrix" toggle to analyze Speed vs Congestion.
    *   **D3 Heatmap**: Interactive temporal view with "Traffic Volume" vs "Avg Speed" toggles.
    *   **Dash Integration**: Seamlessly embedded alongside Plotly charts.

---

## 📁 Project Structure

```text
CPs6005/
├── dashboard/                  # Web Application
│   ├── app.py                  # Main Dash Application
│   └── assets/
│       ├── d3_route_network.js      # Advanced D3: Network/Efficiency Viz
│       ├── d3_congestion_heatmap.js # Advanced D3: Temporal Heatmap
│       └── styles.css               # Professional Styling
├── data/
│   ├── raw/                    # Raw GTFS Datasets
│   └── processed/              # Dashboard Export Files (Parquet/JSON)
├── notebooks/                  # Jupyter Analysis Notebooks (01-06)
├── docker/                     # Docker Configs
├── scripts/                    # Utility Scripts (HDFS Upload, Stack Start)
├── docker-compose.yml          # Infrastructure Orchestration
├── requirements.txt            # Python Dependencies
└── start_project.ps1           # Automated Setup Script
```

---

## 📊 Key Insights & Results
1.  **Peak Congestion**: The "Severe" congestion probability jumps to **10.15%** during peak windows (7-9 AM, 5-7 PM).
2.  **Critical Routes**: Specific routes (visualized in the D3 Efficiency Matrix) show high volume but low speeds (<20 km/h), marking them as candidates for intervention.
3.  **Predictive Power**: Average speed is the strongest predictor of congestion level (65% feature importance).

---

## 🔧 Troubleshooting
*   **Dashboard No Data?**: Ensure you ran **Notebook 06** to generate the export files in `data/processed/`.
*   **HDFS Errors?**: Run `docker restart namenode` if the connection is lost.
*   **Dependency Issues?**: `pip install -r requirements.txt` (or run Step 3 install command).

---

**Status**: ✅ COMPLETE | **Last Updated**: 2026-01-15
