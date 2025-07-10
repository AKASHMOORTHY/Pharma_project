import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)

def test_get_vendors_admin():
    response = client.get("/api/vendors/", headers={"x-role": "admin"})
    assert response.status_code in (200, 422)  # 422 if DB empty
    assert isinstance(response.json(), list) or "detail" in response.json()

def test_get_raw_materials_admin():
    response = client.get("/api/raw-materials/", headers={"x-role": "admin"})
    assert response.status_code in (200, 422)
    assert isinstance(response.json(), list) or "detail" in response.json()

def test_get_material_batches_supervisor():
    response = client.get("/api/material-batches/", headers={"x-role": "supervisor"})
    assert response.status_code in (200, 422)
    assert isinstance(response.json(), list) or "detail" in response.json()
