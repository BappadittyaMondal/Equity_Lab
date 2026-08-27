"""Unit test for legacy Vercel entrypoint (api_legacy/index.py).
"""

def test_vercel_index_import():
    """Verify api_legacy/index.py exports valid FastAPI app instance."""
    from api_legacy.index import app
    assert app is not None
    assert hasattr(app, "routes")
