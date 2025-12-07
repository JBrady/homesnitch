def test_register_login_flow(client):
    # Register
    reg_resp = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "strongpassword"
    })
    assert reg_resp.status_code == 201

    # Login
    login_resp = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "strongpassword"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.headers.get("Set-Cookie", "")

    # Access Protected Route
    # We need to extract the cookies from the login response to reuse them
    # Flask test client handles cookies automatically in the cookie jar

    report_resp = client.get("/report")
    assert report_resp.status_code == 200 # Should be empty list initially

def test_login_invalid_credentials(client):
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "strongpassword"
    })

    resp = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert resp.status_code == 401

def test_logout(client):
    # Register & Login
    client.post("/auth/register", json={"email": "test@example.com", "password": "pass"})
    client.post("/auth/login", json={"email": "test@example.com", "password": "pass"})

    # Logout
    resp = client.post("/auth/logout")
    assert resp.status_code == 200
    assert "access_token=;" in resp.headers.get("Set-Cookie", "")
