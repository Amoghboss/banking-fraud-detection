"""
Transactions Blueprint
Handles manual transaction entry, CSV bulk upload, real-time prediction,
history browsing, filtering, and transaction investigation.
"""
import json
import uuid
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
from database.db import db, TransactionRecord
from routes.auth import login_required, log_activity
from routes.dashboard import get_ml_engine
from config import Config

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions')
@login_required
def index():
    return render_template('transactions.html')

@transactions_bp.route('/transactions/predict-single', methods=['POST'])
@login_required
def predict_single():
    """Processes manual transaction entry and generates fraud classification."""
    try:
        model, preprocessor = get_ml_engine()
        
        # Read form inputs
        tx_id = request.form.get('transaction_id', '').strip()
        if not tx_id:
            tx_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
            
        try:
            amount = float(request.form.get('amount', 0.0))
            time_val = float(request.form.get('time', 0.0))
        except ValueError:
            flash('Invalid numeric value for Amount or Time.', 'danger')
            return redirect(url_for('transactions.index'))
            
        # Collect V1-V28 values
        sample_dict = {'Time': time_val, 'Amount': amount}
        for i in range(1, 29):
            field_name = f'V{i}'
            val_str = request.form.get(field_name, '').strip()
            sample_dict[field_name] = float(val_str) if val_str else 0.0
            
        # Preprocess and Predict
        X_vec = preprocessor.transform_single(sample_dict)
        prob = float(model.predict_proba(X_vec)[0, 1])
        
        # Determine risk and class
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
            
        indicators = preprocessor.explain_transaction(sample_dict, prob)
        
        # Save to database
        record = TransactionRecord(
            transaction_id=tx_id,
            time_offset=time_val,
            amount=amount,
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
            indicators_json=json.dumps(indicators),
            investigation_status='Pending Review' if is_fraud else 'Resolved'
        )
        db.session.add(record)
        db.session.commit()
        
        log_activity('SINGLE_PREDICTION', f"Analyzed transaction {tx_id}: {prediction} ({risk} Risk, Prob: {prob:.4f})")
        return redirect(url_for('transactions.results', id=record.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Prediction error: {str(e)}", 'danger')
        return redirect(url_for('transactions.index'))

@transactions_bp.route('/transactions/predict-bulk', methods=['POST'])
@login_required
def predict_bulk():
    """Accepts CSV file upload and performs batch transaction fraud analysis."""
    if 'csv_file' not in request.files:
        flash('No CSV file selected for upload.', 'danger')
        return redirect(url_for('transactions.index'))
        
    file = request.files['csv_file']
    if file.filename == '':
        flash('Please choose a valid CSV file.', 'danger')
        return redirect(url_for('transactions.index'))
        
    if not file.filename.lower().endswith('.csv'):
        flash('Only standard CSV (.csv) files are permitted.', 'danger')
        return redirect(url_for('transactions.index'))
        
    try:
        model, preprocessor = get_ml_engine()
        df_upload = pd.read_csv(file)
        
        # Enforce batch safety limit
        MAX_ROWS = 5000
        if len(df_upload) > MAX_ROWS:
            flash(f"CSV exceeds maximum batch capacity of {MAX_ROWS:,} rows. Processing first {MAX_ROWS:,} rows.", 'warning')
            df_upload = df_upload.head(MAX_ROWS)
            
        # Ensure Amount exists
        if 'Amount' not in df_upload.columns:
            flash("Missing mandatory 'Amount' column in uploaded CSV.", 'danger')
            return redirect(url_for('transactions.index'))
            
        if 'Time' not in df_upload.columns:
            df_upload['Time'] = 0.0
            
        # Preprocess features
        X_mat = preprocessor.transform_dataframe(df_upload)
        probs = model.predict_proba(X_mat)[:, 1]
        
        created_records = []
        bulk_batch_id = uuid.uuid4().hex[:6].upper()
        
        for idx, row in df_upload.iterrows():
            prob = float(probs[idx])
            amt = float(row.get('Amount', 0.0))
            t_val = float(row.get('Time', 0.0))
            
            if prob < Config.RISK_THRESHOLDS['LOW']:
                risk = 'Low'
                pred = 'Legitimate'
                is_f = False
            elif prob < Config.RISK_THRESHOLDS['MEDIUM']:
                risk = 'Medium'
                pred = 'Legitimate'
                is_f = False
            elif prob < Config.RISK_THRESHOLDS['HIGH']:
                risk = 'High'
                pred = 'Fraudulent'
                is_f = True
            else:
                risk = 'Critical'
                pred = 'Fraudulent'
                is_f = True
                
            sample_dict = row.to_dict()
            indicators = preprocessor.explain_transaction(sample_dict, prob)
            
            tx_name = f"BULK-{bulk_batch_id}-{idx+1:04d}"
            
            rec = TransactionRecord(
                transaction_id=tx_name,
                time_offset=t_val,
                amount=amt,
                feature_v1=float(row.get('V1', 0.0)),
                feature_v2=float(row.get('V2', 0.0)),
                feature_v3=float(row.get('V3', 0.0)),
                feature_v4=float(row.get('V4', 0.0)),
                feature_v10=float(row.get('V10', 0.0)),
                feature_v12=float(row.get('V12', 0.0)),
                feature_v14=float(row.get('V14', 0.0)),
                feature_v17=float(row.get('V17', 0.0)),
                prediction=pred,
                is_fraud=is_f,
                fraud_probability=prob,
                risk_level=risk,
                indicators_json=json.dumps(indicators),
                investigation_status='Pending Review' if is_f else 'Resolved'
            )
            created_records.append(rec)
            
        db.session.bulk_save_objects(created_records)
        db.session.commit()
        
        fraud_count = sum(1 for r in created_records if r.is_fraud)
        log_activity('BULK_CSV_UPLOAD', f"Processed {len(created_records):,} rows from '{file.filename}'. Flagged {fraud_count:,} frauds.")
        
        flash(f"Successfully processed {len(created_records):,} transactions. Detected {fraud_count:,} potential fraudulent activities.", 'success')
        return redirect(url_for('transactions.history', search=f"BULK-{bulk_batch_id}"))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Batch analysis failed: {str(e)}", 'danger')
        return redirect(url_for('transactions.index'))

@transactions_bp.route('/transactions/results/<int:id>')
@login_required
def results(id):
    """Detailed view for a specific analyzed transaction."""
    record = db.session.get(TransactionRecord, id)
    if not record:
        flash('Transaction not found.', 'danger')
        return redirect(url_for('transactions.history'))
    return render_template('results.html', tx=record)

@transactions_bp.route('/transactions/history')
@login_required
def history():
    """Filterable and searchable transaction history."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    risk_filter = request.args.get('risk', '').strip()
    status_filter = request.args.get('status', '').strip()
    investigation_filter = request.args.get('investigation', '').strip()
    
    query = TransactionRecord.query
    
    if search:
        query = query.filter(TransactionRecord.transaction_id.ilike(f"%{search}%"))
    if risk_filter:
        query = query.filter_by(risk_level=risk_filter)
    if status_filter:
        if status_filter == 'Fraudulent':
            query = query.filter_by(is_fraud=True)
        elif status_filter == 'Legitimate':
            query = query.filter_by(is_fraud=False)
    if investigation_filter:
        query = query.filter_by(investigation_status=investigation_filter)
        
    pagination = query.order_by(TransactionRecord.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template(
        'history.html',
        pagination=pagination,
        search=search,
        risk_filter=risk_filter,
        status_filter=status_filter,
        investigation_filter=investigation_filter
    )

@transactions_bp.route('/transactions/investigate/<int:id>', methods=['POST'])
@login_required
def investigate(id):
    """Allows administrators to flag, confirm fraud, or mark false positive."""
    record = db.session.get(TransactionRecord, id)
    if not record:
        flash('Transaction not found.', 'danger')
        return redirect(url_for('transactions.history'))
    new_status = request.form.get('investigation_status', record.investigation_status)
    notes = request.form.get('admin_notes', '').strip()
    
    record.investigation_status = new_status
    record.is_investigated = True
    if notes:
        record.admin_notes = notes
        
    db.session.commit()
    log_activity('INVESTIGATION_UPDATED', f"Updated {record.transaction_id} to '{new_status}'.")
    flash(f"Investigation status updated for {record.transaction_id}.", 'success')
    return redirect(request.referrer or url_for('transactions.history'))
