#!/bin/bash
# Earthquake Building Damage Prediction - Setup Script

echo "=========================================================="
echo "      Earthquake Damage Prediction ML Project Setup       "
echo "=========================================================="

echo "[1/3] Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt
echo "Environment setup complete."

echo ""
echo "[2/3] Checking for dataset..."
if [ -f "data/raw/train_values.csv" ] && [ -f "data/raw/train_labels.csv" ]; then
    echo "Dataset found in data/raw/!"
else
    echo "Dataset NOT FOUND."
    echo "To download the dataset:"
    echo "1. Go to: https://www.drivendata.org/competitions/57/nepal-earthquake/data/"
    echo "2. Create a free account or log in."
    echo "3. Download 'train_values.csv' and 'train_labels.csv'."
    echo "4. Place both files in the 'data/raw/' directory of this project."
    echo "Alternatively, you can find the dataset on Kaggle: https://www.kaggle.com/competitions/richter-predictor/data"
fi

echo ""
echo "[3/3] Directory structure verified."
mkdir -p data/raw data/processed notebooks src models results/figures results/metrics app docs

echo "=========================================================="
echo "Setup complete! Please ensure data is downloaded before running the code."
echo "=========================================================="
