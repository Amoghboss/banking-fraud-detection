"""
Main Flask Application Factory for Banking Fraud Detection System
Initializes SQLAlchemy, blueprints, security middleware, and database seeding.
"""
import os
import random
import uuid
import json
from pathlib import Path
from flask import Flask, render_template
from config import config, Config
from database.db import db, User, TransactionRecord
import joblib

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Ensure instance and upload folders exist safely
    try:
        Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
        Path(app.config['REPORTS_DIR']).mkdir(parents=True, exist_ok=True)
        Path(app.config['DB_PATH']).parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[*] Read-only filesystem detected, skipping directory creation: {e}")
    
    # Initialize Database
    db.init_app(app)
    
    # Register Route Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.transactions import transactions_bp
    from routes.reports import reports_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(reports_bp)
    
    # Register Jinja2 Template Filters
    @app.template_filter('risk_badge')
    def risk_badge_filter(risk_level):
        badges = {
            'Low': 'bg-success text-white',
            'Medium': 'bg-warning text-dark',
            'High': 'bg-orange text-white',
            'Critical': 'bg-danger text-white'
        }
        return badges.get(risk_level, 'bg-secondary text-white')
        
    @app.template_filter('currency')
    def currency_filter(val):
        try:
            return f"${float(val):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    # Context Processor for Global Template Variables
    @app.context_processor
    def inject_global_vars():
        return {
            'app_title': 'Sentinel Fraud Intelligence',
            'app_version': '2.4.0'
        }
        
    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_code=404, error_msg="The requested page could not be found."), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_code=500, error_msg="Internal system error. Please try again shortly."), 500

    # Auto-initialize database tables and seed admin user on startup
    with app.app_context():
        try:
            db.create_all()
            seed_database()
        except Exception as e:
            print(f"[*] Database startup warning: {e}")
        
    return app

def seed_database():
    """Seeds default admin credentials and initial historical transactions if DB is empty."""
    # 1. Admin User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', role='admin')
        admin.set_password('Admin@2026!')
        db.session.add(admin)
        db.session.commit()
        print("[+] Created default administrator: admin / Admin@2026!")

    # 2. Seed Initial Transactions if table is empty
    if TransactionRecord.query.count() == 0:
        print("[*] Seeding initial curated historical transactions...")
        try:
            model = None
            preprocessor = None
            if Path(Config.MODEL_PATH).exists():
                model = joblib.load(Config.MODEL_PATH)
            if Path(Config.SCALER_PATH).exists():
                preprocessor = joblib.load(Config.SCALER_PATH)
                
            sample_data = [
                # Normal everyday transactions
                {'amount': 15.20, 'v14': 0.12, 'v12': -0.05, 'v10': 0.11, 'v4': -0.2, 'fraud_bias': False},
                {'amount': 45.99, 'v14': -0.42, 'v12': 0.22, 'v10': -0.15, 'v4': 0.3, 'fraud_bias': False},
                {'amount': 120.50, 'v14': 0.35, 'v12': -0.18, 'v10': 0.05, 'v4': -0.1, 'fraud_bias': False},
                {'amount': 8.75, 'v14': -0.10, 'v12': 0.02, 'v10': 0.31, 'v4': 0.1, 'fraud_bias': False},
                {'amount': 85.00, 'v14': 0.05, 'v12': -0.30, 'v10': -0.22, 'v4': 0.4, 'fraud_bias': False},
                {'amount': 250.00, 'v14': -0.65, 'v12': 0.15, 'v10': 0.10, 'v4': -0.5, 'fraud_bias': False},
                {'amount': 32.40, 'v14': 0.21, 'v12': -0.08, 'v10': 0.19, 'v4': 0.05, 'fraud_bias': False},
                {'amount': 500.00, 'v14': -0.80, 'v12': -0.40, 'v10': -0.30, 'v4': 0.6, 'fraud_bias': False},
                {'amount': 14.99, 'v14': 0.01, 'v12': 0.05, 'v10': -0.02, 'v4': -0.1, 'fraud_bias': False},
                {'amount': 65.80, 'v14': 0.15, 'v12': -0.12, 'v10': 0.08, 'v4': 0.2, 'fraud_bias': False},
                # High-risk & fraudulent patterns
                {'amount': 1250.00, 'v14': -8.90, 'v12': -6.50, 'v10': -5.80, 'v4': 4.8, 'fraud_bias': True},
                {'amount': 0.00, 'v14': -10.20, 'v12': -7.10, 'v10': -6.40, 'v4': 5.2, 'fraud_bias': True},
                {'amount': 890.50, 'v14': -7.50, 'v12': -5.80, 'v10': -4.90, 'v4': 3.9, 'fraud_bias': True},
                {'amount': 2100.00, 'v14': -11.40, 'v12': -8.20, 'v10': -7.10, 'v4': 6.1, 'fraud_bias': True},
                {'amount': 450.00, 'v14': -6.80, 'v12': -4.50, 'v10': -4.10, 'v4': 3.5, 'fraud_bias': True}
            ]
            
            seeded_records = []
            for item in sample_data:
                sample_dict = {'Time': random.uniform(1000, 80000), 'Amount': item['amount']}
                sample_dict['V14'] = item['v14']
                sample_dict['V12'] = item['v12']
                sample_dict['V10'] = item['v10']
                sample_dict['V4'] = item['v4']
                for i in range(1, 29):
                    k = f'V{i}'
                    if k not in sample_dict:
                        sample_dict[k] = random.gauss(0, 0.5)
                        
                if model and preprocessor:
                    X_vec = preprocessor.transform_single(sample_dict)
                    prob = float(model.predict_proba(X_vec)[0, 1])
                else:
                    prob = 0.92 if item['fraud_bias'] else 0.03
                    
                if prob < 0.20:
                    risk = 'Low'
                    pred = 'Legitimate'
                    is_f = False
                elif prob < 0.50:
                    risk = 'Medium'
                    pred = 'Legitimate'
                    is_f = False
                elif prob < 0.80:
                    risk = 'High'
                    pred = 'Fraudulent'
                    is_f = True
                else:
                    risk = 'Critical'
                    pred = 'Fraudulent'
                    is_f = True
                    
                indicators = preprocessor.explain_transaction(sample_dict, prob) if preprocessor else ["Standard transaction flow."]
                
                tx = TransactionRecord(
                    transaction_id=f"TXN-SEED-{uuid.uuid4().hex[:8].upper()}",
                    time_offset=sample_dict['Time'],
                    amount=item['amount'],
                    feature_v14=item['v14'],
                    feature_v12=item['v12'],
                    feature_v10=item['v10'],
                    feature_v4=item['v4'],
                    features_json=json.dumps(sample_dict),
                    prediction=pred,
                    is_fraud=is_f,
                    fraud_probability=prob,
                    risk_level=risk,
                    indicators_json=json.dumps(indicators),
                    investigation_status='Pending Review' if is_f else 'Resolved'
                )
                seeded_records.append(tx)
                
            db.session.bulk_save_objects(seeded_records)
            db.session.commit()
            print(f"[+] Successfully seeded {len(seeded_records)} historical transactions into database.")
        except Exception as e:
            db.session.rollback()
            print(f"[!] Seeding warning: {e}")

if __name__ == '__main__':
    app = create_app('development')
    print("[*] Starting Sentinel Banking Fraud Detection Server on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
