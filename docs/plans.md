# Earthquake Building Damage Prediction — Project Plan

## 1. Project Overview

| Field | Detail |
|---|---|
| **Title** | Earthquake Building Damage Prediction Using Machine Learning |
| **Problem** | Predict `damage_grade` (1/2/3) of buildings from the 2015 Gorkha earthquake |
| **Dataset** | DrivenData — "Richter's Predictor: Modeling Earthquake Damage" |
| **Models** | K-Nearest Neighbors, MLP Neural Network, Random Forest |
| **Primary Metric** | Micro-averaged F1 Score |
| **Deliverables** | Code, README, 2-page report material, presentation material, live demo app |
| **Timeline** | 1 week |

---

## 2. Repository State (as inspected)

The repository at `/home/pigasso/Projects/ml_project` is **completely empty** — no files, no git history, no existing code. This is a greenfield build.

---

## 3. Dataset Specification

### 3.1 Source
- **Primary**: [DrivenData Competition #57](https://www.drivendata.org/competitions/57/nepal-earthquake/)
- **Alternative**: Available on Kaggle as mirror
- **Requires**: Free account registration + accepting competition rules to download
- **Data collected by**: Kathmandu Living Labs & Central Bureau of Statistics, Nepal

### 3.2 Files Expected

| File | Rows | Columns | Purpose |
|---|---|---|---|
| `train_values.csv` | 260,601 | 39 (building_id + 38 features) | Training features |
| `train_labels.csv` | 260,601 | 2 (building_id + damage_grade) | Training labels |
| `test_values.csv` | ~86,868 | 39 | Competition test set (no labels) |
| `submission_format.csv` | ~86,868 | 2 | Submission template |

> [!IMPORTANT]
> We will **only use** `train_values.csv` and `train_labels.csv` for this project since `test_values.csv` has no labels and is for competition submission. We create our own train/validation split from the training data.

### 3.3 Feature Schema (38 features + 1 ID)

**Numerical / Integer Features (10):**
| Feature | Description |
|---|---|
| `geo_level_1_id` | Geographic region level 1 (0–30) |
| `geo_level_2_id` | Geographic region level 2 (0–1427) |
| `geo_level_3_id` | Geographic region level 3 (0–12567) |
| `count_floors_pre_eq` | Number of floors before earthquake |
| `age` | Building age in years |
| `area_percentage` | Normalized building footprint area |
| `height_percentage` | Normalized building height |
| `count_families` | Number of families living in building |

> [!NOTE]
> `geo_level_*_id` columns are integer-coded geographic identifiers. They are **not truly numerical** — they represent categorical regions. Treatment decision: keep as integers for tree models; consider target-encoding or dropping for KNN/MLP.

**Categorical Features (7):**
| Feature | Possible Values |
|---|---|
| `land_surface_condition` | n, o, t |
| `foundation_type` | h, i, r, u, w |
| `roof_type` | n, q, x |
| `ground_floor_type` | f, m, v, x, z |
| `other_floor_type` | j, q, s, x |
| `position` | j, o, s, t |
| `plan_configuration` | a, c, d, f, m, n, o, q, s, u |
| `legal_ownership_status` | a, r, v, w |

**Binary Features (21):**
- 11 × `has_superstructure_*` (adobe_mud, mud_mortar_stone, stone_flag, cement_mortar_stone, mud_mortar_brick, cement_mortar_brick, timber, bamboo, rc_non_engineered, rc_engineered, other)
- 10 × `has_secondary_use_*` (parent flag + agriculture, hotel, rental, institution, school, industry, health_post, gov_office, use_police, other)

### 3.4 Target Variable

| Column | Values | Meaning |
|---|---|---|
| `damage_grade` | 1 | Low damage |
| | 2 | Medium damage |
| | 3 | Almost complete destruction |

**Expected class distribution**: Imbalanced — class 2 is the majority class (~57%), class 3 (~33%), class 1 (~10%). This is important for model evaluation.

---

## 4. Target Directory Structure

```
ml_project/
├── data/                      # Dataset files (gitignored)
│   ├── raw/                   # Original downloaded CSVs
│   │   ├── train_values.csv
│   │   ├── train_labels.csv
│   │   ├── test_values.csv
│   │   └── submission_format.csv
│   └── processed/             # Any processed/cached data
├── notebooks/
│   └── 01_eda.ipynb           # Exploratory Data Analysis notebook
├── src/
│   ├── __init__.py
│   ├── data_loader.py         # Data loading and validation
│   ├── preprocessing.py       # Feature engineering & pipeline
│   ├── train.py               # Model training script
│   ├── evaluate.py            # Model evaluation script
│   └── predict.py             # Single-sample prediction utility
├── models/                    # Saved model artifacts (gitignored except small ones)
│   └── .gitkeep
├── results/                   # Metrics, plots, comparison tables
│   ├── figures/               # EDA and result plots
│   └── metrics/               # JSON/CSV metric files
├── app/
│   └── streamlit_app.py       # Live demo Streamlit application
├── docs/
│   ├── report.md              # 2-page write-up content
│   └── presentation.md        # Slide content / outline
├── requirements.txt
├── README.md
├── .gitignore
└── setup.sh                   # Optional setup helper
```

---

## 5. Phase-by-Phase Execution Plan

### PHASE 1 — Repository Setup & Scaffolding
**Duration**: ~15 min  
**Tasks**:
1. Initialize git repository
2. Create directory structure shown above
3. Create `.gitignore` (data/raw/*, models/*.pkl, __pycache__, .venv, etc.)
4. Create `requirements.txt` with pinned dependencies
5. Create minimal `README.md` placeholder

**Dependencies**: None  
**Output**: Clean, version-controlled skeleton project

---

### PHASE 2 — Dataset Acquisition
**Duration**: ~10 min  
**Tasks**:
1. Document exact download steps for DrivenData
2. Create `setup.sh` or `download_data.py` helper script
3. Provide Kaggle alternative instructions
4. Place files in `data/raw/`
5. If cannot auto-download, provide clear manual instructions in README

**Critical Decision**:
- DrivenData requires free account registration → document this
- Provide a download script using `drivendata` CLI or direct URL if available
- Fallback: user manually downloads and places files

**Output**: Data files in `data/raw/` or clear instructions for manual placement

---

### PHASE 3 — Dataset Validation
**Duration**: ~20 min  
**Tasks**:
1. Load `train_values.csv` and `train_labels.csv`
2. Verify row counts (expect 260,601)
3. Verify column names match the 39-column schema
4. Confirm `building_id` alignment between values and labels
5. Check for duplicates in `building_id`
6. Check for missing values (expect none based on competition description, but verify)
7. Verify target distribution
8. Check data types

**Validation Checks** (implement in `src/data_loader.py`):
```python
assert len(train_values) == len(train_labels)
assert set(train_values['building_id']) == set(train_labels['building_id'])
assert train_labels['damage_grade'].isin([1, 2, 3]).all()
assert train_values['building_id'].nunique() == len(train_values)
```

**Output**: `data_loader.py` with validation, printed summary

---

### PHASE 4 — Exploratory Data Analysis
**Duration**: ~45 min  
**Tasks**:
1. Create `notebooks/01_eda.ipynb`
2. Generate the following visualizations:
   - **Target distribution**: bar chart of damage_grade counts + percentages
   - **Numerical feature distributions**: histograms for age, count_floors_pre_eq, area_percentage, height_percentage, count_families
   - **Categorical feature distributions**: bar charts for top categorical features
   - **Feature vs. damage_grade**: box plots or violin plots showing relationship between key features and target
   - **Correlation heatmap**: for numerical features
   - **Superstructure material usage**: stacked bar chart showing material prevalence by damage grade
   - **Geographic analysis**: damage distribution by geo_level_1_id
3. Save key figures to `results/figures/`
4. Document key findings

**Key EDA Questions to Answer**:
- Is the dataset balanced? (No — class 2 dominates)
- Which features have strongest visual relationship with damage?
- Are there any suspicious outliers?
- Are geo features informative?
- Which superstructure materials correlate with higher damage?

**Output**: EDA notebook + 6–8 saved figures

---

### PHASE 5 — Preprocessing Pipeline
**Duration**: ~30 min  
**Tasks**:
1. Create `src/preprocessing.py`
2. Design sklearn `ColumnTransformer` pipeline:

| Feature Group | Columns | Treatment |
|---|---|---|
| Numerical | age, count_floors_pre_eq, area_percentage, height_percentage, count_families | StandardScaler (for KNN/MLP) / passthrough (for RF) |
| Geo IDs | geo_level_1_id, geo_level_2_id, geo_level_3_id | Keep as-is for RF; for KNN/MLP consider ordinal or target encoding |
| Categorical | land_surface_condition, foundation_type, roof_type, ground_floor_type, other_floor_type, position, plan_configuration, legal_ownership_status | OneHotEncoder (sparse_output=False, handle_unknown='ignore') |
| Binary | 21 has_* columns | Passthrough (already 0/1) |

3. Create train/validation split: **80/20 stratified**
4. Ensure pipeline is fitted only on training data (no leakage)
5. Save column names and feature types as constants

**Design Decisions**:
- Two pipelines: one with scaling (for KNN/MLP), one without (for RF)
- Or: one pipeline with scaling, and RF ignores it (RF is scale-invariant)
- **Decision**: Use single pipeline with scaling. Simpler. RF still works fine.
- Use `OrdinalEncoder` for geo_level IDs since they have too many unique values for one-hot
- Random seed: **42** throughout

**Output**: `preprocessing.py` with `build_pipeline()`, `get_feature_columns()`, `prepare_data()`

---

### PHASE 6 — Model Implementation
**Duration**: ~1 hour  
**Tasks**:

#### 6.1 K-Nearest Neighbors
```python
from sklearn.neighbors import KNeighborsClassifier
```
- Initial k: 15–25 (dataset is large, small k is noisy)
- Distance metric: 'minkowski' (default Euclidean with p=2)
- Weights: 'distance' (weight by inverse distance)
- **Hyperparameter search**: Try k ∈ {5, 11, 15, 21, 25, 31} with cross-validation
- **Note**: KNN on 260K samples × ~60 features is computationally expensive. May need to subsample or use `algorithm='ball_tree'`
- **Mitigation**: Train on full data but time it. If >10 min, subsample to 50K for tuning, then train final on full.

#### 6.2 Neural Network (MLP)
```python
from sklearn.neural_network import MLPClassifier
```
- Architecture: (128, 64) — two hidden layers
- Activation: 'relu'
- Solver: 'adam'
- Learning rate: 'adaptive' starting at 0.001
- Max iterations: 200
- Early stopping: True (10% validation split internal)
- **Hyperparameter search**: Light — try 2–3 architectures
  - (64, 32)
  - (128, 64)
  - (128, 64, 32)
- Batch size: 256

#### 6.3 Random Forest
```python
from sklearn.ensemble import RandomForestClassifier
```
- n_estimators: 200
- max_depth: None (let trees grow fully) or try 20, 30
- min_samples_split: 5
- min_samples_leaf: 2
- max_features: 'sqrt'
- class_weight: 'balanced' (to handle imbalance)
- n_jobs: -1 (use all cores)
- **Hyperparameter search**: Try n_estimators ∈ {100, 200, 300}, max_depth ∈ {20, 30, None}

#### 6.4 Training Script Design
```python
# src/train.py
def train_knn(X_train, y_train, params):
    ...
def train_mlp(X_train, y_train, params):
    ...
def train_rf(X_train, y_train, params):
    ...
def main():
    # Load data, preprocess, train all 3, save models
```

**Output**: `src/train.py` with three model training functions

---

### PHASE 7 — Evaluation & Comparison
**Duration**: ~30 min  
**Tasks**:
1. Create `src/evaluate.py`
2. For each model compute:
   - Micro-F1 (primary)
   - Macro-F1
   - Accuracy
   - Per-class precision, recall, F1
   - Confusion matrix
   - Classification report
3. Generate comparison table:

```
| Model          | Accuracy | Micro-F1 | Macro-F1 | Train Time |
|----------------|----------|----------|----------|------------|
| KNN (k=21)     | 0.XXXX   | 0.XXXX   | 0.XXXX   | XX.Xs      |
| MLP (128,64)   | 0.XXXX   | 0.XXXX   | 0.XXXX   | XX.Xs      |
| Random Forest   | 0.XXXX   | 0.XXXX   | 0.XXXX   | XX.Xs      |
```

4. Generate visualizations:
   - Confusion matrix heatmap for each model (especially best)
   - Model comparison bar chart
   - Feature importance plot for Random Forest (top 20 features)
   - MLP training loss curve (if available from partial_fit or stored)
5. Save all plots to `results/figures/`
6. Save metrics to `results/metrics/comparison.csv` and `results/metrics/detailed.json`

**Expected Performance Range** (based on competition benchmarks):
- Baseline (predict majority class): ~57% accuracy, ~0.57 micro-F1
- Random Forest: ~0.71–0.74 micro-F1 (typical for this dataset)
- KNN: ~0.60–0.68 micro-F1 (depends on k and features)
- MLP: ~0.68–0.72 micro-F1

**Output**: `evaluate.py`, comparison table, 4–5 saved plots, metrics files

---

### PHASE 8 — Best Model Selection & Saving
**Duration**: ~10 min  
**Tasks**:
1. Select model with highest Micro-F1 on validation set
2. Save using joblib:
   - `models/best_model.pkl` — the trained model
   - `models/preprocessor.pkl` — the fitted preprocessing pipeline
   - `models/model_metadata.json` — model name, hyperparameters, metrics
3. Create `src/predict.py`:
   - Load saved model and preprocessor
   - Accept raw feature dict as input
   - Return predicted damage grade + probability

**Output**: Saved model artifacts, prediction utility

---

### PHASE 9 — Demo Application (Streamlit)
**Duration**: ~30 min  
**Tasks**:
1. Create `app/streamlit_app.py`
2. UI Components:
   - **Title & description**: Project name + brief explanation
   - **Sidebar inputs**: Sliders/dropdowns for key building features:
     - `count_floors_pre_eq` (slider 1–10)
     - `age` (slider 0–200)
     - `area_percentage` (slider 1–100)
     - `height_percentage` (slider 1–30)
     - `land_surface_condition` (dropdown: n, o, t)
     - `foundation_type` (dropdown: h, i, r, u, w)
     - `roof_type` (dropdown: n, q, x)
     - `ground_floor_type` (dropdown: f, m, v, x, z)
     - `position` (dropdown: j, o, s, t)
     - Selected `has_superstructure_*` checkboxes
   - **Predict button**: Triggers prediction
   - **Results display**:
     - Predicted Damage Grade (large, colored)
     - Interpretation text (Low / Medium / Almost Complete Destruction)
     - Prediction probabilities bar chart
     - Confidence percentage
   - **Model info section**: Which model is being used, its accuracy

3. Load model from `models/` on startup (cached with `@st.cache_resource`)
4. Default values for non-displayed features
5. Test that it launches and responds correctly

**Output**: Working Streamlit app, launchable with `streamlit run app/streamlit_app.py`

---

### PHASE 10 — Documentation & Presentation Materials
**Duration**: ~45 min  

#### 10.1 README.md
Complete README with:
- Project title and banner
- Problem statement (2–3 sentences)
- Dataset source and structure
- Methodology overview
- Project architecture tree
- Setup instructions (venv, pip, data download)
- Execution commands (train, evaluate, demo)
- Results table with actual metrics
- Limitations and future work
- Team contributions section
- Citations

#### 10.2 Report Material (`docs/report.md`)
Two-page PDF content:
1. **Problem Statement** (~150 words): Earthquake damage prediction, why it matters
2. **Dataset** (~200 words): Source, size, features, target
3. **Methodology** (~250 words): Preprocessing, models, evaluation strategy
4. **Implementation** (~200 words): Tools, architecture, key decisions
5. **Results** (~300 words): Metrics table, best model, confusion matrix, feature importance
6. **Conclusion** (~100 words): Findings, limitations, future work

#### 10.3 Presentation Material (`docs/presentation.md`)
Slide outline:
1. Title Slide
2. Problem & Motivation (with earthquake image context)
3. Dataset Overview (key stats, features breakdown)
4. Methodology (pipeline diagram)
5. Model 1: KNN (how it works, params, results)
6. Model 2: MLP (architecture, training, results)
7. Model 3: Random Forest (how it works, params, results)
8. Results Comparison (table + chart)
9. Live Demo
10. Conclusion & Future Work

**Output**: README.md, docs/report.md, docs/presentation.md

---

### PHASE 11 — Verification & Reproducibility
**Duration**: ~20 min  
**Tasks**:
1. Run entire pipeline from scratch:
   ```bash
   python -m src.train
   python -m src.evaluate
   streamlit run app/streamlit_app.py
   ```
2. Verify checklist:
   - [ ] Dataset loads without errors
   - [ ] Preprocessing pipeline works
   - [ ] All 3 models train successfully
   - [ ] Evaluation metrics are computed
   - [ ] Plots are generated and saved
   - [ ] Best model is saved to `models/`
   - [ ] Prediction works on single samples
   - [ ] Streamlit app launches
   - [ ] README commands are accurate
   - [ ] No missing imports
   - [ ] No hardcoded absolute paths
   - [ ] No data leakage
   - [ ] `.gitignore` is correct
   - [ ] All results are from actual execution (not fabricated)
3. Fix any errors found
4. Final git commit

**Output**: Verified, reproducible project

---

## 6. Dependencies

```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
joblib>=1.3.0
streamlit>=1.28.0
```

---

## 7. Key Technical Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Train/Val split | 80/20 stratified | Standard, preserves class ratios |
| Scaling | StandardScaler | Required for KNN and MLP; harmless for RF |
| Categorical encoding | OneHotEncoder | Small cardinality cats; clean and interpretable |
| Geo ID encoding | Keep as integer (ordinal) | Too many unique values for one-hot (12K+ for level 3) |
| Missing values | Verify first, then SimpleImputer if needed | Dataset may have no NaN but be safe |
| Random seed | 42 | Reproducibility |
| KNN computation | Full dataset with ball_tree | Dataset is large but manageable |
| MLP framework | sklearn MLPClassifier | Simple, no PyTorch overhead for academic project |
| Model serialization | joblib | Standard for sklearn |
| Demo framework | Streamlit | Simple, fast, no frontend needed |

---

## 8. Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Dataset not downloadable (auth required) | High | Blocks project | Provide manual download instructions; script with fallback |
| KNN too slow on 260K rows | Medium | Slow training | Subsample for tuning; use ball_tree; limit neighbors searched |
| MLP underperforms without extensive tuning | Low | Weak results | Accept honest results; explain in report |
| Streamlit not installed | Low | No demo | Include in requirements.txt |
| geo_level_3_id has 12K+ unique values | Medium | Memory with one-hot | Keep as integer, don't one-hot encode |
| Class imbalance hurts minority class | Medium | Low class-1 recall | Use class_weight='balanced' for RF; report per-class metrics |

---

## 9. Timeline Estimate

| Phase | Estimated Duration | Dependencies |
|---|---|---|
| Phase 1: Repo Setup | 15 min | None |
| Phase 2: Dataset Acquisition | 10 min | Phase 1 |
| Phase 3: Dataset Validation | 20 min | Phase 2 |
| Phase 4: EDA | 45 min | Phase 3 |
| Phase 5: Preprocessing | 30 min | Phase 3 |
| Phase 6: Model Implementation | 60 min | Phase 5 |
| Phase 7: Evaluation | 30 min | Phase 6 |
| Phase 8: Best Model | 10 min | Phase 7 |
| Phase 9: Demo App | 30 min | Phase 8 |
| Phase 10: Documentation | 45 min | Phase 7, 8, 9 |
| Phase 11: Verification | 20 min | All |
| **Total** | **~5 hours** | |

---

## 10. Success Criteria

1. ✅ All 3 models train and produce evaluation metrics
2. ✅ Best model achieves Micro-F1 > 0.65 (beating majority-class baseline of 0.57)
3. ✅ Streamlit demo launches and returns predictions
4. ✅ All results are from actual code execution
5. ✅ README provides complete setup-to-demo instructions
6. ✅ Report material covers all 6 required sections
7. ✅ Code is clean, commented, and explainable in a viva
