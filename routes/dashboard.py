"""
Dashboard Blueprint
Renders executive dashboard views and serves analytical metrics for Chart.js.
"""
import json
import random
import uuid
from pathlib import Path
import pandas as pd
from flask import Blueprint, render_template, jsonify, request
from database.db import db, TransactionRecord
from routes.auth import login_required, log_activity
from config import Config
from preprocessing.data_preprocessing import DataPreprocessor
import joblib

dashboard_bp = Blueprint('dashboard', __name__)

# Cache model and preprocessor for low-latency inference
_model = None
_preprocessor = None

def get_ml_engine():
    global _model, _preprocessor
    if _model is None:
        if Path(Config.MODEL_PATH).exists():
            _model = joblib.load(Config.MODEL_PATH)
        else:
            raise FileNotFoundError("Trained model not found. Run models/train_model.py first.")
    if _preprocessor is None:
        if Path(Config.SCALER_PATH).exists():
            _preprocessor = joblib.load(Config.SCALER_PATH)
        else:
            _preprocessor = DataPreprocessor()
    return _model, _preprocessor

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Fetch summary statistics
    total_tx = TransactionRecord.query.count()
    fraud_tx = TransactionRecord.query.filter_by(is_fraud=True).count()
    legit_tx = total_tx - fraud_tx
    fraud_rate = (fraud_tx / total_tx * 100) if total_tx > 0 else 0.0
    high_critical_risk = TransactionRecord.query.filter(
        TransactionRecord.risk_level.in_(['High', 'Critical'])
    ).count()
    
    # Recent suspicious / flagged transactions
    recent_suspicious = TransactionRecord.query.filter(
        TransactionRecord.risk_level.in_(['Medium', 'High', 'Critical'])
    ).order_by(TransactionRecord.created_at.desc()).limit(8).all()
    
    # Load Model Metrics for summary badge
    metrics_data = {}
    if Path(Config.METRICS_PATH).exists():
        with open(Config.METRICS_PATH, 'r') as f:
            metrics_data = json.load(f)
            
    rf_metrics = metrics_data.get('Random Forest', {})
    
    return render_template(
        'dashboard.html',
        total_tx=total_tx,
        fraud_tx=fraud_tx,
        legit_tx=legit_tx,
        fraud_rate=round(fraud_rate, 2),
        high_critical_risk=high_critical_risk,
        recent_suspicious=recent_suspicious,
        rf_metrics=rf_metrics
    )

@dashboard_bp.route('/api/dashboard-charts')
@login_required
def dashboard_charts():
    """Provides structured data for Chart.js interactive visualizations."""
    # 1. Risk Level Counts
    risk_counts = {
        'Low': TransactionRecord.query.filter_by(risk_level='Low').count(),
        'Medium': TransactionRecord.query.filter_by(risk_level='Medium').count(),
        'High': TransactionRecord.query.filter_by(risk_level='High').count(),
        'Critical': TransactionRecord.query.filter_by(risk_level='Critical').count()
    }
    
    # 2. Status Breakdown
    legit_cnt = TransactionRecord.query.filter_by(is_fraud=False).count()
    fraud_cnt = TransactionRecord.query.filter_by(is_fraud=True).count()
    
    # 3. Recent 10 transactions amounts & risk for scatter/line chart
    recent_txs = TransactionRecord.query.order_by(
        TransactionRecord.created_at.desc()
    ).limit(15).all()
    
    timeline = []
    for tx in reversed(recent_txs):
        timeline.append({
            'id': tx.transaction_id[:8],
            'amount': tx.amount,
            'probability': round(tx.fraud_probability * 100, 1),
            'risk_level': tx.risk_level,
            'is_fraud': tx.is_fraud
        })
        
    return jsonify({
        'risk_distribution': risk_counts,
        'class_breakdown': {'Legitimate': legit_cnt, 'Fraudulent': fraud_cnt},
        'timeline': timeline
    })

@dashboard_bp.route('/api/simulate-transaction', methods=['POST'])
@login_required
def simulate_transaction():
    """
    Simulates an incoming banking transaction using real benchmark distributions.
    Executes live model inference and stores the result into SQLite.
    """
    try:
        model, preprocessor = get_ml_engine()
        
        # Decide if this simulation is normal or fraud (approx 15% chance for demonstration)
        is_target_fraud = random.random() < 0.20
        
        # Realistic sample generation
        sim_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        time_offset = random.uniform(100.0, 170000.0)
        
        sample_dict = {'Time': time_offset}
        
        if is_target_fraud:
            # Fraudulent characteristics: extreme V14, V12, V10 negative, high V4, abnormal amount
            sample_dict['V14'] = random.uniform(-14.0, -4.5)
            sample_dict['V12'] = random.uniform(-10.0, -3.5)
            sample_dict['V10'] = random.uniform(-9.0, -3.0)
            sample_dict['V17'] = random.uniform(-8.0, -2.5)
            sample_dict['V4'] = random.uniform(3.0, 8.5)
            sample_dict['V11'] = random.uniform(2.5, 6.0)
            sample_dict['Amount'] = random.choice([0.0, random.uniform(1.0, 30.0), random.uniform(400.0, 2400.0)])
            # Fill other features
            for i in range(1, 29):
                k = f'V{i}'
                if k not in sample_dict:
                    sample_dict[k] = random.gauss(0.0, 1.5)
        else:
            # Normal legitimate characteristics
            sample_dict['Amount'] = round(random.expovariate(1/75) + 2.5, 2)
            if sample_dict['Amount'] > 1200:
                sample_dict['Amount'] = 150.0
            for i in range(1, 29):
                sample_dict[f'V{i}'] = random.gauss(0.0, 0.9)
                
        # Transform and Predict
        X_vec = preprocessor.transform_single(sample_dict)
        prob = float(model.predict_proba(X_vec)[0, 1])
        
        # Categorize Risk
        if prob < Config.RISK_THRESHOLDS['LOW']:
            risk = 'Low'
            prediction = 'Legitimate'
            is_fraud = False
        elif prob < Config.RISK_THRESHOLDS['MEDIUM']:
            risk = 'Medium'
            prediction = 'Legitimate'
            is_fraud = False
        elif prob < Config.RISK_THRESHOLDS['HIGH']:
            risk = 'High'
            prediction = 'Fraudulent'
            is_fraud = True
        else:
            risk = 'Critical'
            prediction = 'Fraudulent'
            is_fraud = True
            
        reasons = preprocessor.explain_transaction(sample_dict, prob)
        
        # Persist to database
        record = TransactionRecord(
            transaction_id=sim_id,
            time_offset=time_offset,
            amount=sample_dict['Amount'],
            feature_v1=sample_dict.get('V1', 0.0),
            feature_v2=sample_dict.get('V2', 0.0),
            feature_v3=sample_dict.get('V3', 0.0),
            feature_v4=sample_dict.get('V4', 0.0),
            feature_v10=sample_dict.get('V10', 0.0),
            feature_v12=sample_dict.get('V12', 0.0),
            feature_v14=sample_dict.get('V14', 0.0),
            feature_v17=sample_dict.get('V17', 0.0),
            features_json=json.dumps(sample_dict),
            prediction=prediction,
            is_fraud=is_fraud,
            fraud_probability=prob,
            risk_level=risk,
            indicators_json=json.dumps(reasons),
            investigation_status='Pending Review' if is_fraud else 'Resolved'
        )
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transaction': record.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
