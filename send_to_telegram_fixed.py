#!/usr/bin/env python3
"""
Send to Telegram - Try multiple methods
"""

import os
import requests
import time

# Load from .env
token = "7605741830:AAHLuUuz2v4IKz2GlLOVv-vOR0wXb9qsdUI"
user_id = "1978452909"
channel_id = "-2001381541642"

print("Testing Telegram connections...")
print(f"Token: {token[:20]}...")
print(f"User ID: {user_id}")
print(f"Channel ID: {channel_id}")

# Test 1: Send to User ID
print("\n1️⃣  Trying to send to User ID...")
url = f"https://api.telegram.org/bot{token}/sendMessage"
data = {
    'chat_id': user_id,
    'text': '🔬 *Quantum Hybrid vs LLM-TradeBot 對比完成!*\n\n📊 Test Message from OpenCode',
    'parse_mode': 'Markdown'
}

response = requests.post(url, json=data)
print(f"   Response: {response.status_code}")
if response.status_code == 200:
    print(f"   ✅ SUCCESS! Message sent to User ID")
else:
    print(f"   ❌ Failed: {response.text[:100]}")

# Test 2: Try the channel
time.sleep(1)
print("\n2️⃣  Trying to send to Channel ID...")
data['chat_id'] = channel_id
response = requests.post(url, json=data)
print(f"   Response: {response.status_code}")
if response.status_code == 200:
    print(f"   ✅ SUCCESS! Message sent to Channel")
else:
    print(f"   ❌ Failed: {response.text[:100]}")

