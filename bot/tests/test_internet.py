# import requests


# class TestInternetConnection:
#     """Класс тестировщик соединения с интернетом."""

#     def test_internet_connection(self) -> None:
#         """Доступен ли интернет."""

#         assert requests.get("https://example.com").status_code == 200

#     def test_telegram_connection(self) -> None:
#         """Доступен ли телеграмм"""
#         assert requests.get("https://telegram.org/", timeout=10).status_code == 200
