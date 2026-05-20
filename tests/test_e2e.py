import pytest
import httpx
import time
import requests
from testcontainers.compose import DockerCompose
from pathlib import Path


@pytest.fixture(scope="module")
def docker_services():
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
        else:
            raise RuntimeError("Scrapper did not start")

        time.sleep(15)

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
            f"{scrapper_url}/links/?page=0&limit=10",
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
            f"{scrapper_url}/links/?page=0&limit=10",
            headers={"Tg-Chat-Id": "123"},
        )
        assert r2.status_code == 200
        assert url not in str(r2.json())


@pytest.mark.asyncio
async def test_multiple_links(docker_services):
    scrapper_url = docker_services["scrapper_url"]
    links = [
        "https://github.com/user/repo1",
        "https://github.com/user/repo2",
        "https://github.com/user/repo3",
    ]

    async with httpx.AsyncClient() as client:
        await client.post(f"{scrapper_url}/tg-chat/123")

        for link in links:
            await client.post(
                f"{scrapper_url}/links",
                headers={"Tg-Chat-Id": "123"},
                json={"link": link, "tags": ["multi"]},
            )

        r = await client.get(
            f"{scrapper_url}/links/?page=0&limit=10",
            headers={"Tg-Chat-Id": "123"},
        )
        assert r.status_code == 200
        data = r.json()
        for link in links:
            assert link in str(data)


@pytest.mark.asyncio
async def test_invalid_url_rejected(docker_services):
    scrapper_url = docker_services["scrapper_url"]

    async with httpx.AsyncClient() as client:
        await client.post(f"{scrapper_url}/tg-chat/123")

        r = await client.post(
            f"{scrapper_url}/links",
            headers={"Tg-Chat-Id": "123"},
            json={"link": "not-a-url", "tags": ["fail"]},
        )
        assert r.status_code == 422


@pytest.mark.asyncio
async def test_empty_links_list(docker_services):
    scrapper_url = docker_services["scrapper_url"]

    async with httpx.AsyncClient() as client:
        await client.post(f"{scrapper_url}/tg-chat/999")

        r = await client.get(
            f"{scrapper_url}/links/?page=0&limit=10",
            headers={"Tg-Chat-Id": "999"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "links" in data
        assert len(data["links"]) == 0


@pytest.mark.asyncio
async def test_cache_hit(docker_services):
    """Проверка что данные кэшируются."""
    scrapper_url = docker_services["scrapper_url"]

    async with httpx.AsyncClient() as client:
        await client.post(f"{scrapper_url}/tg-chat/111")

        await client.post(
            f"{scrapper_url}/links",
            headers={"Tg-Chat-Id": "111"},
            json={"link": "https://github.com/cache/test", "tags": ["cache"]},
        )

        r1 = await client.get(
            f"{scrapper_url}/links/?page=0&limit=5",
            headers={"Tg-Chat-Id": "111"},
        )
        assert r1.status_code == 200

        r2 = await client.get(
            f"{scrapper_url}/links/?page=0&limit=5",
            headers={"Tg-Chat-Id": "111"},
        )
        assert r2.status_code == 200
        assert r1.json() == r2.json()


@pytest.mark.asyncio
async def test_cache_invalidation_on_add(docker_services):
    """Проверка что кэш сбрасывается при добавлении ссылки."""
    scrapper_url = docker_services["scrapper_url"]

    async with httpx.AsyncClient() as client:
        await client.post(f"{scrapper_url}/tg-chat/222")

        r1 = await client.get(
            f"{scrapper_url}/links/?page=0&limit=5",
            headers={"Tg-Chat-Id": "222"},
        )
        assert r1.status_code == 200
        len_before = len(r1.json()["links"])

        await client.post(
            f"{scrapper_url}/links",
            headers={"Tg-Chat-Id": "222"},
            json={"link": "https://github.com/cache/inv-test", "tags": ["test"]},
        )
        r2 = await client.get(
            f"{scrapper_url}/links/?page=0&limit=5",
            headers={"Tg-Chat-Id": "222"},
        )
        assert r2.status_code == 200
        assert len(r2.json()["links"]) == len_before + 1


@pytest.mark.asyncio
async def test_cache_invalidation_on_delete(docker_services):
    """Проверка что кэш сбрасывается при удалении ссылки."""
    scrapper_url = docker_services["scrapper_url"]
    url = "https://github.com/cache/to-delete"

    async with httpx.AsyncClient() as client:
        await client.post(f"{scrapper_url}/tg-chat/333")
        await client.post(
            f"{scrapper_url}/links",
            headers={"Tg-Chat-Id": "333"},
            json={"link": url, "tags": ["test"]},
        )

        r1 = await client.get(
            f"{scrapper_url}/links/?page=0&limit=5",
            headers={"Tg-Chat-Id": "333"},
        )
        len_before = len(r1.json()["links"])

        await client.request(
            "DELETE",
            f"{scrapper_url}/links",
            headers={"Tg-Chat-Id": "333"},
            json={"link": url},
        )

        r2 = await client.get(
            f"{scrapper_url}/links/?page=0&limit=5",
            headers={"Tg-Chat-Id": "333"},
        )
        assert len(r2.json()["links"]) == len_before - 1


@pytest.mark.asyncio
async def test_rate_limit_exceeded_returns_429(docker_services):
    """При превышении лимита возвращается HTTP 429."""
    scrapper_url = docker_services["scrapper_url"]

    async with httpx.AsyncClient() as client:
        await client.post(f"{scrapper_url}/tg-chat/123")
        for _ in range(10):
            r = await client.post(
                f"{scrapper_url}/links",
                headers={"Tg-Chat-Id": "123"},
                json={"link": "https://github.com/user/repo", "tags": ["rl"]},
            )

        r = await client.post(
            f"{scrapper_url}/links",
            headers={"Tg-Chat-Id": "123"},
            json={"link": "https://github.com/user/repo", "tags": ["rl"]},
        )
        assert r.status_code == 429
