from fastapi.testclient import TestClient  # noqa


class TestBotAPI:
    """Тесты для API бота."""

    def test_send_update_invalid_url(self, client, mock_bot):
        """Тест с невалидным URL."""

        invalid_data = {
            "id": 1,
            "url": "not-a-url",
            "description": "Test",
            "tgChatIds": [123],
        }

        response = client.post("/updates", json=invalid_data)

        assert response.status_code == 422
        mock_bot.return_value.send_message.assert_not_called()

    def test_send_update_missing_field(self, client, mock_bot):
        """Тест с отсутствующим полем."""

        invalid_data = {
            "id": 1,
            "url": "https://github.com/user/repo",
            "tgChatIds": [123],
        }

        response = client.post("/updates", json=invalid_data)

        assert response.status_code == 422
        mock_bot.return_value.send_message.assert_not_called()

    def test_send_update_invalid_id_type(self, client, mock_bot):
        """Тест с неверным типом id."""

        invalid_data = {
            "id": "not-an-int",
            "url": "https://github.com/user/repo",
            "description": "Test",
            "tgChatIds": [123],
        }

        response = client.post("/updates", json=invalid_data)

        assert response.status_code == 422
        mock_bot.return_value.send_message.assert_not_called()

    def test_send_update_invalid_chat_ids_type(self, client, mock_bot):
        """Тест с неверным типом tgChatIds."""

        invalid_data = {
            "id": 1,
            "url": "https://github.com/user/repo",
            "description": "Test",
            "tgChatIds": "not-a-list",
        }

        response = client.post("/updates", json=invalid_data)

        assert response.status_code == 422
        mock_bot.return_value.send_message.assert_not_called()
