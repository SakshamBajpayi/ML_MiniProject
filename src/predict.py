import joblib
import pandas as pd
import os

def predict_single(features_dict, model_path='models/best_model.pkl',
                   preprocessor_path='models/preprocessor.pkl'):
    """
    Accept a dict of raw feature values, return prediction and probabilities.
    
    Returns:
        dict with keys: damage_grade, interpretation, probabilities
    """
    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        raise FileNotFoundError(
            f"Model or preprocessor not found at {model_path}, {preprocessor_path}. "
            "Please run train.py and evaluate.py first."
        )
        
    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)
    
    # Ensure all required features are present, fill missing with defaults if needed
    # But ideally features_dict is complete
    df = pd.DataFrame([features_dict])
    
    try:
        X = preprocessor.transform(df)
    except Exception as e:
        raise ValueError(f"Error preprocessing features: {e}. Ensure all features are provided.")
    
    pred = model.predict(X)[0]
    
    interpretations = {
        1: 'Low Damage', 
        2: 'Medium Damage', 
        3: 'Almost Complete Destruction'
    }
    
    result = {
        'damage_grade': int(pred),
        'interpretation': interpretations.get(pred, "Unknown"),
    }
    
    # Return probabilities if supported by the model (e.g. RF, MLP)
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(X)[0]
        # Match probabilities to classes (usually [1, 2, 3])
        classes = model.classes_
        result['probabilities'] = {f'Grade {cls}': float(p) for cls, p in zip(classes, proba)}
        
    return result

if __name__ == '__main__':
    # Simple test stub
    print("Test prediction stub.")
    print("Usage: import predict_single from this module.")
