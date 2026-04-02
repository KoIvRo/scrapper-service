class TestBotAPIContract:
    """Контрактные тесты Bot API согласно OpenAPI спецификации."""

    def test_updates_valid_request_returns_200(self, client, mock_bot):
        """
        Тест 1: Корректный запрос к сервису Бота
        POST /updates с валидным телом должен вернуть 200 OK
        """
        payload = {
            "id": 123,
            "url": "https://github.com/user/repo",
            "description": "Обнаружены изменения в репозитории",
            "tgChatIds": [12345, 67890],
        }

        response = client.post("/updates", json=payload)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        bot_instance = mock_bot.return_value
        assert bot_instance.send_message.call_count == 2

    def test_updates_invalid_request_returns_400(self, client, mock_bot):
        """
        Тест 2: Некорректный запрос к сервису Бота
        POST /updates с невалидным телом должен вернуть 400 Bad Request
        """
        payload = {
            "id": 123,
            "url": "https://github.com/user/repo",
            "description": "Обнаружены изменения",
            # нет tgChatIds
        }

        response = client.post("/updates", json=payload)

        assert response.status_code == 422

    def test_updates_invalid_url_returns_400(self, client):
        """Тест 2: Некорректный URL в запросе"""
        payload = {
            "id": 123,
            "url": "not-a-valid-url",
            "description": "Обнаружены изменения",
            "tgChatIds": [12345],
        }

        response = client.post("/updates", json=payload)

        assert response.status_code == 422

    def test_updates_missing_id_returns_400(self, client):
        """Тест 2: Отсутствует обязательное поле id"""
        payload = {
            "url": "https://github.com/user/repo",
            "description": "Обнаружены изменения",
            "tgChatIds": [12345],
        }

        response = client.post("/updates", json=payload)

        assert response.status_code == 422

    def test_updates_missing_url_returns_400(self, client):
        """Тест 2: Отсутствует обязательное поле url"""
        payload = {
            "id": 123,
            "description": "Обнаружены изменения",
            "tgChatIds": [12345],
        }

        response = client.post("/updates", json=payload)

        assert response.status_code == 422
