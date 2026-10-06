# Agent Execution Playbook — Earthquake Damage Prediction Project

> This document is the **operational execution guide** for building the project. While `plans.md` defines *what* to build, this document defines *how* to build it — exact file contents, implementation order, subagent delegation, quality gates, and error recovery.

---

## 1. Execution Identity

| Field | Value |
|---|---|
| **Agent Role** | Primary Implementation Agent |
| **Project Root** | `/home/pigasso/Projects/ml_project` |
| **Artifact Dir** | `/home/pigasso/.gemini/antigravity-cli/brain/9f704023-1048-4f06-a046-2250f92d1313` |
| **Python** | 3.14.7 (system) |
| **OS** | Linux |
| **Repo State** | Empty — greenfield build |

---

## 2. Subagent Delegation Strategy

### 2.1 Parallelizable Work

The following tasks are **independent** and can be delegated to subagents running in parallel:

| Batch | Tasks | Agent Type |
|---|---|---|
| **Batch A** (after Phase 1) | EDA notebook creation | `self` subagent |
| **Batch B** (after Phase 5) | KNN implementation, MLP implementation, RF implementation | Could be parallelized but sequential is safer for shared preprocessing |
| **Batch C** (after Phase 8) | Streamlit app, Report writing, Presentation outline | 3 × `self` subagents |

### 2.2 Sequential Tasks (must not be parallelized)

1. Repository scaffolding → dataset acquisition → dataset validation → preprocessing
2. Model training → evaluation → best model selection
3. Verification (depends on everything)

### 2.3 Recommended Execution Flow

```
Phase 1 (Scaffolding)          ← Agent does directly
     ↓
Phase 2 (Dataset)              ← Agent does directly
     ↓
Phase 3 (Validation)           ← Agent does directly
     ↓
┌────────────────────────────┐
│ Phase 4 (EDA)              │ ← Can delegate to subagent
│ Phase 5 (Preprocessing)    │ ← Agent does directly (critical path)
└────────────────────────────┘
     ↓
Phase 6 (Models)              ← Agent does directly (sequential: KNN → MLP → RF)
     ↓
Phase 7 (Evaluation)          ← Agent does directly
     ↓
Phase 8 (Best Model)          ← Agent does directly
     ↓
┌────────────────────────────┐
│ Phase 9 (Demo App)         │ ← Can delegate to subagent
│ Phase 10a (README)         │ ← Agent does directly (needs final metrics)
│ Phase 10b (Report)         │ ← Can delegate to subagent
│ Phase 10c (Presentation)   │ ← Can delegate to subagent
└────────────────────────────┘
     ↓
Phase 11 (Verification)       ← Agent does directly
```

---

## 3. File-by-File Implementation Specification

### 3.1 `.gitignore`

```gitignore
# Data files
data/raw/*.csv
data/processed/

# Model artifacts
models/*.pkl
models/*.joblib

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Jupyter
.ipynb_checkpoints/

# Results (keep figures, ignore large files)
results/metrics/*.json
```

### 3.2 `requirements.txt`

```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
joblib>=1.3.0
streamlit>=1.28.0
```

### 3.3 `src/__init__.py`

Empty file. Makes `src` a Python package so `python -m src.train` works.

### 3.4 `src/data_loader.py`

**Purpose**: Load, validate, and merge the dataset.

**Functions to implement**:
```python
def load_raw_data(data_dir='data/raw'):
    """Load train_values.csv and train_labels.csv, merge on building_id."""
    # Returns merged DataFrame
    
def validate_dataset(df):
    """Run validation checks, print summary, raise on failure."""
    # Check shape, columns, dtypes, missing values, target distribution
    # Return validation report dict

def get_feature_columns():
    """Return dict of column groups: numerical, categorical, binary, geo."""
    
def get_train_val_split(df, test_size=0.2, random_state=42):
    """Stratified train/validation split. Returns X_train, X_val, y_train, y_val."""
```

**Key implementation details**:
- Merge is `pd.merge(train_values, train_labels, on='building_id')`
- Drop `building_id` from features after merge
- Stratify split on `damage_grade`
- Return feature names as module-level constants

### 3.5 `src/preprocessing.py`

**Purpose**: Build sklearn preprocessing pipeline.

**Functions to implement**:
```python
def build_preprocessor():
    """Return a fitted ColumnTransformer."""
    # Numerical: StandardScaler
    # Categorical: OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    # Binary: passthrough
    # Geo IDs: passthrough (kept as integers)
    
def prepare_data(X_train, X_val):
    """Fit preprocessor on X_train, transform both. Return X_train_t, X_val_t, preprocessor."""
```

**Design**:
```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

NUMERICAL_COLS = ['count_floors_pre_eq', 'age', 'area_percentage', 
                  'height_percentage', 'count_families']
GEO_COLS = ['geo_level_1_id', 'geo_level_2_id', 'geo_level_3_id']
CATEGORICAL_COLS = ['land_surface_condition', 'foundation_type', 'roof_type',
                    'ground_floor_type', 'other_floor_type', 'position',
                    'plan_configuration', 'legal_ownership_status']
BINARY_COLS = [col for col in df.columns if col.startswith('has_')]

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), NUMERICAL_COLS),
    ('geo', StandardScaler(), GEO_COLS),  
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL_COLS),
    ('bin', 'passthrough', BINARY_COLS)
])
```

> [!IMPORTANT]
> `geo_level_3_id` has 12,567 unique values. Do NOT one-hot encode it. StandardScaler is fine — treats it as ordinal integer, which is acceptable for KNN/MLP distance metrics. For RF, scaling doesn't matter.

### 3.6 `src/train.py`

**Purpose**: Train all three models, save artifacts.

**Structure**:
```python
import time
import json
import joblib
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

RANDOM_STATE = 42

def train_knn(X_train, y_train):
    """Train KNN with lightweight hyperparameter search."""
    best_score = 0
    best_k = 15
    for k in [5, 11, 15, 21, 25]:
        knn = KNeighborsClassifier(n_neighbors=k, weights='distance', 
                                     algorithm='ball_tree', n_jobs=-1)
        scores = cross_val_score(knn, X_train, y_train, cv=3, 
                                  scoring='f1_micro', n_jobs=-1)
        mean_score = scores.mean()
        print(f"  KNN k={k}: CV Micro-F1 = {mean_score:.4f}")
        if mean_score > best_score:
            best_score = mean_score
            best_k = k
    
    # Train final model with best k
    model = KNeighborsClassifier(n_neighbors=best_k, weights='distance',
                                   algorithm='ball_tree', n_jobs=-1)
    model.fit(X_train, y_train)
    return model, {'n_neighbors': best_k, 'cv_micro_f1': best_score}

def train_mlp(X_train, y_train):
    """Train MLP neural network."""
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
        verbose=True
    )
    model.fit(X_train, y_train)
    return model, {'hidden_layers': '(128, 64)', 'epochs': model.n_iter_}

def train_rf(X_train, y_train):
    """Train Random Forest with lightweight tuning."""
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        class_weight='balanced',
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1
    )
    model.fit(X_train, y_train)
    return model, {'n_estimators': 200, 'max_depth': 'None'}

def main():
    # 1. Load data
    # 2. Validate
    # 3. Split
    # 4. Preprocess
    # 5. Train each model with timing
    # 6. Save models and preprocessor to models/
    # 7. Print summary
```

**Timing pattern** (use for each model):
```python
start = time.time()
model, params = train_knn(X_train_transformed, y_train)
elapsed = time.time() - start
print(f"KNN trained in {elapsed:.1f}s")
```

**Saving pattern**:
```python
joblib.dump(model, 'models/knn_model.pkl')
joblib.dump(model, 'models/mlp_model.pkl')
joblib.dump(model, 'models/rf_model.pkl')
joblib.dump(preprocessor, 'models/preprocessor.pkl')
```

### 3.7 `src/evaluate.py`

**Purpose**: Load saved models, evaluate on validation set, generate all plots and metrics.

**Functions**:
```python
def evaluate_model(model, X_val, y_val, model_name):
    """Compute all metrics for a single model."""
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

def plot_model_comparison(results_list, save_path):
    """Bar chart comparing all models on key metrics."""

def plot_feature_importance(model, feature_names, save_path):
    """Top-20 feature importance for Random Forest."""

def main():
    # 1. Load validation data + preprocessor
    # 2. Load all 3 models
    # 3. Evaluate each
    # 4. Generate plots
    # 5. Save comparison CSV
    # 6. Identify best model → copy to models/best_model.pkl
    # 7. Save model_metadata.json
```

### 3.8 `src/predict.py`

**Purpose**: Load best model, predict on single sample.

```python
def predict_single(features_dict, model_path='models/best_model.pkl',
                   preprocessor_path='models/preprocessor.pkl'):
    """
    Accept a dict of raw feature values, return prediction and probabilities.
    
    Returns:
        dict with keys: damage_grade, interpretation, probabilities
    """
    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)
    
    df = pd.DataFrame([features_dict])
    X = preprocessor.transform(df)
    
    pred = model.predict(X)[0]
    
    interpretations = {1: 'Low Damage', 2: 'Medium Damage', 3: 'Almost Complete Destruction'}
    
    result = {
        'damage_grade': int(pred),
        'interpretation': interpretations[pred],
    }
    
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(X)[0]
        result['probabilities'] = {f'Grade {i+1}': float(p) for i, p in enumerate(proba)}
    
    return result
```

### 3.9 `app/streamlit_app.py`

**Purpose**: Interactive demo for live presentation.

**Layout**:
```
┌──────────────────────────────────────────────┐
│  🏗️ Earthquake Building Damage Predictor     │
│  Predict damage from the 2015 Gorkha quake   │
├────────────┬─────────────────────────────────┤
│ SIDEBAR    │  MAIN AREA                      │
│            │                                  │
│ Floors: [3]│  Predicted Damage Grade: 2      │
│ Age: [25]  │  ■■■■■■■■■■ MEDIUM DAMAGE       │
│ Area: [8]  │                                  │
│ Height:[5] │  Confidence: 73.2%              │
│ Surface:[▼]│                                  │
│ Found: [▼] │  ┌──────────────────────┐       │
│ Roof:  [▼] │  │ Probability Chart    │       │
│ ...        │  │ Grade 1: ████ 12%    │       │
│            │  │ Grade 2: ████████ 73%│       │
│ [Predict]  │  │ Grade 3: ███ 15%     │       │
│            │  └──────────────────────┘       │
└────────────┴─────────────────────────────────┘
```

**Implementation notes**:
- Use `@st.cache_resource` to load model once
- Provide sensible default values for all features
- Color-code damage grades: green (1), orange (2), red (3)
- Show probability distribution as horizontal bar chart
- Handle features not shown in UI with default values (e.g., most `has_secondary_use_*` default to 0)
- Keep the UI clean — don't expose all 38 features; show ~12 most important ones

### 3.10 `notebooks/01_eda.ipynb`

**Structure (cells)**:
1. Imports and data loading
2. Dataset shape and info
3. Missing value analysis
4. Target distribution (bar chart + percentages)
5. Numerical feature distributions (histograms subplot grid)
6. Categorical feature distributions (bar charts for top 4)
7. Feature vs damage_grade (box plots for age, floors, area, height)
8. Superstructure materials by damage grade (grouped bar)
9. Geographic analysis: mean damage by geo_level_1
10. Correlation heatmap (numerical features)
11. Key findings summary (markdown cell)

**Saving figures**:
```python
fig.savefig('results/figures/target_distribution.png', dpi=150, bbox_inches='tight')
```

---

## 4. Quality Gates

Each phase has a **quality gate** — a set of checks that must pass before proceeding.

### Gate 1: After Scaffolding
- [ ] `git init` successful
- [ ] All directories exist
- [ ] `.gitignore` works correctly
- [ ] `requirements.txt` is valid

### Gate 2: After Dataset
- [ ] CSV files exist in `data/raw/`
- [ ] Files are non-empty and loadable by pandas

### Gate 3: After Validation
- [ ] Row count = 260,601
- [ ] Column count = 39 (features) + 1 (target after merge)
- [ ] No duplicate building_ids
- [ ] Target values ∈ {1, 2, 3}
- [ ] building_id alignment confirmed

### Gate 4: After Preprocessing
- [ ] `build_preprocessor()` runs without error
- [ ] Output shape is correct (rows preserved, columns expanded for one-hot)
- [ ] No NaN in transformed output
- [ ] Train and val shapes are consistent

### Gate 5: After Training
- [ ] Each model's `.fit()` completes without error
- [ ] Models are saved to `models/`
- [ ] Preprocessor is saved to `models/`
- [ ] Training time is reasonable (< 30 min total)

### Gate 6: After Evaluation
- [ ] All 3 models produce metrics
- [ ] Micro-F1 > 0.57 for all models (beats baseline)
- [ ] Confusion matrices are generated
- [ ] Comparison table is saved
- [ ] Feature importance plot exists

### Gate 7: After Demo
- [ ] `streamlit run app/streamlit_app.py` launches without error
- [ ] Prediction returns valid damage_grade
- [ ] Probabilities sum to ~1.0
- [ ] UI is readable and presentable

---

## 5. Error Recovery Procedures

### 5.1 Dataset Not Found
```
Problem: CSV files not in data/raw/
Action:
1. Print clear error message with download URL
2. Provide step-by-step download instructions
3. Check for alternative locations
4. Do NOT fabricate data
```

### 5.2 KNN Too Slow
```
Problem: KNN training takes >15 minutes
Action:
1. Reduce CV folds from 3 to 2
2. Reduce k values to search: [11, 21] only
3. If still slow, subsample to 100K rows for tuning
4. Train final model on full data with best k
5. Document the time constraint in results
```

### 5.3 MLP Not Converging
```
Problem: MLP loss not decreasing
Action:
1. Check that data is scaled (StandardScaler applied)
2. Try lower learning rate: 0.0001
3. Try different architecture: (64, 32)
4. Increase max_iter to 500
5. If still failing, use solver='lbfgs' for small data
6. Report honest results even if poor
```

### 5.4 Import Error
```
Problem: Module not found
Action:
1. pip install the missing package
2. Add to requirements.txt
3. Verify installation
```

### 5.5 Memory Error
```
Problem: OOM on large dataset operations
Action:
1. For KNN: use algorithm='ball_tree' instead of 'brute'
2. For one-hot: ensure geo IDs are NOT one-hot encoded
3. For RF: reduce n_estimators to 100
4. Last resort: subsample dataset to 150K rows
```

---

## 6. Exact CLI Commands

### Setup
```bash
cd /home/pigasso/Projects/ml_project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Data Placement
```bash
# User manually downloads from DrivenData and places files:
# data/raw/train_values.csv
# data/raw/train_labels.csv
# data/raw/test_values.csv (optional)
# data/raw/submission_format.csv (optional)
```

### Training
```bash
python -m src.train
# Expected output:
#   Loading dataset...
#   Dataset validated: 260601 rows, 39 feature columns
#   Preprocessing...
#   Training KNN... (3-5 min)
#   Training MLP... (2-5 min)
#   Training RF...  (1-3 min)
#   Models saved to models/
```

### Evaluation
```bash
python -m src.evaluate
# Expected output:
#   Loading models...
#   Evaluating KNN... Micro-F1: 0.XXXX
#   Evaluating MLP... Micro-F1: 0.XXXX
#   Evaluating RF...  Micro-F1: 0.XXXX
#   Best model: Random Forest (Micro-F1: 0.XXXX)
#   Results saved to results/
```

### Demo
```bash
streamlit run app/streamlit_app.py
# Opens browser at http://localhost:8501
```

---

## 7. Code Style Guidelines

### Naming
```python
# Variables: snake_case
train_values = pd.read_csv(...)
micro_f1_score = 0.72

# Functions: snake_case, verb-first
def load_raw_data():
def build_preprocessor():
def train_knn():
def evaluate_model():

# Constants: UPPER_SNAKE_CASE
RANDOM_STATE = 42
NUMERICAL_COLS = [...]
```

### Comments
```python
# Good: explains WHY
# Use ball_tree algorithm because brute force is O(n²) on 260K rows
knn = KNeighborsClassifier(algorithm='ball_tree')

# Bad: explains WHAT (obvious from code)
# Create a KNN classifier
knn = KNeighborsClassifier()
```

### Docstrings
```python
def evaluate_model(model, X_val, y_val, model_name):
    """
    Evaluate a trained model on validation data.
    
    Args:
        model: Trained sklearn model with .predict() method
        X_val: Transformed validation features (numpy array)
        y_val: Validation labels (pandas Series)
        model_name: String name for display (e.g., 'Random Forest')
    
    Returns:
        dict: Contains accuracy, micro_f1, macro_f1, confusion_matrix, etc.
    """
```

### Print Output Style
```python
print("=" * 60)
print("MODEL TRAINING")
print("=" * 60)
print(f"\n[1/3] Training KNN (k={best_k})...")
print(f"  ✓ KNN trained in {elapsed:.1f}s")
print(f"\n[2/3] Training MLP (128, 64)...")
print(f"  ✓ MLP trained in {elapsed:.1f}s ({model.n_iter_} epochs)")
print(f"\n[3/3] Training Random Forest (200 trees)...")
print(f"  ✓ RF trained in {elapsed:.1f}s")
print(f"\nAll models saved to models/")
```

---

## 8. Viva / Q&A Preparation

### Likely Questions & Prepared Answers

**Q: Why did you choose these three models?**
> KNN is a simple instance-based method that serves as our non-parametric baseline. MLP (neural network) captures non-linear patterns through learned representations. Random Forest is an ensemble of decision trees that handles mixed feature types well and provides feature importance. Together they represent three fundamentally different learning paradigms.

**Q: How did you handle categorical features?**
> We used one-hot encoding for low-cardinality categorical features (8 features with 3-10 categories each). Geographic IDs were kept as integers because one-hot encoding geo_level_3_id would create 12,567 sparse columns. Binary features were passed through unchanged.

**Q: Why micro-averaged F1 and not accuracy?**
> Micro-F1 weights each sample equally across all classes, which is appropriate for imbalanced datasets. In our case, class 2 is the majority (~57%), so raw accuracy would be inflated by simply predicting class 2 often. Micro-F1 is also the official competition metric.

**Q: How did you prevent data leakage?**
> The preprocessing pipeline (StandardScaler, OneHotEncoder) is fitted only on the training set. The validation set is transformed using the already-fitted pipeline. We used a stratified split to preserve class ratios.

**Q: Why does your Random Forest outperform KNN and MLP?**
> Random Forest naturally handles mixed feature types, is invariant to feature scaling, captures non-linear interactions through tree splits, and is robust to noise through ensemble averaging. KNN struggles with high-dimensional data (curse of dimensionality with ~60 features). MLP requires more careful tuning and may need more epochs or a different architecture.

**Q: What are the most important features?**
> [Refer to the feature importance plot] Geographic location (geo_level IDs), superstructure type, building age, and number of floors are typically the strongest predictors. This makes physical sense — location determines earthquake intensity, materials determine structural resilience.

**Q: What are the limitations of your approach?**
> 1) We used sklearn's MLP which is limited compared to PyTorch/TensorFlow for deep architectures. 2) Geographic features are treated as ordinal integers which loses the categorical nature. 3) We didn't try advanced methods like gradient boosting (XGBoost/LightGBM) which typically top this competition's leaderboard. 4) Hyperparameter tuning was lightweight due to time constraints.

---

## 9. Post-Completion Checklist

Before declaring the project complete, verify every item:

```
CRITICAL:
□ Dataset loads from data/raw/ without error
□ Preprocessing pipeline fits and transforms correctly
□ KNN trains and predicts
□ MLP trains and predicts  
□ Random Forest trains and predicts
□ Micro-F1 computed for all 3 models
□ Best model identified and saved
□ Streamlit app launches and returns predictions
□ All reported metrics come from actual execution

FILES EXIST:
□ .gitignore
□ requirements.txt
□ README.md
□ src/__init__.py
□ src/data_loader.py
□ src/preprocessing.py
□ src/train.py
□ src/evaluate.py
□ src/predict.py
□ app/streamlit_app.py
□ notebooks/01_eda.ipynb (or .py)
□ docs/report.md
□ docs/presentation.md

RESULTS EXIST:
□ results/figures/target_distribution.png
□ results/figures/confusion_matrix_best.png
□ results/figures/model_comparison.png
□ results/figures/feature_importance.png
□ results/metrics/comparison.csv
□ models/best_model.pkl (or .joblib)
□ models/preprocessor.pkl (or .joblib)
□ models/model_metadata.json

CODE QUALITY:
□ No hardcoded absolute paths
□ No missing imports
□ No broken relative paths
□ All functions have docstrings
□ Random seeds set for reproducibility
□ No data leakage in preprocessing
□ No fabricated results
□ Code is readable by a university student
```

---

## 10. Final Report Template

When the project is complete, produce a summary in this format:

```
FINAL PROJECT REPORT
====================

1. IMPLEMENTED:
   - [list all components built]

2. DATASET:
   - Source: DrivenData Competition #57
   - Training samples: 260,601
   - Features: 38
   - Target: damage_grade (1/2/3)

3. MODELS:
   - KNN (k=XX): Micro-F1 = 0.XXXX
   - MLP (128,64): Micro-F1 = 0.XXXX
   - Random Forest (200 trees): Micro-F1 = 0.XXXX

4. BEST MODEL:
   - [Model Name] with Micro-F1 = 0.XXXX

5. FILES CREATED:
   - [full list]

6. COMMANDS:
   pip install -r requirements.txt
   python -m src.train
   python -m src.evaluate
   streamlit run app/streamlit_app.py

7. MANUAL STEPS REQUIRED:
   - [e.g., download dataset from DrivenData]

8. TALKING POINTS:
   - [Key points for demo presentation]
```
