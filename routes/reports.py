"""
Reports Blueprint
Generates downloadable CSV transaction audit logs, model performance reports,
and executive compliance summaries.
"""
import io
import csv
import json
from pathlib import Path
from datetime import datetime
from flask import Blueprint, render_template, Response, request, redirect, url_for, flash
from database.db import db, TransactionRecord
from routes.auth import login_required, log_activity
from config import Config

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def index():
    total_tx = TransactionRecord.query.count()
    fraud_tx = TransactionRecord.query.filter_by(is_fraud=True).count()
    legit_tx = total_tx - fraud_tx
    fraud_rate = (fraud_tx / total_tx * 100) if total_tx > 0 else 0.0
    
    risk_stats = {
        'Low': TransactionRecord.query.filter_by(risk_level='Low').count(),
        'Medium': TransactionRecord.query.filter_by(risk_level='Medium').count(),
        'High': TransactionRecord.query.filter_by(risk_level='High').count(),
        'Critical': TransactionRecord.query.filter_by(risk_level='Critical').count()
    }
    
    # Load model benchmark metrics
    metrics = {}
    if Path(Config.METRICS_PATH).exists():
        with open(Config.METRICS_PATH, 'r') as f:
            metrics = json.load(f)
            
    return render_template(
        'reports.html',
        total_tx=total_tx,
        fraud_tx=fraud_tx,
        legit_tx=legit_tx,
        fraud_rate=round(fraud_rate, 2),
        risk_stats=risk_stats,
        metrics=metrics,
        now=datetime.utcnow()
    )

@reports_bp.route('/reports/export-csv')
@login_required
def export_csv():
    """Streams full transaction log as a formatted CSV file."""
    log_activity('EXPORT_CSV', "Administrator exported transaction history to CSV.")
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV Header
    writer.writerow([
        'Transaction ID', 'Time Offset', 'Amount ($)', 'Prediction',
        'Fraud Probability', 'Risk Level', 'Investigation Status',
        'Contributing Indicators', 'Timestamp'
    ])
    
    records = TransactionRecord.query.order_by(TransactionRecord.created_at.desc()).all()
    for r in records:
        writer.writerow([
            r.transaction_id,
            r.time_offset,
            f"{r.amount:.2f}",
            r.prediction,
            f"{r.fraud_probability:.4f}",
            r.risk_level,
            r.investigation_status,
            "; ".join(r.get_indicators()),
            r.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    output.seek(0)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"banking_fraud_report_{timestamp}.csv"
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@reports_bp.route('/performance')
@login_required
def performance():
    """Dedicated Model Performance & Evaluation Comparison Page."""
    metrics = {}
    if Path(Config.METRICS_PATH).exists():
        with open(Config.METRICS_PATH, 'r') as f:
            metrics = json.load(f)
            
    return render_template('performance.html', metrics=metrics)
