"""
Database Module for Banking Fraud Detection System
Configures SQLAlchemy models: User, TransactionRecord, and AuditLog.
"""
from datetime import datetime, timezone
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def get_utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    """Administrator and Analyst User Account."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='admin', nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class TransactionRecord(db.Model):
    """Persistent storage for analyzed banking transactions and ML predictions."""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    time_offset = db.Column(db.Float, default=0.0) # Seconds from reference
    amount = db.Column(db.Float, nullable=False)
    
    # Store feature values (can store JSON or key values)
    feature_v1 = db.Column(db.Float, default=0.0)
    feature_v2 = db.Column(db.Float, default=0.0)
    feature_v3 = db.Column(db.Float, default=0.0)
    feature_v4 = db.Column(db.Float, default=0.0)
    feature_v10 = db.Column(db.Float, default=0.0)
    feature_v12 = db.Column(db.Float, default=0.0)
    feature_v14 = db.Column(db.Float, default=0.0)
    feature_v17 = db.Column(db.Float, default=0.0)
    features_json = db.Column(db.Text, nullable=True) # Full V1-V28 vector
    
    # ML Prediction Outputs
    prediction = db.Column(db.String(20), nullable=False) # 'Legitimate' or 'Fraudulent'
    is_fraud = db.Column(db.Boolean, nullable=False, default=False)
    fraud_probability = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False) # 'Low', 'Medium', 'High', 'Critical'
    indicators_json = db.Column(db.Text, nullable=True) # Explanatory factors
    
    # Administrative Investigation State
    is_investigated = db.Column(db.Boolean, default=False)
    investigation_status = db.Column(db.String(30), default='Pending Review') # 'Pending Review', 'Confirmed Fraud', 'False Positive', 'Resolved'
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now, index=True)

    def get_indicators(self):
        if self.indicators_json:
            try:
                return json.loads(self.indicators_json)
            except Exception:
                return [self.indicators_json]
        return []

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'time_offset': self.time_offset,
            'amount': self.amount,
            'prediction': self.prediction,
            'is_fraud': self.is_fraud,
            'fraud_probability': round(self.fraud_probability, 4),
            'risk_level': self.risk_level,
            'indicators': self.get_indicators(),
            'is_investigated': self.is_investigated,
            'investigation_status': self.investigation_status,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class AuditLog(db.Model):
    """Audit log tracking system and administrative activities."""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    username = db.Column(db.String(64), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=get_utc_now, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username or 'System',
            'action': self.action,
            'ip_address': self.ip_address,
            'details': self.details,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
