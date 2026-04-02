import pytest
import httpx
import time
import requests
from testcontainers.compose import DockerCompose
from pathlib import Path


@pytest.fixture(scope="module")
def docker_services():
    """Запуск всей системы через docker-compose.test.yml"""

    compose_path = Path(__file__).parent

    with DockerCompose(
        str(compose_path),
        compose_file_name="docker-compose.test.yml",
        pull=True,
    ):
        scrapper_url = "http://localhost:8001"

        for _ in range(30):
            try:
                r = requests.get(f"{scrapper_url}/docs")
                if r.status_code == 200:
                    break
            except Exception:
                time.sleep(1)

        yield {"scrapper_url": scrapper_url}


@pytest.mark.asyncio
async def test_register_chat(docker_services):
    scrapper_url = docker_services["scrapper_url"]

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{scrapper_url}/tg-chat/123")

        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_add_link(docker_services):
    scrapper_url = docker_services["scrapper_url"]

    async with httpx.AsyncClient() as client:
        await client.post(f"{scrapper_url}/tg-chat/123")

        r = await client.post(
            f"{scrapper_url}/links",
            json={"link": "https://github.com/user/repo", "tags": ["work"]},
            headers={"Tg-Chat-Id": "123"},
        )

        assert r.status_code in (200, 201)

        r2 = await client.get(
            f"{scrapper_url}/links/?page=0&limit=1",
            headers={"Tg-Chat-Id": "123"},
        )

        assert r2.status_code == 200
        data = r2.json()

        assert "links" in data
        assert len(data["links"]) >= 1


@pytest.mark.asyncio
async def test_delete_link(docker_services):
    scrapper_url = docker_services["scrapper_url"]

    url = "https://github.com/user/repo-to-delete"

    async with httpx.AsyncClient() as client:
        await client.post(f"{scrapper_url}/tg-chat/123")

        await client.post(
            f"{scrapper_url}/links",
            headers={"Tg-Chat-Id": "123"},
            json={"link": url, "tags": ["test"]},
        )

        r = await client.request(
            "DELETE",
            f"{scrapper_url}/links",
            headers={"Tg-Chat-Id": "123"},
            json={"link": url},
        )

        assert r.status_code == 200

        r2 = await client.get(
            f"{scrapper_url}/links/?page=0&limit=1",
            headers={"Tg-Chat-Id": "123"},
        )

        assert r2.status_code == 200
        assert url not in str(r2.json())
