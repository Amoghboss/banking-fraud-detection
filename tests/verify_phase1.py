"""
Phase 1 Verification Script
Validates environment dependencies, directory layout, and configuration.
"""
import sys
import os
from pathlib import Path

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_phase1_checks():
    print("=" * 60)
    print("  PHASE 1 ENVIRONMENT & ARCHITECTURE VERIFICATION")
    print("=" * 60)
    
    # 1. Python version check
    py_ver = sys.version_info
    print(f"[+] Python Version: {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    assert py_ver.major == 3 and py_ver.minor >= 9, "Python 3.9+ required!"
    
    # 2. Check Directory Structure
    required_dirs = [
        PROJECT_ROOT / 'dataset',
        PROJECT_ROOT / 'models',
        PROJECT_ROOT / 'preprocessing',
        PROJECT_ROOT / 'database',
        PROJECT_ROOT / 'routes',
        PROJECT_ROOT / 'templates',
        PROJECT_ROOT / 'static' / 'css',
        PROJECT_ROOT / 'static' / 'js',
        PROJECT_ROOT / 'static' / 'images',
        PROJECT_ROOT / 'tests',
        PROJECT_ROOT / 'reports_export'
    ]
    
    print("\n[+] Verifying Directory Structure:")
    for d in required_dirs:
        if d.exists() and d.is_dir():
            print(f"  [OK] Directory: {d.relative_to(PROJECT_ROOT)}")
        else:
            print(f"  [FAIL] Missing: {d.relative_to(PROJECT_ROOT)}")
            return False
            
    # 3. Check Configuration Loading
    print("\n[+] Testing Configuration Module:")
    try:
        from config import Config, config
        dev_cfg = config['development']
        print(f"  [OK] Loaded Secret Key: {dev_cfg.SECRET_KEY[:8]}***")
        print(f"  [OK] SQLite Path: {dev_cfg.SQLALCHEMY_DATABASE_URI}")
        print(f"  [OK] Risk Thresholds: {dev_cfg.RISK_THRESHOLDS}")
    except Exception as e:
        print(f"  [FAIL] Config loading failed: {e}")
        return False
        
    # 4. Check Library Imports
    print("\n[+] Testing Dependency Imports:")
    modules = [
        ('Flask', 'flask'),
        ('Werkzeug', 'werkzeug'),
        ('SQLAlchemy', 'sqlalchemy'),
        ('Scikit-Learn', 'sklearn'),
        ('Pandas', 'pandas'),
        ('NumPy', 'numpy'),
        ('Matplotlib', 'matplotlib'),
        ('Seaborn', 'seaborn'),
        ('Joblib', 'joblib')
    ]
    
    for name, mod in modules:
        try:
            m = __import__(mod)
            ver = getattr(m, '__version__', 'detected')
            print(f"  [OK] {name:<15} version: {ver}")
        except ImportError as e:
            print(f"  [FAIL] {name:<15} Import Error: {e}")
            return False
            
    print("\n" + "=" * 60)
    print("  PHASE 1 VERIFICATION PASSED: ENVIRONMENT & ARCHITECTURE READY!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = run_phase1_checks()
    sys.exit(0 if success else 1)
