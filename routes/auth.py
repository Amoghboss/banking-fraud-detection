"""
Authentication Blueprint
Handles administrator login, session management, logout, and security checks.
"""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import db, User, AuditLog

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def log_activity(action, details=None):
    """Helper to record an administrative action in the audit log."""
    try:
        user_id = session.get('user_id')
        username = session.get('username', 'Anonymous')
        ip_addr = request.remote_addr or '127.0.0.1'
        log_entry = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            ip_address=ip_addr,
            details=details
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('login.html')
            
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session.permanent = True
            
            user.last_login = db.func.now()
            db.session.commit()
            
            log_activity('ADMIN_LOGIN', f"User '{username}' logged in successfully.")
            flash(f"Welcome back, {user.username}!", 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            log_activity('FAILED_LOGIN_ATTEMPT', f"Failed login attempt for username '{username}'.")
            flash('Invalid administrator credentials. Please check your credentials.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'User')
    log_activity('ADMIN_LOGOUT', f"User '{username}' logged out.")
    session.clear()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))
