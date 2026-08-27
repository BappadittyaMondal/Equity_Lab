# DEPRECATED: Legacy Vercel serverless Python handler. Production topology runs backend standalone on Render (https://equity-lab-c90s.onrender.com).
import os
import sys
import tempfile
import shutil

# Ensure project root is on Python module path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Vercel serverless filesystem at /var/task is read-only.
# Move SQLite database file to /tmp for write compatibility.
tmp_dir = tempfile.gettempdir()
tmp_db_path = os.path.join(tmp_dir, "equity_lab.db")

source_db = os.path.join(root_dir, "data", "ierl_equity.sqlite3")
if not os.path.exists(source_db):
    source_db = os.path.join(root_dir, "equity_lab.db")

if os.path.exists(source_db) and not os.path.exists(tmp_db_path):
    try:
        shutil.copy2(source_db, tmp_db_path)
    except Exception:
        pass

if os.path.exists(tmp_db_path):
    os.environ["DATA_STORE_PATH"] = tmp_db_path

# Fix CORS origin for Vercel production deployment
allowed_origin = os.getenv("ALLOWED_ORIGIN", "")
vercel_url = os.getenv("VERCEL_URL", "")

if vercel_url and (not allowed_origin or "*" in allowed_origin):
    os.environ["ALLOWED_ORIGIN"] = f"https://{vercel_url}"
# Allow Vercel serverless environment fallback mode without hard startup abort
os.environ["STRICT_VERCEL_POSTGRES_GATE"] = "0"

from app.main import app

# Export FastAPI app instance for Vercel Serverless Function Handler
app = app
