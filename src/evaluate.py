import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

def evaluate_model(model, X_val, y_val, model_name):
    """Compute metrics for a model."""
    print(f"Evaluating {model_name}...")
    y_pred = model.predict(X_val)
    
    return {
        'model': model_name,
        'accuracy': accuracy_score(y_val, y_pred),
        'micro_f1': f1_score(y_val, y_pred, average='micro'),
        'macro_f1': f1_score(y_val, y_pred, average='macro'),
        'classification_report': classification_report(y_val, y_pred, output_dict=True),
        'confusion_matrix': confusion_matrix(y_val, y_pred).tolist(),
        'y_pred': y_pred
    }

def plot_confusion_matrix(cm, model_name, save_path):
    """Generate and save confusion matrix heatmap."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Low (1)', 'Medium (2)', 'High (3)'],
                yticklabels=['Low (1)', 'Medium (2)', 'High (3)'])
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.title(f'Confusion Matrix: {model_name}')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_model_comparison(results_df, save_path):
    """Bar chart comparing all models on key metrics."""
    # Melt the dataframe for seaborn barplot
    melted = pd.melt(results_df, id_vars=['model'], value_vars=['accuracy', 'micro_f1', 'macro_f1'],
                     var_name='metric', value_name='score')
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=melted, x='model', y='score', hue='metric')
    plt.title('Model Performance Comparison')
    plt.ylim(0, 1.0)
    
    # Add actual values on bars
    for p in plt.gca().patches:
        plt.gca().annotate(f"{p.get_height():.3f}", 
                           (p.get_x() + p.get_width() / 2., p.get_height()), 
                           ha='center', va='center', xytext=(0, 5), 
                           textcoords='offset points', fontsize=9)
                           
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_feature_importance(model, feature_names, save_path):
    """Plot top-20 feature importance for Random Forest."""
    if not hasattr(model, 'feature_importances_'):
        return
        
    importances = model.feature_importances_
    
    # Generate dummy feature names if they weren't preserved
    if feature_names is None or len(feature_names) != len(importances):
        feature_names = [f"Feature {i}" for i in range(len(importances))]
        
    indices = np.argsort(importances)[::-1][:20] # Top 20
    
    plt.figure(figsize=(12, 8))
    plt.title("Top 20 Feature Importances (Random Forest)")
    plt.bar(range(20), importances[indices], align="center")
    plt.xticks(range(20), [feature_names[i] for i in indices], rotation=90)
    plt.xlim([-1, 20])
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def main():
    print("=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)
    
    # Setup directories
    os.makedirs('results/figures', exist_ok=True)
    os.makedirs('results/metrics', exist_ok=True)
    
    # Load validation data
    try:
        X_val_t, y_val = joblib.load('models/val_data.pkl')
        preprocessor = joblib.load('models/preprocessor.pkl')
    except FileNotFoundError:
        print("ERROR: Validation data or preprocessor not found. Please run src.train first.")
        return
        
    # Get feature names if possible
    try:
        feature_names = preprocessor.get_feature_names_out()
    except:
        feature_names = None
        
    # Load available models
    models = {}
    if os.path.exists('models/knn_model.pkl'):
        models['KNN'] = joblib.load('models/knn_model.pkl')
    if os.path.exists('models/mlp_model.pkl'):
        models['MLP'] = joblib.load('models/mlp_model.pkl')
    if os.path.exists('models/rf_model.pkl'):
        models['Random Forest'] = joblib.load('models/rf_model.pkl')
        
    if not models:
        print("ERROR: No trained models found in models/ directory.")
        return
        
    print(f"Found models: {', '.join(models.keys())}")
    
    # Evaluate each model
    results_list = []
    best_model_name = None
    best_score = 0
    
    for name, model in models.items():
        res = evaluate_model(model, X_val_t, y_val, name)
        
        # Save confusion matrix plot
        plot_confusion_matrix(res['confusion_matrix'], name, f"results/figures/cm_{name.lower().replace(' ', '_')}.png")
        
        # Specific model plots
        if name == 'Random Forest':
            plot_feature_importance(model, feature_names, "results/figures/feature_importance_rf.png")
            
        # Track best model
        if res['micro_f1'] > best_score:
            best_score = res['micro_f1']
            best_model_name = name
            
        # Remove y_pred from dictionary before saving to dataframe
        res.pop('y_pred')
        results_list.append(res)
        
    # Build comparison DataFrame
    summary_data = []
    detailed_metrics = {}
    
    for r in results_list:
        summary_data.append({
            'model': r['model'],
            'accuracy': r['accuracy'],
            'micro_f1': r['micro_f1'],
            'macro_f1': r['macro_f1']
        })
        detailed_metrics[r['model']] = r
        
    df_summary = pd.DataFrame(summary_data)
    
    print("\n--- Evaluation Summary ---")
    print(df_summary.to_string(index=False))
    
    # Save comparison chart
    plot_model_comparison(df_summary, 'results/figures/model_comparison.png')
    
    # Save metrics data
    df_summary.to_csv('results/metrics/comparison.csv', index=False)
    with open('results/metrics/detailed.json', 'w') as f:
        json.dump(detailed_metrics, f, indent=4)
        
    # Save best model logic
    print(f"\n🏆 Best model based on Micro-F1 is: {best_model_name} ({best_score:.4f})")
    
    # Copy best model to best_model.pkl
    import shutil
    best_file_map = {'KNN': 'knn_model.pkl', 'MLP': 'mlp_model.pkl', 'Random Forest': 'rf_model.pkl'}
    src_file = f"models/{best_file_map[best_model_name]}"
    shutil.copy(src_file, 'models/best_model.pkl')
    
    # Save best metadata
    with open('models/model_metadata.json', 'w') as f:
        json.dump({'best_model': best_model_name, 'micro_f1': best_score}, f)
        
    print("Evaluation complete. Results saved to results/")

if __name__ == '__main__':
    main()
