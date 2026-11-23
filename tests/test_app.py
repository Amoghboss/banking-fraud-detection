"""
Automated Test Suite for Banking Fraud Detection System
Tests authentication, authorization, ML prediction pipelines,
CSV bulk ingestion, security validations, and reporting.
"""
import io
import sys
import uuid
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from database.db import db, User, TransactionRecord, AuditLog

class SentinelFraudDetectionTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('development')
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.logout()

    def tearDown(self):
        self.ctx.pop()

    def login(self, username='admin', password='Admin@2026!'):
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    # 1. Test Authentication
    def test_login_success(self):
        res = self.login()
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Executive Fraud Intelligence Dashboard', res.data)

    def test_login_invalid_password(self):
        res = self.login(password='WrongPassword')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Invalid administrator credentials', res.data)

    # 2. Test Authorization & Route Protection
    def test_protected_routes_redirect_unauthenticated(self):
        self.logout()
        routes = ['/dashboard', '/transactions', '/transactions/history', '/reports', '/performance']
        for route in routes:
            res = self.client.get(route, follow_redirects=False)
            self.assertEqual(res.status_code, 302, f"Route {route} was not protected!")
            self.assertIn('/login', res.headers['Location'])

    # 3. Test Dashboard KPI & Charts API
    def test_dashboard_api(self):
        self.login()
        res = self.client.get('/api/dashboard-charts')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertIn('risk_distribution', json_data)
        self.assertIn('class_breakdown', json_data)
        self.assertIn('timeline', json_data)

    # 4. Test Single Transaction Prediction (Legitimate)
    def test_predict_single_legitimate(self):
        self.login()
        unique_id = f"TXN-TEST-LEGIT-{uuid.uuid4().hex[:6]}"
        res = self.client.post('/transactions/predict-single', data={
            'transaction_id': unique_id,
            'amount': '35.50',
            'time': '12500',
            'V14': '0.12',
            'V12': '-0.05',
            'V10': '0.10',
            'V4': '0.18'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'LEGITIMATE TRANSACTION', res.data)
        
        # Verify in database
        tx = TransactionRecord.query.filter_by(transaction_id=unique_id).first()
        self.assertIsNotNone(tx)
        self.assertFalse(tx.is_fraud)
        self.assertLess(tx.fraud_probability, 0.50)

    # 5. Test Single Transaction Prediction (Fraudulent Pattern)
    def test_predict_single_fraudulent(self):
        self.login()
        unique_id = f"TXN-TEST-FRAUD-{uuid.uuid4().hex[:6]}"
        res = self.client.post('/transactions/predict-single', data={
            'transaction_id': unique_id,
            'amount': '950.00',
            'time': '25000',
            'V14': '-9.50', # Severe negative anomaly
            'V12': '-7.20',
            'V10': '-6.10',
            'V17': '-8.00',
            'V4': '5.20',   # Severe positive anomaly
            'V11': '4.10'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'POTENTIAL FRAUD DETECTED', res.data)
        
        tx = TransactionRecord.query.filter_by(transaction_id=unique_id).first()
        self.assertIsNotNone(tx)
        self.assertTrue(tx.is_fraud)
        self.assertIn(tx.risk_level, ['High', 'Critical'])

    # 6. Test CSV Bulk Ingestion
    def test_bulk_csv_upload(self):
        self.login()
        csv_content = (
            "Time,V1,V2,V3,V4,V10,V12,V14,Amount\n"
            "100,0.1,-0.2,0.3,0.1,0.05,-0.05,0.1,25.00\n"
            "200,-1.5,2.1,-2.5,4.8,-5.5,-6.2,-8.9,850.00\n"
        )
        data = {
            'csv_file': (io.BytesIO(csv_content.encode('utf-8')), 'test_batch.csv')
        }
        res = self.client.post('/transactions/predict-bulk', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        # Should redirect to history with flash message
        self.assertIn(b'Transaction Surveillance History', res.data)

    # 7. Test Non-CSV Upload Rejection
    def test_invalid_file_upload_rejected(self):
        self.login()
        data = {
            'csv_file': (io.BytesIO(b"malicious executable"), 'test_script.exe')
        }
        res = self.client.post('/transactions/predict-bulk', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Only standard CSV (.csv) files are permitted', res.data)

    # 8. Test CSV Report Export
    def test_export_csv_report(self):
        self.login()
        res = self.client.get('/reports/export-csv')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn(b'Transaction ID,Time Offset,Amount ($),Prediction', res.data)

    # 9. Test Investigation Update
    def test_investigation_update(self):
        self.login()
        unique_id = f"TXN-INV-{uuid.uuid4().hex[:6]}"
        tx = TransactionRecord(
            transaction_id=unique_id,
            amount=320.0,
            prediction='Fraudulent',
            is_fraud=True,
            fraud_probability=0.88,
            risk_level='Critical',
            investigation_status='Pending Review'
        )
        db.session.add(tx)
        db.session.commit()
        
        res = self.client.post(f'/transactions/investigate/{tx.id}', data={
            'investigation_status': 'Confirmed Fraud',
            'admin_notes': 'Cardholder confirmed unauthorized card present transaction.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        updated_tx = db.session.get(TransactionRecord, tx.id)
        self.assertEqual(updated_tx.investigation_status, 'Confirmed Fraud')
        self.assertIn('Cardholder confirmed', updated_tx.admin_notes)

    # 10. Test Real-Time Simulation API
    def test_simulate_transaction_endpoint(self):
        self.login()
        res = self.client.post('/api/simulate-transaction')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('transaction', data)
        self.assertIn('fraud_probability', data['transaction'])

if __name__ == '__main__':
    unittest.main()
