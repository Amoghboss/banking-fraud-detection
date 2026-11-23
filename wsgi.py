"""
Production WSGI Entrypoint for Sentinel Banking Fraud Detection System
Runs multi-threaded Waitress WSGI server on 0.0.0.0:5000 for high-concurrency production serving.
"""
import os
import sys
from pathlib import Path
from waitress import serve
from app import create_app

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')

app = create_app('production')

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    HOST = '0.0.0.0'
    THREADS = int(os.environ.get('WEB_CONCURRENCY', 6))
    
    print("=" * 70)
    print("   SENTINEL BANKING FRAUD DEFENSE - PRODUCTION WSGI SERVER")
    print("=" * 70)
    print(f"[*] Engine: Waitress Production WSGI Server")
    print(f"[*] Threads: {THREADS} concurrent worker threads")
    print(f"[*] Listening on: http://{HOST}:{PORT}")
    print(f"[*] Local URL:    http://127.0.0.1:{PORT}")
    print(f"[*] Network URL:  http://localhost:{PORT}")
    print(f"[*] Default Administrator: admin / Admin@2026!")
    print("=" * 70)
    print("[+] Production server ready. Serving requests...")
    
    serve(app, host=HOST, port=PORT, threads=THREADS)
