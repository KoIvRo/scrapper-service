class TestBotAPI:
    """Тесты для API бота."""

    def test_send_update_success(self, client, valid_update_data, mock_bot):
        """Тест успешной отправки уведомления."""

        response = client.post("/updates", json=valid_update_data)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        bot_instance = mock_bot.return_value
        assert bot_instance.send_message.call_count == 2
        calls = bot_instance.send_message.call_args_list
        assert calls[0][1]["chat_id"] == 123
        assert calls[0][1]["text"] == "Test update"
        assert calls[1][1]["chat_id"] == 456

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

    def test_send_update_empty_chat_ids(self, client, valid_update_data, mock_bot):
        """Тест с пустым списком chat_ids."""

        data = valid_update_data.copy()
        data["tgChatIds"] = []

        response = client.post("/updates", json=data)

        assert response.status_code == 200
        mock_bot.return_value.send_message.assert_not_called()
