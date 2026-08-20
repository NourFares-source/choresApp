import pytest

@pytest.mark.asyncio
async def test_create_parent_user(client):
    """Test user registration endpoint."""
    payload = {
        "username": "newparent",
        "email": "newparent@example.com",
        "fullName": "New Parent",
        "password": "strongpassword123"
    }
    response = await client.post("/auth/register/parent", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_protected_route_without_token(client):
    """Ensure unauthenticated users are blocked."""
    response = await client.get("/chores/my-chores")
    print("\nDEBUG RESPONSE:", response.status_code, response.json())
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_route_with_token(auth_child_client):
    response = await auth_child_client.get("/chores/my-chores")
    print("\nDEBUG RESPONSE:", response.status_code, response.json())
    assert response.status_code == 200