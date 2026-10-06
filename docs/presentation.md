# Presentation Outline: Earthquake Building Damage Prediction

## Slide 1: Title
*   **Title**: Earthquake Building Damage Prediction
*   **Subtitle**: Machine Learning applied to the 2015 Gorkha Earthquake
*   **Presenters**: [Team Names]
*   **Visual**: Title slide with a relevant, respectful background image.

## Slide 2: Problem & Motivation
*   **The Event**: 2015 Gorkha earthquake in Nepal (Magnitude 7.8).
*   **The Problem**: Can we predict the level of damage a building will sustain based on its construction and location?
*   **Why it Matters**: 
    *   Informs disaster response planning.
    *   Guides future structural engineering regulations.
    *   Identifies at-risk populations.

## Slide 3: Dataset Overview
*   **Source**: DrivenData competition data (collected by Kathmandu Living Labs & CBS Nepal).
*   **Size**: 260,601 buildings (rows).
*   **Features**: 38 variables (Age, height, geographic location, foundation type, superstructure materials).
*   **Target**: `damage_grade`
    *   1: Low damage (~10%)
    *   2: Medium damage (~57%)
    *   3: Almost complete destruction (~33%)

## Slide 4: Methodology & Preprocessing
*   **Data Split**: 80/20 Stratified Split.
*   **Preprocessing Pipeline**:
    *   *Numerical*: Scaled using StandardScaler.
    *   *Categorical*: One-Hot Encoded (e.g., roof type, foundation type).
    *   *Geographic*: Kept as integers (ordinal representation).
    *   *Binary*: Passed through as 0/1 (e.g., `has_superstructure_timber`).

## Slide 5: Models Evaluated
We tested three diverse machine learning paradigms:
1.  **K-Nearest Neighbors (KNN)**: Non-parametric baseline, evaluates buildings similar to nearby historical examples.
2.  **Multi-Layer Perceptron (MLP)**: A neural network capable of learning complex, non-linear feature representations.
3.  **Random Forest**: An ensemble of decision trees, highly robust for mixed-type tabular data.

## Slide 6: Results & Comparison
*   **Primary Metric**: Micro-averaged F1 Score (balances precision/recall across all 3 classes).
*   **Performance summary**: 
    *   *Baseline (Predicting majority)*: 0.57
    *   *KNN*: ~0.67
    *   *MLP*: ~0.71
    *   *Random Forest*: ~0.73 (Best)
*   **Visual**: Display the Model Comparison Bar Chart (generated in `results/figures/`).

## Slide 7: Insights (Feature Importance)
*   What makes a building survive or collapse?
*   **Top Predictors** (from Random Forest):
    1.  Geographic Location (`geo_level_1`, `2`, `3`) - Proximity to epicenter/fault lines.
    2.  Age of building.
    3.  Superstructure material (e.g., mud mortar vs. reinforced concrete).
*   **Visual**: Display the Top 20 Feature Importances chart.

## Slide 8: Live Demonstration
*   Showcase the Streamlit Web Application.
*   *Action*: Enter a hypothetical building (e.g., 50-year-old mud-mortar building) vs (5-year-old reinforced concrete building).
*   *Action*: Show the real-time prediction and confidence probabilities.

## Slide 9: Conclusion & Future Work
*   **Conclusion**: Random Forest is highly effective for this tabular dataset, significantly beating the baseline.
*   **Limitations**: High cardinality of geographic IDs is tricky to encode; KNN struggles with high dimensions.
*   **Future Work**: 
    *   Explore Gradient Boosting (XGBoost/LightGBM).
    *   Implement Target Encoding for geographic regions.
    *   Handle class imbalance using SMOTE.

## Slide 10: Q&A
*   "Thank you for listening. We open the floor to any questions."
