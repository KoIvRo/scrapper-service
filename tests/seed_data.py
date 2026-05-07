import asyncio
import httpx


async def fill_user(client: httpx.AsyncClient, user: int, links_per_user: int, sem: asyncio.Semaphore):
    async with sem:
        await client.post(f"http://localhost:8001/tg-chat/{user}")

        for link in range(1, links_per_user + 1):
            await client.post(
                "http://localhost:8001/links",
                json={
                    "link": f"https://github.com/user{user}/repo{link}",
                    "tags": ["load-test"],
                },
                headers={"Tg-Chat-Id": str(user)},
            )


async def main():
    count_users = 1000
    links_per_user = 100
    concurrency = 20
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [
            fill_user(client, user, links_per_user, sem)
            for user in range(1, count_users + 1)
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
