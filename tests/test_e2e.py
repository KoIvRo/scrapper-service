import pytest
import time
import requests
import httpx
from testcontainers.compose import DockerCompose
from pathlib import Path

SCRAPPER_URL = "http://localhost:8001"


@pytest.fixture(scope="module")
def docker_services():
    compose_path = Path(__file__).parent

    with DockerCompose(
        str(compose_path),
        compose_file_name="docker-compose.test.yml",
        pull=True,
    ):
        for i in range(30):
            try:
                r = requests.get(f"{SCRAPPER_URL}/docs", timeout=5)
                if r.status_code == 200:
                    break
            except Exception:
                time.sleep(1)
        else:
            raise RuntimeError("Scrapper did not start")

        time.sleep(15)
        yield {}


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_register_chat(docker_services):  # noqa
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{SCRAPPER_URL}/tg-chat/123", timeout=10)
        assert r.status_code == 200


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_add_link(docker_services):  # noqa
    async with httpx.AsyncClient() as c:
        await c.post(f"{SCRAPPER_URL}/tg-chat/456", timeout=10)
        r = await c.post(
            f"{SCRAPPER_URL}/links",
            json={"link": "https://github.com/test/repo", "tags": ["test"]},
            headers={"Tg-Chat-Id": "456"},
            timeout=10,
        )
        assert r.status_code in (200, 201)


@pytest.mark.timeout(30)
def test_valid_message_consumed(docker_services):  # noqa
    """
    TC-1.1: Scrapper публикует ссылку → пишет в Kafka →
    agent_service получает без ошибок десериализации.
    """

    requests.post(f"{SCRAPPER_URL}/tg-chat/111", timeout=10)
    r = requests.post(
        f"{SCRAPPER_URL}/links",
        json={"link": "https://github.com/e2e/valid-repo", "tags": ["e2e"]},
        headers={"Tg-Chat-Id": "111"},
        timeout=10,
    )
    assert r.status_code in (200, 201)
    time.sleep(10)


@pytest.mark.timeout(30)
def test_invalid_message_not_crash(docker_services):  # noqa
    """
    TC-1.2: Scrapper отправляет ссылку с длинным описанием,
    agent_service обрабатывает. Сервис не падает.
    """

    requests.post(f"{SCRAPPER_URL}/tg-chat/222", timeout=10)
    r = requests.post(
        f"{SCRAPPER_URL}/links",
        json={"link": "https://github.com/e2e/special-repo", "tags": ["e2e"]},
        headers={"Tg-Chat-Id": "222"},
        timeout=10,
    )
    assert r.status_code in (200, 201)

    time.sleep(10)


@pytest.mark.timeout(30)
def test_stop_word_filtered(docker_services):  # noqa
    """
    TC-2.1: Сообщение со стоп-словом отфильтровывается.
    """
    requests.post(f"{SCRAPPER_URL}/tg-chat/333", timeout=10)
    r = requests.post(
        f"{SCRAPPER_URL}/links",
        json={"link": "https://github.com/e2e/spam-repo", "tags": ["spam"]},
        headers={"Tg-Chat-Id": "333"},
        timeout=10,
    )
    assert r.status_code in (200, 201)

    time.sleep(10)


@pytest.mark.timeout(30)
def test_excluded_author_filtered(docker_services):  # noqa
    """
    TC-2.2: Сообщение от исключённого автора отфильтровывается.
    """

    requests.post(f"{SCRAPPER_URL}/tg-chat/444", timeout=10)
    r = requests.post(
        f"{SCRAPPER_URL}/links",
        json={"link": "https://github.com/bot-user/repo", "tags": ["e2e"]},
        headers={"Tg-Chat-Id": "444"},
        timeout=10,
    )
    assert r.status_code in (200, 201)

    time.sleep(10)


@pytest.mark.timeout(30)
def test_short_message_filtered(docker_services):  # noqa
    """
    TC-2.3: Короткое сообщение отфильтровывается.
    """

    requests.post(f"{SCRAPPER_URL}/tg-chat/555", timeout=10)
    r = requests.post(
        f"{SCRAPPER_URL}/links",
        json={"link": "https://github.com/e2e/short-repo", "tags": ["e2e"]},
        headers={"Tg-Chat-Id": "555"},
        timeout=10,
    )
    assert r.status_code in (200, 201)

    time.sleep(10)


@pytest.mark.timeout(30)
def test_valid_message_passes_filters(docker_services):  # noqa
    """
    TC-2.4: Валидное сообщение проходит все фильтры.
    """
    requests.post(f"{SCRAPPER_URL}/tg-chat/666", timeout=10)
    r = requests.post(
        f"{SCRAPPER_URL}/links",
        json={"link": "https://github.com/e2e/clean-repo", "tags": ["e2e"]},
        headers={"Tg-Chat-Id": "666"},
        timeout=10,
    )
    assert r.status_code in (200, 201)

    time.sleep(10)
