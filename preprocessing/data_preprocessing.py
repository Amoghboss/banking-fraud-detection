"""
Data Preprocessing & Feature Engineering Module
Handles data ingestion, scaling, train/test splitting without leakage,
and single/batch inference transformations.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler, StandardScaler
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from config import Config

FEATURE_COLUMNS = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']

class DataPreprocessor:
    """Production-grade preprocessor for banking fraud transaction data."""
    
    def __init__(self):
        self.amount_scaler = RobustScaler()
        self.time_scaler = RobustScaler()
        self.feature_columns = FEATURE_COLUMNS
        # Baselines for explainability (populated during training or fallback reference)
        self.legit_feature_means = {
            'V14': 0.0, 'V10': 0.0, 'V12': 0.0, 'V17': 0.0,
            'V4': 0.0, 'V11': 0.0, 'Amount': 88.29
        }
        self.legit_feature_stds = {
            'V14': 0.95, 'V10': 1.05, 'V12': 0.98, 'V17': 0.85,
            'V4': 1.41, 'V11': 1.02, 'Amount': 250.12
        }

    def load_dataset(self, csv_path=None):
        """Loads transaction dataset from disk."""
        path = csv_path or Config.DATASET_PATH
        if not Path(path).exists():
            raise FileNotFoundError(f"Dataset not found at {path}")
        df = pd.read_csv(path)
        return df

    def clean_dataset(self, df, remove_duplicates=False):
        """Validates and cleans data."""
        df_clean = df.copy()
        # Fill missing values if any
        if df_clean.isnull().values.any():
            df_clean = df_clean.fillna(df_clean.median(numeric_only=True))
        if remove_duplicates:
            df_clean = df_clean.drop_duplicates()
        return df_clean

    def split_and_scale(self, df, test_size=0.2, random_state=42):
        """
        Splits dataset into stratified train and test sets, then fits scalers ONLY on train.
        Prevents data leakage.
        """
        df_clean = self.clean_dataset(df)
        X = df_clean[self.feature_columns].copy()
        y = df_clean['Class'].copy()
        
        # Stratified train/test split preserves class ratio (0.17% fraud) in both splits
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Fit scalers strictly on training data
        X_train_scaled = X_train.copy()
        X_test_scaled = X_test.copy()
        
        self.amount_scaler.fit(X_train[['Amount']])
        self.time_scaler.fit(X_train[['Time']])
        
        X_train_scaled['Amount'] = self.amount_scaler.transform(X_train[['Amount']])
        X_train_scaled['Time'] = self.time_scaler.transform(X_train[['Time']])
        
        X_test_scaled['Amount'] = self.amount_scaler.transform(X_test[['Amount']])
        X_test_scaled['Time'] = self.time_scaler.transform(X_test[['Time']])
        
        # Compute legitimate class baseline statistics from training set
        legit_train = X_train[y_train == 0]
        for feat in ['V14', 'V10', 'V12', 'V17', 'V4', 'V11', 'Amount']:
            if feat in legit_train:
                self.legit_feature_means[feat] = float(legit_train[feat].mean())
                self.legit_feature_stds[feat] = float(legit_train[feat].std() or 1.0)
                
        return X_train_scaled, X_test_scaled, y_train, y_test

    def transform_single(self, input_dict):
        """
        Transforms a single transaction dictionary into a 2D array matching the model schema.
        Fills missing V1-V28 features with neutral defaults (0.0).
        """
        row = {}
        row['Time'] = float(input_dict.get('Time', 0.0))
        for i in range(1, 29):
            col = f'V{i}'
            row[col] = float(input_dict.get(col, 0.0))
        row['Amount'] = float(input_dict.get('Amount', 0.0))
        
        df_single = pd.DataFrame([row], columns=self.feature_columns)
        
        # Scale Amount and Time using fitted scalers
        df_single['Amount'] = self.amount_scaler.transform(df_single[['Amount']])
        df_single['Time'] = self.time_scaler.transform(df_single[['Time']])
        
        return df_single

    def transform_dataframe(self, df):
        """Transforms a batch dataframe of uploaded transactions."""
        df_proc = df.copy()
        # Verify required columns or populate missing with 0.0
        for col in self.feature_columns:
            if col not in df_proc.columns:
                df_proc[col] = 0.0
                
        df_ordered = df_proc[self.feature_columns].copy()
        df_ordered['Amount'] = self.amount_scaler.transform(df_ordered[['Amount']])
        df_ordered['Time'] = self.time_scaler.transform(df_ordered[['Time']])
        return df_ordered

    def explain_transaction(self, input_dict, fraud_prob):
        """
        Calculates key contributing indicators/deviations for risk explainability.
        Flags unusual features (e.g. extreme negative V14, V10, V12 or high V4, abnormal Amount).
        """
        reasons = []
        raw_amt = float(input_dict.get('Amount', 0.0))
        
        # Check Amount anomaly
        if raw_amt > 1500:
            reasons.append(f"Unusually high transaction volume (${raw_amt:,.2f}) compared to normal average ($88.29).")
        elif raw_amt == 0:
            reasons.append("Zero-value card testing / verification authorization pattern detected.")
            
        # Check top diagnostic PCA components (V14, V12, V10 are known negative fraud markers)
        for feat in ['V14', 'V12', 'V10', 'V17']:
            val = float(input_dict.get(feat, 0.0))
            baseline_mean = self.legit_feature_means.get(feat, 0.0)
            baseline_std = self.legit_feature_stds.get(feat, 1.0)
            z_score = (val - baseline_mean) / (baseline_std or 1.0)
            if z_score < -3.0:
                reasons.append(f"Critical anomaly in behavioural factor {feat} (Z-score: {z_score:.2f}, highly indicative of identity compromise).")
                
        # Check positive fraud markers (V4, V11)
        for feat in ['V4', 'V11']:
            val = float(input_dict.get(feat, 0.0))
            baseline_mean = self.legit_feature_means.get(feat, 0.0)
            baseline_std = self.legit_feature_stds.get(feat, 1.0)
            z_score = (val - baseline_mean) / (baseline_std or 1.0)
            if z_score > 3.0:
                reasons.append(f"Uncharacteristic spike in transaction factor {feat} (Z-score: +{z_score:.2f}).")
                
        if not reasons:
            if fraud_prob >= 0.5:
                reasons.append("Multi-factor non-linear anomaly detected across combined transaction vectors.")
            else:
                reasons.append("Transaction behavioral pattern aligns within legitimate customer baseline parameters.")
                
        return reasons

    def save(self, filepath=None):
        """Saves fitted scalers and preprocessor to disk."""
        path = filepath or Config.SCALER_PATH
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        print(f"[+] Saved fitted DataPreprocessor to: {path}")

    @classmethod
    def load(cls, filepath=None):
        """Loads fitted preprocessor from disk."""
        path = filepath or Config.SCALER_PATH
        if not Path(path).exists():
            raise FileNotFoundError(f"Scaler file not found at {path}")
        return joblib.load(path)
