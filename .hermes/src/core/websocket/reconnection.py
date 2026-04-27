# src/core/websocket/reconnection.py
import asyncio
import logging
from typing import Optional, Callable, Awaitable

logger = logging.getLogger(__name__)

class ReconnectionManager:
    """通用 WebSocket 重连管理器"""
    
    def __init__(
        self,
        connect_func: Callable[[], Awaitable],
        on_reconnect: Optional[Callable[[], Awaitable]] = None,
        max_retries: int = 0,          # 0 表示无限重连
        base_delay: float = 1.0,
        max_delay: float = 30.0
    ):
        self.connect_func = connect_func
        self.on_reconnect = on_reconnect
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self._retry_count = 0
        self._running = False
    
    async def run_with_reconnect(self):
        """主循环：运行连接并处理重连"""
        self._running = True
        while self._running:
            try:
                await self.connect_func()
                self._retry_count = 0  # 连接成功，重置计数
            except Exception as e:
                logger.error(f"Connection error: {e}")
                if not await self._should_retry():
                    break
                await self._wait_with_backoff()
                if self.on_reconnect:
                    await self.on_reconnect()
    
    async def _should_retry(self) -> bool:
        if not self._running:
            return False
        if self.max_retries > 0 and self._retry_count >= self.max_retries:
            logger.error(f"Max retries ({self.max_retries}) reached, giving up.")
            return False
        self._retry_count += 1
        return True
    
    async def _wait_with_backoff(self):
        """指数退避等待"""
        delay = min(self.base_delay * (2 ** (self._retry_count - 1)), self.max_delay)
        logger.info(f"Reconnecting in {delay:.1f}s (attempt {self._retry_count})")
        await asyncio.sleep(delay)
    
    def stop(self):
        self._running = False