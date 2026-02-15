import pytest


@pytest.mark.asyncio
class TestItemCreate:
    async def test_user_can_create_item(self, client, auth_token):
        response = await client.post(
            "/api/items",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "iPhone 14",
                "description": "Apple smartphone",
                "category": "electronics",
            },
        )

        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "iPhone 14"
        assert data["description"] == "Apple smartphone"
        assert data["category"] == "electronics"
        assert data["status"] == "active"
        assert data["is_deleted"] is False
        assert "id" in data

    async def test_create_requires_authentication(self, client):
        response = await client.post(
            "/api/items", json={"name": "iPhone 14", "category": "electronics"}
        )

        assert response.status_code == 401

    async def test_create_with_short_name_fails(self, client, auth_token):
        response = await client.post(
            "/api/items",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "iP", "category": "electronics"},
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestItemGet:
    async def test_user_can_get_item(self, client, auth_token):
        create_response = await client.post(
            "/api/items",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Test iPhone",
                "description": "Test Description",
                "category": "electronics",
            },
        )

        # Debug
        print(f"Create status: {create_response.status_code}")
        print(f"Create response: {create_response.json()}")

        assert create_response.status_code == 201

        item_id = create_response.json()["id"]

        response = await client.get(
            f"/api/items/{item_id}", headers={"Authorization": f"Bearer {auth_token}"}
        )

        print(f"Get status: {response.status_code}")
        if response.status_code != 200:
            print(f"Get response: {response.json()}")

        assert response.status_code == 200

    async def test_get_nonexistent_item_returns_404(self, client, auth_token):
        response = await client.get(
            "/api/items/99999", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 404

        data = response.json()

        assert data["success"] is False
        assert "error" in data
        assert "code" in data["error"]
        assert "not found" in data["error"]["message"].lower()

    async def test_get_requires_authentication(self, client, auth_token):
        create_response = await client.post(
            "/api/items",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "Test Item", "category": "electronics"},
        )
        item_id = create_response.json()["id"]

        response = await client.get(f"/api/items/{item_id}")

        assert response.status_code == 401


@pytest.mark.asyncio
class TestItemList:
    async def test_user_can_list_items(self, client, auth_token):
        for i in range(3):
            await client.post(
                "/api/items",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"name": f"Item {i+1}", "category": "electronics"},
            )

        response = await client.get("/api/items", headers={"Authorization": f"Bearer {auth_token}"})

        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert data["total"] >= 3
        assert len(data["items"]) >= 3

    async def test_pagination_works(self, client, auth_token):
        for i in range(8):
            await client.post(
                "/api/items",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"name": f"Item {i+1}", "category": "electronics"},
            )
        response1 = await client.get(
            "/api/items?page=1&per_page=5", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["items"]) == 5
        assert data1["page"] == 1
        assert data1["total"] >= 8

        response2 = await client.get(
            "/api/items?page=2&per_page=5", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["items"]) >= 3
        assert data2["page"] == 2

    async def test_filter_by_category_works(self, client, auth_token):
        await client.post(
            "/api/items",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "iPhone", "category": "electronics"},
        )
        await client.post(
            "/api/items",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "T-Shirt", "category": "clothing"},
        )

        response = await client.get(
            "/api/items?category=electronics", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        for item in data["items"]:
            assert item["category"] == "electronics"


@pytest.mark.asyncio
class TestItemUpdate:
    async def test_user_can_update_item(self, client, auth_token):
        create_response = await client.post(
            "/api/items",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "Old Name", "description": "Old Description", "category": "electronics"},
        )
        item_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/items/{item_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "New Name", "description": "New Description"},
        )

        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "New Description"
        assert data["category"] == "electronics"

    async def test_update_nonexistent_item_returns_404(self, client, auth_token):
        response = await client.patch(
            "/api/items/99999",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "Updated"},
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestItemDelete:
    async def test_user_can_delete_item(self, client, auth_token):
        create_response = await client.post(
            "/api/items",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "To Delete", "category": "electronics"},
        )
        item_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/items/{item_id}", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 204
        get_response = await client.get(
            f"/api/items/{item_id}", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert get_response.status_code == 404

    async def test_delete_nonexistent_item_returns_404(self, client, auth_token):
        response = await client.delete(
            "/api/items/99999", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestCategoryAnalytics:
    async def test_category_density_calculation(self, client, auth_token):
        items = [
            {"name": "Item 1", "category": "electronics"},
            {"name": "Item 2", "category": "electronics"},
            {"name": "Item 3", "category": "clothing"},
        ]

        for item in items:
            await client.post(
                "/api/items", headers={"Authorization": f"Bearer {auth_token}"}, json=item
            )

        response = await client.get(
            "/api/items/analytics/category-density",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200

        data = response.json()
        assert data["total_items"] >= 3
        assert len(data["categories"]) >= 2

        electronics = next((c for c in data["categories"] if c["category"] == "electronics"), None)
        assert electronics is not None
        assert electronics["count"] >= 2

    async def test_analytics_with_no_items(self, client, auth_token):
        response = await client.get(
            "/api/items/analytics/category-density",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200

        data = response.json()
        assert data["total_items"] == 0
        assert data["categories"] == []
