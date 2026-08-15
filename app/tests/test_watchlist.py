"""Unit tests for Watchlist API endpoints.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_watchlist_crud_flow():
    # 1. Clear/check initial watchlist
    response = client.get("/api/v1/watchlist")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data

    # 2. Add ticker to watchlist
    add_payload = {
        "symbol": "TCS",
        "company_name": "Tata Consultancy Services",
        "target_price": 4500.0,
        "notes": "Quality IT giant with strong free cash flows"
    }
    post_res = client.post("/api/v1/watchlist", json=add_payload)
    assert post_res.status_code == 200
    added = post_res.json()
    assert added["symbol"] == "TCS.NS"
    assert added["company_name"] == "Tata Consultancy Services"
    assert added["target_price"] == 4500.0

    # 3. Get watchlist and verify TCS exists
    get_res = client.get("/api/v1/watchlist")
    assert get_res.status_code == 200
    items = get_res.json()["items"]
    found = any(item["symbol"] == "TCS.NS" for item in items)
    assert found is True

    # 4. Delete ticker from watchlist
    del_res = client.delete("/api/v1/watchlist/TCS")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "SUCCESS"

    # 5. Verify removal
    get_res2 = client.get("/api/v1/watchlist")
    assert get_res2.status_code == 200
    items2 = get_res2.json()["items"]
    found2 = any(item["symbol"] == "TCS.NS" for item in items2)
    assert found2 is False
