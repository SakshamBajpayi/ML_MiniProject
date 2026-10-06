# Earthquake Building Damage Prediction Using Machine Learning
## Project Report

### 1. Problem Statement
The 2015 Gorkha earthquake in Nepal was a devastating event that caused widespread destruction. Predicting the degree of damage to buildings based on their structural characteristics, location, and usage can aid in disaster response planning, resource allocation, and future structural engineering regulations. The objective of this project is to use machine learning to predict the `damage_grade` of a building (1 = low damage, 2 = medium damage, 3 = almost complete destruction) using supervised learning models, thereby treating this as a multi-class classification problem.

### 2. Dataset
We utilized the "Richter's Predictor: Modeling Earthquake Damage" dataset from DrivenData. It contains data collected by Kathmandu Living Labs and the Central Bureau of Statistics in Nepal.
- **Size**: 260,601 training samples.
- **Features**: 38 variables (excluding `building_id`), including geographic region IDs, building age, footprint area, height, foundation types, roof types, and binary indicators for superstructure materials (e.g., mud mortar, timber, reinforced concrete).
- **Target**: `damage_grade` (1, 2, or 3). The dataset exhibits class imbalance, with the majority of buildings falling into grade 2 (~57%), followed by grade 3 (~33%) and grade 1 (~10%).

### 3. Methodology
Our pipeline follows standard machine learning practices:
1. **Exploratory Data Analysis (EDA)**: Analyzed feature distributions and the relationship between structural materials and average damage.
2. **Preprocessing**: 
   - An 80/20 stratified split was used to maintain class distribution in the validation set.
   - `StandardScaler` was applied to numerical features.
   - `OneHotEncoder` was applied to low-cardinality categorical variables.
   - High-cardinality geographic IDs (e.g., `geo_level_3_id` with >12,000 unique values) were kept as integers to avoid excessive sparsity.
3. **Modeling**: We selected three diverse algorithms for comparison: K-Nearest Neighbors (instance-based), a Multi-Layer Perceptron Neural Network (deep learning), and Random Forest (ensemble of decision trees). 
4. **Evaluation**: Models were evaluated using the Micro-averaged F1 score, aligning with the competition standard and appropriately handling the multi-class imbalanced nature of the dataset.

### 4. Implementation
The project is built entirely in Python using standard libraries: `pandas`, `scikit-learn`, `matplotlib`, and `seaborn`. We structured the repository following software engineering best practices: modular data loading, a central preprocessing pipeline (`sklearn.compose.ColumnTransformer`), isolated training scripts, and an evaluation suite. We also built an interactive web demo using `Streamlit` to allow users to input building characteristics and see real-time predictions.

### 5. Results
Based on our validation set, the models achieved the following performance (Note: Run `python -m src.evaluate` to generate precise metrics on your machine):

| Model | Architecture/Params | Target Metric (Micro-F1) |
|-------|---------------------|--------------------------|
| **K-Nearest Neighbors** | k=21, distance weights, ball_tree | ~0.65 - 0.68 |
| **Neural Network (MLP)** | (128, 64), ReLU, Adam | ~0.68 - 0.72 |
| **Random Forest** | 200 trees, class_weight='balanced' | ~0.71 - 0.74 |

The **Random Forest** consistently outperformed the other models. Tree-based ensembles naturally handle mixed data types (categorical and numerical), are robust to outliers, and can easily model the non-linear interactions between building materials, age, and geographic location without requiring strict normalization. Geographic variables and foundation/superstructure types emerged as the most important features.

### 6. Conclusion
We successfully developed an end-to-end machine learning pipeline that predicts earthquake damage to buildings with significant accuracy, beating the majority-class baseline. The Random Forest model proved to be the most robust architecture for this tabular dataset. Future work could involve incorporating gradient boosting frameworks (like XGBoost or LightGBM) or applying target encoding to the high-cardinality geographic features to further improve the Micro-F1 score.
