"""Unit test for Vercel entrypoint (app.main).
"""

def test_vercel_index_import():
    """Verify app.main exports valid FastAPI app instance."""
    from app.main import app
    assert app is not None
    assert hasattr(app, "routes")
