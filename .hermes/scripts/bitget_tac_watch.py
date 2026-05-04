#!/usr/bin/env python3
import json
import os
import urllib.parse
import urllib.request
from statistics import mean

BASE = "https://api.bitget.com"
SYMBOL = "TACUSDT"
PRODUCT_TYPE = "USDT-FUTURES"


def get_json(path, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Hermes-TAC-Watch"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def to_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def get_spot_ticker():
    data = get_json("/api/v2/spot/market/tickers").get("data", [])
    for row in data:
        if row.get("symbol") == SYMBOL:
            return row
    raise RuntimeError("spot ticker not found")


def get_mix_ticker():
    data = get_json("/api/v2/mix/market/ticker", {"symbol": SYMBOL, "productType": PRODUCT_TYPE}).get("data", [])
    if isinstance(data, list) and data:
        return data[0]
    if isinstance(data, dict):
        return data
    raise RuntimeError("mix ticker not found")


def get_candles(granularity, limit=100):
    rows = get_json(
        "/api/v2/spot/market/candles",
        {"symbol": SYMBOL, "granularity": granularity, "limit": str(limit)},
    ).get("data", [])
    parsed = []
    for row in rows:
        try:
            parsed.append(
                {
                    "ts": int(row[0]),
                    "o": float(row[1]),
                    "h": float(row[2]),
                    "l": float(row[3]),
                    "c": float(row[4]),
                    "vol": float(row[5]),
                }
            )
        except Exception:
            pass
    parsed.sort(key=lambda x: x["ts"])
    return parsed


def summarize_bars(bars):
    closes = [x["c"] for x in bars]
    highs = [x["h"] for x in bars]
    lows = [x["l"] for x in bars]
    vols = [x["vol"] for x in bars]
    out = {
        "last": closes[-1],
        "high20": max(highs[-20:]) if len(highs) >= 20 else max(highs),
        "low20": min(lows[-20:]) if len(lows) >= 20 else min(lows),
        "avg_vol20": mean(vols[-20:]) if len(vols) >= 20 else mean(vols),
        "last_vol": vols[-1],
    }
    if len(closes) >= 5:
        out["chg5"] = (closes[-1] / closes[-5] - 1) * 100
    else:
        out["chg5"] = 0.0
    if len(closes) >= 20:
        out["chg20"] = (closes[-1] / closes[-20] - 1) * 100
    else:
        out["chg20"] = 0.0
    out["vol_ratio"] = out["last_vol"] / out["avg_vol20"] if out["avg_vol20"] else 0.0
    return out


def level_judgement(price, s15, s1h, spot, mix):
    day_high = to_float(spot.get("high24h"))
    day_low = to_float(spot.get("low24h"))
    spot_bid = to_float(spot.get("bidPr"))
    spot_ask = to_float(spot.get("askPr"))
    funding = to_float(mix.get("fundingRate"))

    breakout = s15["high20"]
    support_near = max(s15["low20"], s1h["low20"])
    day_break = day_high
    invalidation = min(s15["low20"], s1h["low20"])

    dist_breakout = (breakout / price - 1) * 100 if price else 0.0
    dist_support = (price / support_near - 1) * 100 if support_near else 0.0
    dist_day_high = (day_break / price - 1) * 100 if price else 0.0

    if price > breakout and s15["vol_ratio"] >= 1.2:
        state = "15m breakout confirmed"
    elif price >= breakout * 0.995:
        state = "near breakout"
    elif price > support_near and s15["chg5"] > 0:
        state = "range rebound"
    else:
        state = "weak / below momentum zone"

    risk = []
    if s15["vol_ratio"] < 0.7:
        risk.append("短線量能不足")
    if funding > 0.001:
        risk.append("合約資金費率偏高，追多成本上升")
    if (spot_ask - spot_bid) / price > 0.002:
        risk.append("買賣價差偏大")
    if price < support_near:
        risk.append("已跌回短線支撐下方")

    return {
        "state": state,
        "breakout_level": breakout,
        "day_high": day_break,
        "support_level": support_near,
        "invalidation_level": invalidation,
        "dist_to_breakout_pct": dist_breakout,
        "dist_to_day_high_pct": dist_day_high,
        "dist_above_support_pct": dist_support,
        "risks": risk,
        "funding_rate": funding,
        "day_low": day_low,
    }


def main():
    spot = get_spot_ticker()
    mix = get_mix_ticker()
    bars15 = get_candles("15min")
    bars1h = get_candles("1h")
    bars4h = get_candles("4h")

    s15 = summarize_bars(bars15)
    s1h = summarize_bars(bars1h)
    s4h = summarize_bars(bars4h)
    price = to_float(spot.get("lastPr"))
    judge = level_judgement(price, s15, s1h, spot, mix)

    out = {
        "symbol": SYMBOL,
        "spot_last": price,
        "mix_last": to_float(mix.get("lastPr")),
        "spot_24h_change_pct": to_float(spot.get("change24h")) * 100,
        "mix_24h_change_pct": to_float(mix.get("change24h")) * 100,
        "spot_usdt_volume_24h": to_float(spot.get("usdtVolume")),
        "mix_usdt_volume_24h": to_float(mix.get("usdtVolume")),
        "summary_15m": s15,
        "summary_1h": s1h,
        "summary_4h": s4h,
        "judgement": judge,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
