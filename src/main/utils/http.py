import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, max=2))
async def fetch(client: httpx.AsyncClient, url: str):
    r = await client.get(url, timeout=httpx.Timeout(2.0, connect=1.0))
    r.raise_for_status()
    return r.json()

