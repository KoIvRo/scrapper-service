import asyncio
import httpx

async def main() -> None:
    """Заполнение тестовых данных"""

    count_users = 1000
    links_per_user = 100

    async with httpx.AsyncClient() as client:
        for user in range(count_users):

            await client.post(f"http://localhost:8001/tg-chat/{user}")

            for link in range(links_per_user):
                await client.post(
                    "http://localhost:8001/links",
                    json={
                        "link": f"https://github.com/user{user}/repo{link}",
                        "tags": ["load-test"]
                    },
                    headers={"Tg-Chat-Id": str(user)}
                )


if __name__ == "__main__":
    asyncio.run(main())
