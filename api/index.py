import os
import sys
from pathlib import Path

# Add project root to Python search path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Signal serverless execution
os.environ['VERCEL'] = '1'
os.environ['SERVERLESS'] = '1'

from app import create_app

# Vercel entrypoint
app = create_app('production')
