"""Unit test for Vercel Serverless Function entrypoint (api/index.py).
"""

def test_vercel_index_import():
    """Verify api/index.py exports valid FastAPI app instance."""
    from api.index import app
    assert app is not None
    assert hasattr(app, "routes")
