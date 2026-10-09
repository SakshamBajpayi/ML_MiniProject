import joblib
import pandas as pd
import json
import os
import time
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

import src.evaluate
from src.evaluate import XGBWrapper
import __main__
__main__.XGBWrapper = XGBWrapper

def main():
    print("Evaluating XGBoost only...")
    try:
        X_val_t, y_val = joblib.load('models/val_data.pkl')
    except Exception as e:
        print("Error:", e)
        return

    model = joblib.load('models/xgb_model.pkl')
    
    start = time.time()
    preds = model.predict(X_val_t)
    print("Inference took:", time.time() - start)
    
    acc = accuracy_score(y_val, preds)
    micro_f1 = f1_score(y_val, preds, average='micro')
    macro_f1 = f1_score(y_val, preds, average='macro')
    
    report = classification_report(y_val, preds, output_dict=True)
    cm = confusion_matrix(y_val, preds).tolist()
    
    xgb_results = {
        'model': 'XGBoost',
        'accuracy': acc,
        'micro_f1': micro_f1,
        'macro_f1': macro_f1,
        'classification_report': report,
        'confusion_matrix': cm
    }
    
    print("XGBoost F1:", micro_f1)
    
    # Update detailed.json
    with open('results/metrics/detailed.json', 'r') as f:
        detailed = json.load(f)
        
    detailed['XGBoost'] = xgb_results
    
    with open('results/metrics/detailed.json', 'w') as f:
        json.dump(detailed, f, indent=4)
        
    # Update comparison.csv
    import csv
    with open('results/metrics/comparison.csv', 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    for row in rows:
        if row['model'] == 'XGBoost':
            row['accuracy'] = acc
            row['micro_f1'] = micro_f1
            row['macro_f1'] = macro_f1
            
    with open('results/metrics/comparison.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['model', 'accuracy', 'micro_f1', 'macro_f1'])
        writer.writeheader()
        writer.writerows(rows)
        
    print("Metrics updated.")

if __name__ == '__main__':
    main()
