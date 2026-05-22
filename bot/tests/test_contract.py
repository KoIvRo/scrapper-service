class TestBotAPIContract:
    """Тесты контракта API."""

    def test_updates_invalid_request_returns_400(self, client):
        response = client.post("/updates", json={"invalid": "data"})
        assert response.status_code == 422

    def test_updates_invalid_url_returns_400(self, client):
        data = {
            "id": 1,
            "url": "not-a-url",
            "description": "Test",
            "tgChatIds": [123],
            "author": "test-user",
        }
        response = client.post("/updates", json=data)
        assert response.status_code == 422

    def test_updates_missing_id_returns_400(self, client):
        data = {
            "url": "https://github.com/user/repo",
            "description": "Test",
            "author": "test-user",
            "tgChatIds": [123],
        }
        response = client.post("/updates", json=data)
        assert response.status_code == 422

    def test_updates_missing_url_returns_400(self, client):
        data = {
            "id": 1,
            "description": "Test",
            "tgChatIds": [123],
            "author": "test-user",
        }
        response = client.post("/updates", json=data)
        assert response.status_code == 422
