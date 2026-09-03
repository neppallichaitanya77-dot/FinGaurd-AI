import pytest
from app.core.security import verify_password, hash_password, create_access_token, decode_access_token


def test_password_hashing():
    raw = "super_secure_pass_123"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_token_encode_decode():
    sub = "user-uuid-12345"
    token = create_access_token(sub)
    decoded = decode_access_token(token)
    assert decoded == sub


def test_jwt_invalid_token():
    assert decode_access_token("invalid.jwt.token") is None


def test_register_and_login_flow(client):
    register_payload = {
        "name": "Integration User",
        "email": "integration@finguard.ai",
        "password": "Password123!",
    }
    # Register
    res = client.post("/api/auth/register", json=register_payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == register_payload["email"]
    assert data["user"]["name"] == register_payload["name"]

    # Duplicate registration should fail
    dup_res = client.post("/api/auth/register", json=register_payload)
    assert dup_res.status_code == 409

    # Login
    login_res = client.post(
        "/api/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token

    # Check /me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == register_payload["email"]


def test_login_invalid_credentials(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@finguard.ai", "password": "wrongpassword"},
    )
    assert res.status_code == 401


def test_protected_route_unauthorized(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 401


def test_profile_update(client, auth_headers):
    update_data = {"name": "Updated Demo Name", "phone": "+91 9876543210"}
    res = client.put("/api/auth/profile", json=update_data, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Demo Name"
    assert res.json()["phone"] == "+91 9876543210"
