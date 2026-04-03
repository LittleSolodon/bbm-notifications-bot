import asyncio
import httpx
import os
from dotenv import load_dotenv
import json

load_dotenv()


class ApiClient():
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(2, pool=20),
            http2=True,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=30),
            transport=httpx.AsyncHTTPTransport(retries=2)
        )

    async def aclose(self) -> None:
        await self.client.aclose()

    async def get_batch(self, ids: list) -> list[dict]:
        hash = os.getenv("PLAYER_HASH")
        if not hash:
            raise 
        tasks = []
        url="https://analniy-demon.ru/market_api.php"
        for i in ids:
            params = {
            "platform": "tg",
            "rawData": hash,
            "url": f"https://stage-app52440787-c7d40ae3d108.pages.vk-apps.com/index.html#/item/{i}",
            "type": "getItemInfo",
            "uniqueItemId": i
            }
            tasks.append(self.client.get(url=url, params=params))
        batch = await asyncio.gather(*tasks, return_exceptions=True)
        j = []
        for res in batch:
            try:
                res.raise_for_status()
                resp = res.json()
                # print(resp)
                j.append({
                    "success": True,
                    "resp": resp})
            except Exception as e:
                j.append({
                    "success": False,
                    "resp": e
                })
        return j