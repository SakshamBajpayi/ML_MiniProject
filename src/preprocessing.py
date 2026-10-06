import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def build_preprocessor(feature_groups):
    """
    Build a fitted ColumnTransformer based on feature groups.
    
    Args:
        feature_groups: Dict returned by get_feature_columns()
    
    Returns:
        sklearn ColumnTransformer
    """
    # Numerical: StandardScaler
    # Geo IDs: StandardScaler (treating as ordinal integer since there are too many for OneHot)
    # Categorical: OneHotEncoder
    # Binary: passthrough
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), feature_groups['numerical']),
            ('geo', StandardScaler(), feature_groups['geo']),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), feature_groups['categorical']),
            ('bin', 'passthrough', feature_groups['binary'])
        ],
        remainder='drop' # Just to be safe, drop any columns not explicitly handled
    )
    
    return preprocessor

def prepare_data(X_train, X_val, feature_groups):
    """
    Fit preprocessor on X_train, transform both.
    
    Args:
        X_train: Training features DataFrame
        X_val: Validation features DataFrame
        feature_groups: Feature grouping dict
        
    Returns:
        X_train_transformed, X_val_transformed, preprocessor
    """
    preprocessor = build_preprocessor(feature_groups)
    
    # Fit and transform on training data
    print("Fitting preprocessor on training data...")
    X_train_transformed = preprocessor.fit_transform(X_train)
    
    # Transform validation data
    print("Transforming validation data...")
    X_val_transformed = preprocessor.transform(X_val)
    
    # Get feature names if possible (useful for later analysis)
    try:
        feature_names = preprocessor.get_feature_names_out()
        print(f"Total features after preprocessing: {len(feature_names)}")
    except Exception as e:
        print(f"Could not extract feature names: {e}")
        
    return X_train_transformed, X_val_transformed, preprocessor
