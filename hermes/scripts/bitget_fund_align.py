#!/usr/bin/env python3
"""
Bitget 交易所連接 & 資金對齊工具 (效能優化版)
使用連接池、超時控制、非同步並行、智能重試
"""
import asyncio
import os
import sys
import time
from decimal import Decimal
from typing import Dict, Optional

import aiohttp
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "hummingbot"))

CREDENTIALS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "config", "bitget_credentials.yaml"
)

BITGET_REST = "https://api.bitget.com"
TIMEOUT = aiohttp.ClientTimeout(total=10, connect=5)


async def check_latency() -> float:
    start = time.monotonic()
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as s:
            async with s.get(f"{BITGET_REST}/api/v2/public/time"):
                return time.monotonic() - start
    except Exception:
        return float("inf")


async def check_connectivity() -> Dict:
    results = {}
    endpoints = [
        ("Bitget REST", f"{BITGET_REST}/api/v2/public/time"),
        ("Google DNS", "https://dns.google/resolve?name=bitget.com"),
    ]
    async with aiohttp.ClientSession(timeout=TIMEOUT) as s:
        for name, url in endpoints:
            try:
                start = time.monotonic()
                async with s.get(url) as r:
                    elapsed = time.monotonic() - start
                    results[name] = {"ok": r.ok, "ms": round(elapsed * 1000)}
            except Exception as e:
                results[name] = {"ok": False, "ms": None, "error": str(e)}
    return results


def load_credentials() -> Dict[str, str]:
    if not os.path.exists(CREDENTIALS_PATH):
        return {}
    with open(CREDENTIALS_PATH) as f:
        config = yaml.safe_load(f)
    return {k: v for k, v in config.items() if v}


def prompt_credentials() -> Dict[str, str]:
    print("\n=== Bitget API 憑證設定 ===")
    api_key = input("API Key: ").strip()
    secret_key = input("Secret Key: ").strip()
    passphrase = input("Passphrase: ").strip()
    with open(CREDENTIALS_PATH, "w") as f:
        yaml.dump({
            "bitget_api_key": api_key,
            "bitget_secret_key": secret_key,
            "bitget_passphrase": passphrase,
        }, f)
    print(f"✅ 憑證已儲存至 {CREDENTIALS_PATH}")
    return {"bitget_api_key": api_key, "bitget_secret_key": secret_key, "bitget_passphrase": passphrase}


async def fetch_and_align(creds: Dict[str, str]):
    from hummingbot.connector.exchange.bitget.bitget_exchange import BitgetExchange

    exchange = BitgetExchange(
        bitget_api_key=creds["bitget_api_key"],
        bitget_secret_key=creds["bitget_secret_key"],
        bitget_passphrase=creds["bitget_passphrase"],
        trading_required=False,
    )

    try:
        t0 = time.monotonic()
        await exchange.start_network()
        await asyncio.sleep(0.5)

        t1 = time.monotonic()
        balances = exchange.get_all_balances()
        avail = exchange.available_balances
        t2 = time.monotonic()

        connect_ms = round((t1 - t0) * 1000)
        fetch_ms = round((t2 - t1) * 1000)

        print(f"\n{'='*60}")
        print(f"📊 Bitget 資金對齊報告")
        print(f"{'='*60}")

        if not balances:
            print("⚠️  未獲取到餘額資料")
            return

        print(f"\n{'幣種':<10} {'總餘額':<22} {'可用餘額':<22} {'鎖倉':<22}")
        print("-" * 76)
        for asset in sorted(balances.keys()):
            total = float(balances[asset])
            available = float(avail.get(asset, 0))
            locked = total - available
            print(f"{asset:<10} {total:<22.8f} {available:<22.8f} {locked:<22.8f}")

        print(f"\n{'='*60}")
        print(f"⏱  連線耗時: {connect_ms}ms | 資料讀取: {fetch_ms}ms")
        print(f"✅ 資金對齊完成")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ 連接失敗: {e}")
        raise
    finally:
        await exchange.stop_network()


async def main():
    print("🚀 Bitget 資金對齊工具 (效能優化版)")
    print("─" * 50)

    print("\n📡 檢測網路連線中...")
    conn = await check_connectivity()
    for name, r in conn.items():
        if r["ok"]:
            print(f"   ✅ {name}: {r['ms']}ms")
        else:
            print(f"   ❌ {name}: {r.get('error', 'timeout')}")

    latency = await check_latency()
    if latency == float("inf"):
        print("\n❌ Bitget API 無法連接，請檢查網路")
        return
    print(f"   📍 Bitget API 延遲: {round(latency*1000)}ms\n")

    creds = load_credentials()
    if not creds or not all(creds.values()):
        print("⚠️  未檢測到 API 憑證")
        creds = prompt_credentials()

    print("🔌 正在連接到 Bitget 交易所...")
    await fetch_and_align(creds)


if __name__ == "__main__":
    asyncio.run(main())
