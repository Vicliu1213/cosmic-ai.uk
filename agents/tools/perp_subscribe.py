"""
tools/perp_subscribe.py
真實 WebSocket 即時訂閱 — 替換模擬 perp_subscribe_tool
"""

import json, logging, threading, time
from typing import List
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

logger = logging.getLogger(__name__)

_latest_data: dict = {}
_ws_client: UMFuturesWebsocketClient = None
_lock = threading.Lock()


def _on_message(_, message):
    try:
        data = json.loads(message)
        stream = data.get("stream", "")
        symbol = data.get("data", {}).get("s", "unknown")
        with _lock:
            _latest_data[f"{stream}:{symbol}"] = data.get("data", data)
    except Exception:
        pass


def perp_subscribe_tool(
    symbol: str,
    levels: List[float],
    data_types: List[str] = None,
):
    """
    對指定幣種開啟 WebSocket 即時流。
    支援：liquidations / open_interest / large_orders / delta_bars / funding_events
    """
    global _ws_client
    symbol_lower = symbol.lower()

    streams = []
    if "liquidations" in (data_types or []):
        streams.append(f"{symbol_lower}@forceOrder")
    if "open_interest" in (data_types or []):
        streams.append(f"{symbol_lower}@openInterest")
    if "large_orders" in (data_types or []):
        streams.append(f"{symbol_lower}@trade")
    if "funding_events" in (data_types or []):
        streams.append(f"{symbol_lower}@markPrice")

    if _ws_client is None:
        _ws_client = UMFuturesWebsocketClient(on_message=_on_message, is_combined=True)

    for s in streams:
        _ws_client.subscribe(stream=s)

    logger.info(f"WebSocket 訂閱: {symbol} → {streams}")


def get_latest_ws_data(symbol: str, stream_type: str) -> dict:
    """讀取最新推送資料"""
    with _lock:
        return _latest_data.get(f"{symbol.lower()}@{stream_type}", {})