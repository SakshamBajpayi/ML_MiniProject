import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_loader import load_raw_data

def run_eda():
    print("Starting Exploratory Data Analysis...")
    os.makedirs('results/figures', exist_ok=True)
    
    try:
        df = load_raw_data()
    except FileNotFoundError as e:
        print(f"Cannot run EDA. {e}")
        return

    # 1. Target Distribution
    print("Generating Target Distribution...")
    plt.figure(figsize=(8, 6))
    ax = sns.countplot(data=df, x='damage_grade', palette='viridis')
    plt.title('Distribution of Damage Grade')
    plt.xlabel('Damage Grade')
    plt.ylabel('Count')
    
    # Add percentages
    total = len(df)
    for p in ax.patches:
        percentage = f'{100 * p.get_height() / total:.1f}%'
        x = p.get_x() + p.get_width() / 2 - 0.1
        y = p.get_height() + total * 0.01
        ax.annotate(percentage, (x, y))
        
    plt.tight_layout()
    plt.savefig('results/figures/target_distribution.png', dpi=150)
    plt.close()

    # 2. Numerical Feature Distributions
    print("Generating Numerical Distributions...")
    numeric_cols = ['age', 'area_percentage', 'height_percentage', 'count_floors_pre_eq']
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for i, col in enumerate(numeric_cols):
        ax = axes[i//2, i%2]
        # Cap age for visualization since it has a 995 outlier
        plot_data = df[df[col] < df[col].quantile(0.99)]
        sns.histplot(data=plot_data, x=col, bins=30, ax=ax, kde=True, color='skyblue')
        ax.set_title(f'Distribution of {col} (99th percentile)')
    plt.tight_layout()
    plt.savefig('results/figures/numerical_distributions.png', dpi=150)
    plt.close()

    # 3. Superstructure vs Damage Grade
    print("Generating Superstructure Analysis...")
    superstructure_cols = [c for c in df.columns if c.startswith('has_superstructure_')]
    
    # Calculate mean damage for each superstructure type
    mat_damage = []
    for col in superstructure_cols:
        name = col.replace('has_superstructure_', '')
        # Only look at rows where the material is used
        subset = df[df[col] == 1]
        if len(subset) > 0:
            mean_damage = subset['damage_grade'].mean()
            mat_damage.append({'Material': name, 'Mean Damage': mean_damage, 'Count': len(subset)})
            
    mat_df = pd.DataFrame(mat_damage).sort_values('Mean Damage')
    
    # Plot
    plt.figure(figsize=(12, 8))
    sns.barplot(data=mat_df, x='Mean Damage', y='Material', palette='coolwarm')
    plt.title('Mean Damage Grade by Superstructure Material')
    plt.axvline(x=df['damage_grade'].mean(), color='r', linestyle='--', label='Overall Mean Damage')
    plt.legend()
    plt.tight_layout()
    plt.savefig('results/figures/superstructure_vs_damage.png', dpi=150)
    plt.close()

    # 4. Correlation Heatmap
    print("Generating Correlation Heatmap...")
    plt.figure(figsize=(10, 8))
    corr = df[numeric_cols + ['damage_grade']].corr()
    sns.heatmap(corr, annot=True, cmap='RdBu', vmin=-1, vmax=1, fmt='.2f')
    plt.title('Correlation Heatmap (Numerical Features & Target)')
    plt.tight_layout()
    plt.savefig('results/figures/correlation_heatmap.png', dpi=150)
    plt.close()
    
    print("EDA Complete. Figures saved to results/figures/")

if __name__ == '__main__':
    run_eda()
