import asyncio
import hmac
import hashlib
import time
import aiohttp
from abc import ABC, abstractmethod

class BaseClient(ABC):
    def __init__(self, api_key, secret, passphrase=None):
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        self.session = None

    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    @abstractmethod
    def _generate_signature(self, method, path, params):
        pass

    async def request(self, method, path, params=None, data=None):
        await self._ensure_session()
        # 自動重試機制 (Exponential Backoff)
        for attempt in range(3):
            try:
                headers = self._get_headers(method, path, params or data)
                async with self.session.request(method, path, params=params, json=data, headers=headers) as resp:
                    if resp.status == 429: # 觸發頻率限制
                        wait = 2 ** attempt
                        print(f"⚠️ Rate limited, waiting {wait}s...")
                        await asyncio.sleep(wait)
                        continue
                    return await resp.json()
            except Exception as e:
                if attempt == 2: raise e
                await asyncio.sleep(1)
