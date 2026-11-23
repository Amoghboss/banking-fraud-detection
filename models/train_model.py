"""
Comprehensive Machine Learning Training & Evaluation Pipeline
Trains, evaluates, and benchmarks 5 machine learning and data mining algorithms:
1. Logistic Regression
2. Decision Tree
3. Random Forest
4. Support Vector Machine (Linear SVM with probability calibration)
5. Isolation Forest (Anomaly Detection)
"""
import sys
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    roc_curve, precision_recall_curve
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from config import Config
from preprocessing.data_preprocessing import DataPreprocessor

def train_and_evaluate_models():
    print("=" * 70)
    print("  BANKING FRAUD DETECTION - ML MODEL TRAINING & BENCHMARKING")
    print("=" * 70)
    
    # 1. Load and Preprocess Data
    preprocessor = DataPreprocessor()
    print("[*] Loading dataset...")
    df = preprocessor.load_dataset()
    print(f"[+] Loaded {len(df):,} transactions.")
    
    print("[*] Performing stratified train/test split (80/20) and robust scaling...")
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(df, test_size=0.2, random_state=42)
    print(f"[+] Training Set: {X_train.shape[0]:,} samples (Frauds: {int(y_train.sum())})")
    print(f"[+] Test Set:     {X_test.shape[0]:,} samples (Frauds: {int(y_test.sum())})")
    
    # Save the preprocessor
    preprocessor.save(Config.SCALER_PATH)
    
    # Define models dictionary
    models = {
        'Logistic Regression': LogisticRegression(
            class_weight='balanced',
            max_iter=1000,
            solver='lbfgs',
            random_state=42
        ),
        'Decision Tree': DecisionTreeClassifier(
            class_weight='balanced',
            max_depth=8,
            min_samples_split=20,
            random_state=42
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=100,
            class_weight='balanced',
            max_depth=12,
            min_samples_split=10,
            n_jobs=-1,
            random_state=42
        ),
        'Support Vector Machine': CalibratedClassifierCV(
            estimator=LinearSVC(class_weight='balanced', max_iter=2000, random_state=42, dual=False),
            cv=3
        ),
        'Isolation Forest': IsolationForest(
            n_estimators=100,
            contamination=0.0017,
            n_jobs=-1,
            random_state=42
        )
    }
    
    metrics_results = {}
    roc_data = {}
    pr_data = {}
    confusion_matrices = {}
    trained_estimators = {}
    
    # Train each model
    for name, model in models.items():
        print(f"\n[*] Training {name}...")
        start_t = time.time()
        
        if name == 'Isolation Forest':
            # Unsupervised: fit on X_train features only
            model.fit(X_train)
            train_duration = time.time() - start_t
            
            # Predict: 1 is normal, -1 is anomaly
            raw_preds = model.predict(X_test)
            y_pred = np.where(raw_preds == -1, 1, 0)
            
            # Anomaly scores: lower is more abnormal, invert for probability proxy
            anomaly_scores = -model.score_samples(X_test)
            min_s, max_s = anomaly_scores.min(), anomaly_scores.max()
            y_prob = (anomaly_scores - min_s) / (max_s - min_s + 1e-9)
        else:
            model.fit(X_train, y_train)
            train_duration = time.time() - start_t
            
            y_pred = model.predict(X_test)
            if hasattr(model, 'predict_proba'):
                y_prob = model.predict_proba(X_test)[:, 1]
            else:
                y_prob = y_pred.astype(float)
                
        trained_estimators[name] = model
        
        # Calculate Evaluation Metrics
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        roc_auc = float(roc_auc_score(y_test, y_prob))
        pr_auc = float(average_precision_score(y_test, y_prob))
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        print(f"  [>] Training Time: {train_duration:.2f}s")
        print(f"  [>] Accuracy:   {acc:.4f} | Precision: {prec:.4f}")
        print(f"  [>] Recall:     {rec:.4f} | F1-Score:  {f1:.4f}")
        print(f"  [>] ROC-AUC:    {roc_auc:.4f} | PR-AUC:    {pr_auc:.4f}")
        print(f"  [>] Confusion Matrix: TN={cm[0][0]}, FP={cm[0][1]}, FN={cm[1][0]}, TP={cm[1][1]}")
        
        metrics_results[name] = {
            'accuracy': round(acc, 4),
            'precision': round(prec, 4),
            'recall': round(rec, 4),
            'f1_score': round(f1, 4),
            'roc_auc': round(roc_auc, 4),
            'pr_auc': round(pr_auc, 4),
            'confusion_matrix': cm,
            'training_time_sec': round(train_duration, 2)
        }
        
        # Compute ROC & PR curves for plotting
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        precision_vals, recall_vals, _ = precision_recall_curve(y_test, y_prob)
        roc_data[name] = (fpr, tpr, roc_auc)
        pr_data[name] = (recall_vals, precision_vals, pr_auc)
        confusion_matrices[name] = cm

    # 3. Save Comparative Metrics JSON
    metrics_path = Config.METRICS_PATH
    with open(metrics_path, 'w') as f:
        json.dump(metrics_results, f, indent=4)
    print(f"\n[+] Saved comparative benchmark metrics to: {metrics_path}")
    
    # 4. Select and Save Best Model (based on F1-score & PR-AUC)
    # Exclude Isolation Forest for supervised deployment
    supervised_models = {k: v for k, v in metrics_results.items() if k != 'Isolation Forest'}
    best_model_name = max(supervised_models, key=lambda k: (supervised_models[k]['f1_score'], supervised_models[k]['pr_auc']))
    best_model = trained_estimators[best_model_name]
    
    joblib.dump(best_model, Config.MODEL_PATH)
    print(f"[+] BEST PERFORMING MODEL: {best_model_name} (F1: {metrics_results[best_model_name]['f1_score']})")
    print(f"[+] Saved deployed model artifact to: {Config.MODEL_PATH}")
    
    # 5. Generate and Save Visualizations
    img_dir = PROJECT_ROOT / 'static' / 'images'
    img_dir.mkdir(parents=True, exist_ok=True)
    
    # Plot ROC Curves
    print("[*] Generating ROC Curves Plot...")
    plt.figure(figsize=(10, 7))
    for name, (fpr, tpr, auc_val) in roc_data.items():
        plt.plot(fpr, tpr, lw=2, label=f"{name} (AUC = {auc_val:.3f})")
    plt.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Random Guess (AUC = 0.500)')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
    plt.ylabel('True Positive Rate (Recall / Sensitivity)', fontsize=12)
    plt.title('Receiver Operating Characteristic (ROC) Comparison', fontsize=14, fontweight='bold', pad=12)
    plt.legend(loc='lower right', frameon=True)
    plt.tight_layout()
    plt.savefig(img_dir / 'roc_curves.png', dpi=200)
    plt.close()
    
    # Plot Precision-Recall Curves
    print("[*] Generating Precision-Recall Curves Plot...")
    plt.figure(figsize=(10, 7))
    for name, (recall_vals, precision_vals, pr_auc_val) in pr_data.items():
        plt.plot(recall_vals, precision_vals, lw=2, label=f"{name} (PR-AUC = {pr_auc_val:.3f})")
    plt.xlabel('Recall (Fraud Detection Rate)', fontsize=12)
    plt.ylabel('Precision (True Positive Fidelity)', fontsize=12)
    plt.title('Precision-Recall Curves (Critical for Severe Class Imbalance)', fontsize=14, fontweight='bold', pad=12)
    plt.legend(loc='lower left', frameon=True)
    plt.tight_layout()
    plt.savefig(img_dir / 'pr_curves.png', dpi=200)
    plt.close()
    
    # Plot Confusion Matrices Grid
    print("[*] Generating Confusion Matrices Grid...")
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()
    
    for idx, (name, cm_list) in enumerate(confusion_matrices.items()):
        ax = axes[idx]
        cm_arr = np.array(cm_list)
        sns.heatmap(cm_arr, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax,
                    xticklabels=['Legit (0)', 'Fraud (1)'],
                    yticklabels=['Legit (0)', 'Fraud (1)'])
        ax.set_title(f"{name}", fontsize=12, fontweight='bold')
        ax.set_xlabel('Predicted Label')
        ax.set_ylabel('True Label')
        
    # Hide empty 6th subplot
    fig.delaxes(axes[5])
    plt.suptitle('Confusion Matrix Comparison across Algorithms (Test Set: N=56,962)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(img_dir / 'confusion_matrices.png', dpi=200)
    plt.close()
    
    # Plot Random Forest Feature Importance
    print("[*] Generating Random Forest Feature Importance Plot...")
    rf_model = trained_estimators['Random Forest']
    if hasattr(rf_model, 'feature_importances_'):
        importances = rf_model.feature_importances_
        feature_names = preprocessor.feature_columns
        indices = np.argsort(importances)[::-1][:15] # Top 15
        
        plt.figure(figsize=(11, 6))
        plt.title('Top 15 Feature Importances (Random Forest Gini Impurity Reduction)', fontsize=13, fontweight='bold', pad=12)
        plt.bar(range(15), importances[indices], color='#1e3a8a', align='center')
        plt.xticks(range(15), [feature_names[i] for i in indices], rotation=45, ha='right')
        plt.ylabel('Relative Importance')
        plt.tight_layout()
        plt.savefig(img_dir / 'feature_importance.png', dpi=200)
        plt.close()
        
    print("\n" + "=" * 70)
    print("  MODEL TRAINING, EVALUATION, AND ARTIFACT EXPORT COMPLETE!")
    print("=" * 70)

if __name__ == '__main__':
    train_and_evaluate_models()
