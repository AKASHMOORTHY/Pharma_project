# tests/test_user.py
import uuid
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from user_management.app.main import app



client = TestClient(app)

def test_login_success():
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@example.com", "password": "Admin@123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.fixture
def get_token():
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@example.com", "password": "Admin@123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]


def test_profile_access(get_token):
    response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"


def test_create_user(get_token):
    user_data = {
        "email": f"testuser_{uuid.uuid4().hex[:6]}@example.com",  # dynamic unique email
        "full_name": "Test User 1",
        "password": "Test@123",
        "role_id": 2,
        "shift": "A"
    }
    response = client.post(
        "/api/auth/users/",
        headers={"Authorization": f"Bearer {get_token}"},
        json=user_data
    )
    assert response.status_code == 200

def test_shift_access_denied(get_token):
    response = client.post(
        "/api/auth/some-data-entry",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"test_time": "16:00"}  # Should fail for Shift A
    )
    assert response.status_code == 403

