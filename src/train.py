import time
import json
import joblib
import os
import argparse
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

from src.data_loader import load_raw_data, validate_dataset, get_feature_columns, get_train_val_split
from src.preprocessing import prepare_data

RANDOM_STATE = 42

def train_knn(X_train, y_train):
    """Train KNN with lightweight hyperparameter search."""
    best_score = 0
    best_k = 15
    
    # We will just test a couple of k values to save time on large datasets
    k_values = [11, 21] 
    
    # If the dataset is very large, subsample for tuning to save time
    if len(X_train) > 100000:
        print("  Subsampling training data for KNN tuning (100k rows)...")
        # Subsample indices
        import numpy as np
        np.random.seed(RANDOM_STATE)
        idx = np.random.choice(len(X_train), 100000, replace=False)
        X_tune, y_tune = X_train[idx], y_train.iloc[idx]
    else:
        X_tune, y_tune = X_train, y_train
        
    for k in k_values:
        # ball_tree is generally faster for larger dimensions and size than brute
        knn = KNeighborsClassifier(n_neighbors=k, weights='distance', 
                                   algorithm='ball_tree', n_jobs=-1)
        scores = cross_val_score(knn, X_tune, y_tune, cv=2, 
                                 scoring='f1_micro', n_jobs=-1)
        mean_score = scores.mean()
        print(f"  KNN k={k}: CV Micro-F1 = {mean_score:.4f}")
        if mean_score > best_score:
            best_score = mean_score
            best_k = k
            
    print(f"  Training final KNN with k={best_k} on full training set...")
    model = KNeighborsClassifier(n_neighbors=best_k, weights='distance',
                                 algorithm='ball_tree', n_jobs=-1)
    model.fit(X_train, y_train)
    return model, {'n_neighbors': best_k, 'cv_micro_f1_tune': best_score}

def train_mlp(X_train, y_train):
    """Train MLP neural network."""
    # (128, 64) architecture based on plan
    model = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation='relu',
        solver='adam',
        learning_rate='adaptive',
        learning_rate_init=0.001,
        max_iter=200,
        early_stopping=True,
        validation_fraction=0.1,
        batch_size=256,
        random_state=RANDOM_STATE,
        verbose=False # Set to True if you want to see epoch progress
    )
    model.fit(X_train, y_train)
    return model, {'hidden_layers': '(128, 64)', 'epochs': model.n_iter_}

def train_rf(X_train, y_train):
    """Train Random Forest with standard parameters."""
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        class_weight='balanced',
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=0
    )
    model.fit(X_train, y_train)
    return model, {'n_estimators': 200, 'max_depth': 'None'}

def main():
    parser = argparse.ArgumentParser(description='Train models for Earthquake Damage Prediction')
    parser.add_argument('--models', type=str, default='rf', 
                        help='Comma separated list of models to train: knn,mlp,rf. Default: rf')
    args = parser.parse_args()
    
    models_to_train = [m.strip().lower() for m in args.models.split(',')]
    
    print("=" * 60)
    print("MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    # 1. Load Data
    try:
        df = load_raw_data()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return
        
    # 2. Validate
    validate_dataset(df)
    
    # 3. Get feature columns and Split
    feature_groups = get_feature_columns(df)
    X_train, X_val, y_train, y_val = get_train_val_split(df)
    
    print(f"\nTraining set: {X_train.shape[0]} rows")
    print(f"Validation set: {X_val.shape[0]} rows")
    
    # 4. Preprocess
    print("\nStarting preprocessing...")
    X_train_t, X_val_t, preprocessor = prepare_data(X_train, X_val, feature_groups)
    
    # Save preprocessor
    os.makedirs('models', exist_ok=True)
    joblib.dump(preprocessor, 'models/preprocessor.pkl')
    print("✓ Preprocessor saved to models/preprocessor.pkl")
    
    # Save validation data for evaluate.py
    joblib.dump((X_val_t, y_val), 'models/val_data.pkl')
    
    # 5. Train models
    print("\n--- Training Models ---")
    trained_models = []
    
    if 'knn' in models_to_train:
        print("\n[Training KNN...]")
        start = time.time()
        knn_model, knn_params = train_knn(X_train_t, y_train)
        elapsed = time.time() - start
        print(f"✓ KNN trained in {elapsed:.1f}s")
        joblib.dump(knn_model, 'models/knn_model.pkl')
        trained_models.append('knn')
        
    if 'mlp' in models_to_train:
        print("\n[Training MLP...]")
        start = time.time()
        mlp_model, mlp_params = train_mlp(X_train_t, y_train)
        elapsed = time.time() - start
        print(f"✓ MLP trained in {elapsed:.1f}s ({mlp_params['epochs']} epochs)")
        joblib.dump(mlp_model, 'models/mlp_model.pkl')
        trained_models.append('mlp')
        
    if 'rf' in models_to_train:
        print("\n[Training Random Forest...]")
        start = time.time()
        rf_model, rf_params = train_rf(X_train_t, y_train)
        elapsed = time.time() - start
        print(f"✓ RF trained in {elapsed:.1f}s")
        joblib.dump(rf_model, 'models/rf_model.pkl')
        trained_models.append('rf')
        
    print("\n==========================================================")
    print(f"Training complete. Saved {len(trained_models)} models to models/")
    print("Next step: Run `python -m src.evaluate` to evaluate models.")
    print("==========================================================")

if __name__ == '__main__':
    main()
