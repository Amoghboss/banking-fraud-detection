import os
import sys
from pathlib import Path

# Add project root to Python search path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# On Vercel serverless functions, the file system is read-only except /tmp
# Set database and upload directory to /tmp if running in AWS Lambda / Vercel
if os.environ.get('VERCEL') == '1':
    os.environ['DATABASE_URL'] = 'sqlite:////tmp/banking_fraud.db'

from app import create_app

app = create_app('production')
