from unittest.mock import AsyncMock, patch

from dependencies.service_factory import ServiceFactory
from exceptions import UnknownChatError, ExistLink, InvalidURL


HEADERS = {"Tg-Chat-Id": "123"}


class TestScrapperAPIContract:
    def _payload(self, valid_github_link):
        return {
            "link": valid_github_link["url"],
            "tags": valid_github_link.get("tags", []),
            "filters": [],
        }

    def test_delete_from_nonexistent_chat(self, client, valid_github_link):
        mock_service = AsyncMock()
        mock_service.delete_link = AsyncMock(side_effect=UnknownChatError(999))

        with patch.object(ServiceFactory, "get_service", return_value=mock_service):
            resp = client.request(
                "DELETE",
                "/links",
                json={"link": valid_github_link["url"]},
                headers=HEADERS,
            )
            assert resp.status_code in (400, 404)

    def test_delete_nonexistent_chat(self, client):
        mock_service = AsyncMock()
        mock_service.delete_chat = AsyncMock(side_effect=UnknownChatError(999))

        with patch.object(ServiceFactory, "get_service", return_value=mock_service):
            resp = client.delete("/chats/999", headers=HEADERS)
            assert resp.status_code in (400, 404)

    def test_add_link_invalid_url(self, client):
        mock_service = AsyncMock()
        mock_service.append_link = AsyncMock(side_effect=InvalidURL("bad"))

        with patch.object(ServiceFactory, "get_service", return_value=mock_service):
            resp = client.post(
                "/links",
                json={"link": "bad-url", "tags": [], "filters": []},
                headers=HEADERS,
            )
            assert resp.status_code in (400, 422)

    def test_add_link_duplicate(self, client, valid_github_link):
        mock_service = AsyncMock()
        mock_service.append_link = AsyncMock(side_effect=ExistLink("dup"))

        with patch.object(ServiceFactory, "get_service", return_value=mock_service):
            resp = client.post(
                "/links", json=self._payload(valid_github_link), headers=HEADERS
            )
            assert resp.status_code in (400, 409)
