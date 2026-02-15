import pytest


@pytest.mark.asyncio
class TestUserRegister:
    async def test_user_can_register_with_valid_data(self, client):
        response = await client.post(
            "/api/users/register",
            json={
                "email": "newuser@example.com",
                "password": "Test1234",
                "first_name": "New",
                "last_name": "User",
            },
        )

        assert response.status_code == 201

        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["first_name"] == "New"
        assert data["last_name"] == "User"
        assert data["is_active"] is True

        # sensitive fields should never be exposed
        assert "hashed_password" not in data

    async def test_duplicate_email_is_not_allowed(self, client, test_user):
        response = await client.post(
            "/api/users/register",
            json={
                "email": test_user.email,
                "password": "Test1234",
                "first_name": "Another",
                "last_name": "User",
            },
        )

        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    async def test_invalid_email_returns_validation_error(self, client):
        response = await client.post(
            "/api/users/register",
            json={
                "email": "invalid-email",
                "password": "Test1234",
                "first_name": "Test",
                "last_name": "User",
            },
        )

        assert response.status_code == 422

    async def test_weak_password_is_rejected(self, client):
        response = await client.post(
            "/api/users/register",
            json={
                "email": "weakpass@example.com",
                "password": "123",
                "first_name": "Test",
                "last_name": "User",
            },
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestUserLogin:
    async def test_user_can_login_with_valid_credentials(self, client, test_user):
        response = await client.post(
            "/api/users/login", json={"email": test_user.email, "password": "Test1234"}
        )

        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    async def test_login_fails_with_wrong_password(self, client, test_user):
        response = await client.post(
            "/api/users/login", json={"email": test_user.email, "password": "WrongPassword123"}
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

        response = await client.post(
            "/api/users/login", json={"email": "nonexistent@example.com", "password": "Test1234"}
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestUserProfile:
    async def test_user_can_get_own_profile(self, client, test_user):
        login_response = await client.post(
            "/api/users/login", json={"email": test_user.email, "password": "Test1234"}
        )
        token = login_response.json()["access_token"]

        response = await client.get(
            "/api/users/profile", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

        data = response.json()
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert "hashed_password" not in data

    async def test_profile_requires_authentication(self, client):
        response = await client.get("/api/users/profile")

        assert response.status_code == 401

    async def test_user_can_update_profile(self, client, test_user):
        login_response = await client.post(
            "/api/users/login", json={"email": test_user.email, "password": "Test1234"}
        )
        token = login_response.json()["access_token"]

        response = await client.patch(
            "/api/users/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Updated", "last_name": "Name"},
        )

        assert response.status_code == 200

        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["email"] == test_user.email

    async def test_user_can_partially_update_profile(self, client, test_user):
        login_response = await client.post(
            "/api/users/login", json={"email": test_user.email, "password": "Test1234"}
        )
        token = login_response.json()["access_token"]

        response = await client.patch(
            "/api/users/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "OnlyFirstName"},
        )

        assert response.status_code == 200

        data = response.json()
        assert data["first_name"] == "OnlyFirstName"
        assert data["last_name"] == test_user.last_name


@pytest.mark.asyncio
class TestRefreshToken:
    async def test_user_can_refresh_access_token(self, client, test_user):
        login_response = await client.post(
            "/api/users/login", json={"email": test_user.email, "password": "Test1234"}
        )
        refresh_token = login_response.json()["refresh_token"]

        response = await client.post("/api/users/refresh", json={"refresh_token": refresh_token})

        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_fails_with_invalid_token(self, client):
        response = await client.post(
            "/api/users/refresh", json={"refresh_token": "invalid_token_here"}
        )

        assert response.status_code == 401

    async def test_refresh_fails_with_access_token(self, client, test_user):
        login_response = await client.post(
            "/api/users/login", json={"email": test_user.email, "password": "Test1234"}
        )
        access_token = login_response.json()["access_token"]

        response = await client.post(
            "/api/users/refresh", json={"refresh_token": access_token}  # Wrong token type!
        )

        assert response.status_code == 401
