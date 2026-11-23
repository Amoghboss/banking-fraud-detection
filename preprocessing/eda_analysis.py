"""
Exploratory Data Analysis (EDA) Script for Banking Fraud Detection
Analyzes creditcard.csv, computes statistical profiles, correlations, and generates visual charts.
"""
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Headless backend for web/server environments
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from config import Config

def perform_eda():
    csv_path = Config.DATASET_PATH
    output_img_dir = PROJECT_ROOT / 'static' / 'images'
    output_img_dir.mkdir(parents=True, exist_ok=True)
    summary_path = PROJECT_ROOT / 'dataset' / 'eda_summary.json'
    
    print(f"[*] Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    total_records = len(df)
    total_features = df.shape[1]
    
    print(f"[+] Loaded {total_records:,} transactions across {total_features} features.")
    
    # 1. Missing Values & Duplicates
    missing_vals = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())
    print(f"[+] Missing values: {missing_vals}")
    print(f"[+] Duplicate rows: {duplicates:,}")
    
    # 2. Class Distribution
    class_counts = df['Class'].value_counts()
    legit_count = int(class_counts.get(0, 0))
    fraud_count = int(class_counts.get(1, 0))
    fraud_pct = (fraud_count / total_records) * 100
    legit_pct = (legit_count / total_records) * 100
    print(f"[+] Legitimate (0): {legit_count:,} ({legit_pct:.4f}%)")
    print(f"[+] Fraudulent (1): {fraud_count:,} ({fraud_pct:.4f}%)")
    
    # 3. Amount Statistics
    legit_amt = df[df['Class'] == 0]['Amount']
    fraud_amt = df[df['Class'] == 1]['Amount']
    
    amount_stats = {
        'legit': {
            'mean': float(legit_amt.mean()),
            'std': float(legit_amt.std()),
            'median': float(legit_amt.median()),
            'max': float(legit_amt.max()),
            'min': float(legit_amt.min())
        },
        'fraud': {
            'mean': float(fraud_amt.mean()),
            'std': float(fraud_amt.std()),
            'median': float(fraud_amt.median()),
            'max': float(fraud_amt.max()),
            'min': float(fraud_amt.min())
        }
    }
    
    # 4. Correlation Analysis
    correlations = df.corr()['Class'].drop('Class')
    top_pos_corr = correlations.sort_values(ascending=False).head(5).to_dict()
    top_neg_corr = correlations.sort_values().head(5).to_dict()
    
    # Serialize EDA Summary
    eda_summary = {
        'total_transactions': total_records,
        'total_features': total_features,
        'missing_values': missing_vals,
        'duplicate_rows': duplicates,
        'legitimate_transactions': legit_count,
        'fraudulent_transactions': fraud_count,
        'fraud_percentage': round(fraud_pct, 4),
        'legitimate_percentage': round(legit_pct, 4),
        'amount_stats': amount_stats,
        'top_positive_correlations': {k: round(v, 4) for k, v in top_pos_corr.items()},
        'top_negative_correlations': {k: round(v, 4) for k, v in top_neg_corr.items()}
    }
    
    with open(summary_path, 'w') as f:
        json.dump(eda_summary, f, indent=4)
    print(f"[+] Saved EDA Summary to: {summary_path}")
    
    # Visual Styles
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    navy_palette = ['#1e293b', '#ef4444']
    
    # CHART 1: Class Distribution (Imbalance)
    print("[*] Generating Class Distribution Chart...")
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    
    # Bar Chart (Log Scale for visibility of rare class)
    bars = ax[0].bar(['Legitimate (0)', 'Fraudulent (1)'], [legit_count, fraud_count], color=['#10b981', '#ef4444'])
    ax[0].set_yscale('log')
    ax[0].set_title('Transaction Class Counts (Log Scale)', fontsize=13, fontweight='bold', pad=12)
    ax[0].set_ylabel('Number of Transactions (Log)')
    for bar in bars:
        h = bar.get_height()
        ax[0].text(bar.get_x() + bar.get_width()/2., h * 1.15, f'{int(h):,}', ha='center', va='bottom', fontweight='bold')
        
    # Donut Chart
    wedges, texts, autotexts = ax[1].pie(
        [legit_count, fraud_count],
        labels=['Legitimate (99.83%)', 'Fraudulent (0.17%)'],
        autopct='%1.2f%%',
        startangle=45,
        colors=['#3b82f6', '#ef4444'],
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
    )
    ax[1].set_title('Severe Class Imbalance Proportion', fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()
    fig.savefig(output_img_dir / 'class_distribution.png', dpi=200)
    plt.close()
    
    # CHART 2: Amount Distribution Comparison
    print("[*] Generating Amount Distribution Chart...")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df[df['Class'] == 0]['Amount'], bins=50, color='#3b82f6', label='Legitimate', kde=True, ax=ax, stat='density')
    sns.histplot(df[df['Class'] == 1]['Amount'], bins=50, color='#ef4444', label='Fraudulent', kde=True, ax=ax, stat='density')
    ax.set_xlim([0, 2500])
    ax.set_title('Transaction Amount Distribution by Class (Capped at $2,500)', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Amount ($)')
    ax.set_ylabel('Density')
    ax.legend()
    plt.tight_layout()
    fig.savefig(output_img_dir / 'amount_distribution.png', dpi=200)
    plt.close()
    
    # CHART 3: Feature Correlation Heatmap with Class
    print("[*] Generating Correlation Heatmap...")
    plt.figure(figsize=(12, 6))
    top_corr_features = list(top_pos_corr.keys()) + list(top_neg_corr.keys()) + ['Class']
    corr_matrix = df[top_corr_features].corr()
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1, cbar=True, square=False)
    plt.title('Correlation Heatmap of Key Features with Fraud Class', fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(output_img_dir / 'correlation_matrix.png', dpi=200)
    plt.close()
    
    print("[+] All EDA charts and summaries successfully generated!")

if __name__ == '__main__':
    perform_eda()
