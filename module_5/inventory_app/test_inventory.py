from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_inward_entry():
    response = client.post("/api/inventory/inward/", json={
        "material_id": 2,
        "batch_code": "BATCH002",
        "quantity": 100,
        "uom": "KG",
        "location": "Store A",
        "status": "AVAILABLE",
        "expiry_date": "2025-12-31"
    })
    assert response.status_code == 200
    assert response.json()["batch_code"] == "BATCH002"

def test_get_by_batch_code():
    response = client.get("/api/inventory/BATCH002")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_fifo_consumption():
    response = client.post("/api/inventory/consumption/?material_id=2&quantity=20")
    assert response.status_code == 200
    assert "batches_used" in response.json()

def test_stock_adjustment():
    # Assuming item_id=1 exists
    response = client.post("/api/inventory/adjust/", json={
        "item_id": 1,
        "adjustment_type": "increase",
        "quantity": 10,
        "reason": "Correction after audit"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Stock adjusted successfully"

print("All tests passed!")
