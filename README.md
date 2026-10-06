# QUAKESENSE
**Seismic Structural Intelligence Platform**

QuakeSense is an end-to-end machine learning platform engineered to predict earthquake building damage using structural telemetry and geographic data from the 2015 Gorkha earthquake in Nepal. 

The project features a full Python machine learning pipeline, a FastAPI inference backend, and a premium React-based frontend built on an Apple × Palantir design philosophy.

---

## Architecture Overview

* **Machine Learning Core**: Scikit-Learn pipeline featuring One-Hot Encoding and Standard Scaling.
* **Model Topologies**: Evaluated Multi-Layer Perceptron (Neural Network), Random Forest, and K-Nearest Neighbors.
* **Inference Server**: Asynchronous FastAPI service (`uvicorn`) exposing local endpoints.
* **Command Interface**: React 19 + Tailwind CSS + Framer Motion + Recharts.

For a comprehensive explanation of the dataset, class imbalances, ML methodology, and the UI design system, please read the [**Project Guide**](PROJECT_GUIDE.md).

---

## Performance Telemetry (Best Model)

The active inference model is a **Multi-Layer Perceptron (MLP)**. It achieved the highest performance metrics during validation while maintaining a minimal disk footprint and ultra-fast inference speed.

* **Primary Metric (Micro-F1):** 0.686
* **Inference Latency:** ~45ms
* **Disk Footprint:** ~424 KB

---

## Directory Structure

```text
.
├── api/                  # FastAPI inference server (main.py)
├── data/
│   └── raw/              # Raw CSV datasets (train_values.csv, train_labels.csv)
├── docs/                 # Documentation, project guides, and presentation outlines
├── models/               # Serialized models and preprocessors (.pkl)
├── notebooks/            # Jupyter notebooks and EDA scripts
├── results/              # Evaluation metrics and generated visualization figures
├── src/                  # Core ML pipeline (training, evaluation, preprocessing)
├── web/                  # React frontend application (Vite)
├── PROJECT_GUIDE.md      # Comprehensive educational guide
├── README.md             # This document
├── requirements.txt      # Python dependencies
├── setup.sh              # Environment initialization script
└── start.sh              # Launch script for backend API and React UI
```

---

## Deployment & Execution

### 1. Environment Initialization
To set up the Python virtual environment and install all necessary dependencies (including the React frontend node modules):

```bash
chmod +x setup.sh
./setup.sh

# Install frontend dependencies
cd web
npm install
cd ..
```

### 2. Dataset Acquisition
The dataset is provided by DrivenData and must be downloaded manually.
1. Create an account at [DrivenData](https://www.drivendata.org/competitions/57/nepal-earthquake/data/)
2. Download `train_values.csv` and `train_labels.csv`.
3. Place both files in the `data/raw/` directory.

### 3. Model Training & Evaluation
To run the preprocessing pipeline and train the models:
```bash
python -m src.train
```

To evaluate the models and generate performance metrics:
```bash
python -m src.evaluate
```

To generate Exploratory Data Analysis (EDA) visualizations:
```bash
python notebooks/01_eda.py
```

### 4. Launch the Platform
To launch the FastAPI backend and the React Command Interface simultaneously:
```bash
chmod +x start.sh
./start.sh
```
The React frontend will be available at: `http://localhost:5173`

---

## Academic Integrity
This is an academic project. The data is provided by DrivenData, Kathmandu Living Labs, and the Central Bureau of Statistics in Nepal. 
The user interface is designed to present actual model outputs and metrics; no telemetry or predictions are artificially fabricated.
