import time
import json
import joblib
import os
import argparse
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
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


class XGBWrapper:
    def __init__(self, model, le):
        self.model = model
        self.le = le
        self.classes_ = le.classes_
        
    def predict(self, X):
        preds = self.model.predict(X)
        return self.le.inverse_transform(preds)
        
    def predict_proba(self, X):
        return self.model.predict_proba(X)
        
    @property
    def feature_importances_(self):
        return self.model.feature_importances_

def train_xgb(X_train, y_train):
    """Train XGBoost classifier with expanded hyperparameter tuning."""
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score
    from xgboost import XGBClassifier
    import numpy as np
    
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    
    # Subsample for tuning to keep it fast
    print("  Subsampling training data for XGBoost tuning (50k rows)...")
    np.random.seed(RANDOM_STATE)
    idx = np.random.choice(len(X_train), 50000, replace=False)
    X_tune, y_tune = X_train[idx], y_train_encoded[idx]
    
    X_t, X_v, y_t, y_v = train_test_split(X_tune, y_tune, test_size=0.2, random_state=RANDOM_STATE)
    
    configs = [
        {'n_estimators': 150, 'max_depth': 8, 'learning_rate': 0.1, 'subsample': 0.9},
        {'n_estimators': 250, 'max_depth': 12, 'learning_rate': 0.05, 'subsample': 0.8},
        {'n_estimators': 350, 'max_depth': 12, 'learning_rate': 0.03, 'subsample': 0.8, 'min_child_weight': 3},
        {'n_estimators': 300, 'max_depth': 10, 'learning_rate': 0.05, 'subsample': 0.8, 'min_child_weight': 5},
        {'n_estimators': 400, 'max_depth': 14, 'learning_rate': 0.02, 'subsample': 0.7, 'min_child_weight': 3}
    ]
    
    best_f1 = 0
    best_config = configs[0]
    
    print("  Starting extended XGBoost tuning...")
    for idx, config in enumerate(configs):
        model = XGBClassifier(**config, colsample_bytree=0.8, random_state=RANDOM_STATE, n_jobs=-1)
        model.fit(X_t, y_t)
        preds = model.predict(X_v)
        f1 = f1_score(y_v, preds, average='micro')
        print(f"  Config {idx+1} {config}: Validation Micro-F1 = {f1:.4f}")
        if f1 > best_f1:
            best_f1 = f1
            best_config = config
            
    print(f"  Best config: {best_config}")
    print("  Training final XGBoost on full training set...")
    
    final_model = XGBClassifier(**best_config, colsample_bytree=0.8, random_state=RANDOM_STATE, n_jobs=-1)
    final_model.fit(X_train, y_train_encoded)
    
    # Check for overfitting
    train_preds = final_model.predict(X_train)
    train_f1 = f1_score(y_train_encoded, train_preds, average='micro')
    print(f"  Final XGBoost Training Micro-F1: {train_f1:.4f}")
    
    wrapped_model = XGBWrapper(final_model, le)
    return wrapped_model, best_config

def train_rf(X_train, y_train):
    """Train Random Forest with hyperparameter tuning."""
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score
    import numpy as np
    
    print("  Subsampling training data for RF tuning (50k rows)...")
    np.random.seed(RANDOM_STATE)
    idx = np.random.choice(len(X_train), 50000, replace=False)
    X_tune, y_tune = X_train[idx], y_train.iloc[idx]
    
    X_t, X_v, y_t, y_v = train_test_split(X_tune, y_tune, test_size=0.2, random_state=RANDOM_STATE)
    
    configs = [
        {'n_estimators': 150, 'max_depth': 15, 'min_samples_split': 5},
        {'n_estimators': 250, 'max_depth': 20, 'min_samples_split': 5},
        {'n_estimators': 200, 'max_depth': None, 'min_samples_split': 10},
        {'n_estimators': 250, 'max_depth': None, 'min_samples_split': 5}
    ]
    
    best_f1 = 0
    best_config = configs[0]
    
    print("  Starting extended RF tuning...")
    for idx, config in enumerate(configs):
        model = RandomForestClassifier(**config, min_samples_leaf=2, max_features='sqrt', class_weight='balanced', random_state=RANDOM_STATE, n_jobs=-1, verbose=0)
        model.fit(X_t, y_t)
        preds = model.predict(X_v)
        f1 = f1_score(y_v, preds, average='micro')
        print(f"  Config {idx+1} {config}: Validation Micro-F1 = {f1:.4f}")
        if f1 > best_f1:
            best_f1 = f1
            best_config = config
            
    print(f"  Best config: {best_config}")
    print("  Training final RF on full training set...")
    
    final_model = RandomForestClassifier(**best_config, min_samples_leaf=2, max_features='sqrt', class_weight='balanced', random_state=RANDOM_STATE, n_jobs=-1, verbose=0)
    final_model.fit(X_train, y_train)
    
    train_preds = final_model.predict(X_train)
    train_f1 = f1_score(y_train, train_preds, average='micro')
    print(f"  Final RF Training Micro-F1: {train_f1:.4f}")
    return final_model, best_config

def main():
    parser = argparse.ArgumentParser(description='Train models for Earthquake Damage Prediction')
    parser.add_argument('--models', type=str, default='rf', 
                        help='Comma separated list of models to train: knn,mlp,rf,xgb. Default: rf')
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
        

    if 'xgb' in models_to_train:
        print("\n[Training XGBoost...]")
        start = time.time()
        xgb_model, xgb_params = train_xgb(X_train_t, y_train)
        elapsed = time.time() - start
        print(f"✓ XGB trained in {elapsed:.1f}s")
        joblib.dump(xgb_model, 'models/xgb_model.pkl')
        trained_models.append('xgb')

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
