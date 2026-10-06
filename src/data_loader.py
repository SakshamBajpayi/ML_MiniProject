import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

def load_raw_data(data_dir='data/raw'):
    """Load train_values.csv and train_labels.csv, merge on building_id."""
    values_path = os.path.join(data_dir, 'train_values.csv')
    labels_path = os.path.join(data_dir, 'train_labels.csv')
    
    if not os.path.exists(values_path) or not os.path.exists(labels_path):
        raise FileNotFoundError(
            f"Dataset files not found in {data_dir}. "
            "Please ensure 'train_values.csv' and 'train_labels.csv' are downloaded."
        )
        
    print("Loading dataset...")
    values = pd.read_csv(values_path)
    labels = pd.read_csv(labels_path)
    
    # Merge datasets
    df = pd.merge(values, labels, on='building_id')
    return df

def validate_dataset(df):
    """Run validation checks, print summary, raise on failure."""
    # Check shape
    expected_rows = 260601
    assert len(df) == expected_rows, f"Expected {expected_rows} rows, got {len(df)}"
    
    # Check target
    assert 'damage_grade' in df.columns, "Target column 'damage_grade' missing!"
    assert df['damage_grade'].isin([1, 2, 3]).all(), "Target has invalid values (must be 1, 2, or 3)"
    
    # Check duplicates
    assert df['building_id'].nunique() == len(df), "Found duplicate building_ids"
    
    # Check missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f"Warning: Found {missing} missing values in the dataset.")
    
    feature_cols = [c for c in df.columns if c not in ['building_id', 'damage_grade']]
    
    print(f"Dataset validated: {len(df)} rows, {len(feature_cols)} feature columns.")
    
    return {
        'rows': len(df),
        'features': len(feature_cols),
        'missing_values': missing,
        'target_distribution': df['damage_grade'].value_counts(normalize=True).to_dict()
    }

def get_feature_columns(df):
    """Return dict of column groups: numerical, categorical, binary, geo."""
    # Numerical features
    numerical_cols = ['count_floors_pre_eq', 'age', 'area_percentage', 
                      'height_percentage', 'count_families']
    
    # Geo IDs (categorical but represented as ints)
    geo_cols = ['geo_level_1_id', 'geo_level_2_id', 'geo_level_3_id']
    
    # Binary features (0/1)
    binary_cols = [c for c in df.columns if c.startswith('has_')]
    
    # Categorical string features
    categorical_cols = ['land_surface_condition', 'foundation_type', 'roof_type',
                        'ground_floor_type', 'other_floor_type', 'position',
                        'plan_configuration', 'legal_ownership_status']
    
    # Verify all feature columns are accounted for
    all_grouped = set(numerical_cols + geo_cols + binary_cols + categorical_cols)
    all_features = set(c for c in df.columns if c not in ['building_id', 'damage_grade'])
    
    if all_grouped != all_features:
        missing = all_features - all_grouped
        print(f"Warning: Following columns are not assigned to a group: {missing}")
        
    return {
        'numerical': numerical_cols,
        'geo': geo_cols,
        'binary': binary_cols,
        'categorical': categorical_cols
    }

def get_train_val_split(df, test_size=0.2, random_state=42):
    """Stratified train/validation split. Returns X_train, X_val, y_train, y_val."""
    X = df.drop(columns=['building_id', 'damage_grade'])
    y = df['damage_grade']
    
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    return X_train, X_val, y_train, y_val
