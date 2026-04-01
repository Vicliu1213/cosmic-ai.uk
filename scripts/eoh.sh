#!/bin/bash
# EON-MarketBot 真正的一鍵部署
# 使用方法: bash eon.sh

set -e

echo "🌌 EON-MarketBot 一鍵部署開始..."

# 創建項目目錄
mkdir -p eon-marketbot
cd eon-marketbot

# 創建所有文件
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && make install && \
    cd .. && rm -rf ta-lib*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  eon:
    build: .
    container_name: eon-marketbot
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
EOF

cat > requirements.txt << 'EOF'
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
scipy==1.11.1
ccxt==4.1.22
TA-Lib==0.4.28
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
pyyaml==6.0.1
cryptography==41.0.7
requests==2.31.0
EOF

cat > app.py << 'EOF'
#!/usr/bin/env python3
"""
EON-MarketBot - 單文件一鍵部署版
包含：量子手環、感知場、交易系統、API
"""

import hashlib
import secrets
import time
import json
import os
import numpy as np
import pandas as pd
import ccxt
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from collections import deque

# ==================== 量子手環 ====================
class QuantumRing:
    def __init__(self):
        self.master_key = None
        self.session_key = None
        self.session_expiry = 0
        self.authenticated = False
        self.behavior_history = deque(maxlen=100)
        self.behavior_mean = None
        self.behavior_std = None

    def initialize(self):
        self.master_key = secrets.token_hex(32)
        return self.master_key[:16] + "..."

    def record_behavior(self, features):
        self.behavior_history.append(features)
        if len(self.behavior_history) >= 10:
            arr = np.array(self.behavior_history)
            self.behavior_mean = np.mean(arr, axis=0)
            self.behavior_std = np.std(arr, axis=0) + 1e-8

    def authenticate(self, features):
        self.record_behavior(features)
        if self.behavior_mean is None:
            return False, 0.0

        z = np.abs((features - self.behavior_mean) / self.behavior_std)
        confidence = float(np.mean(np.exp(-z)))

        if confidence > 0.6:
            self.session_key = secrets.token_hex(32)
            self.session_expiry = time.time() + 3600
            self.authenticated = True
            return True, confidence
        return False, confidence

    def check_session(self):
        return self.authenticated and time.time() < self.session_expiry

    def get_token(self):
        if not self.check_session():
            return None
        return hashlib.sha256(f"{self.session_key}".encode()).hexdigest()

# ==================== 感知場 ====================
class PerceptionField:
    def __init__(self):
        self.exchange = ccxt.binance({'enableRateLimit': True})
        self.last_data = {}

    def fetch_btc(self):
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            ohlcv = self.exchange.fetch_ohlcv('BTC/USDT', '1h', limit=50)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            return {
                'price': ticker['last'],
                'change': ticker['percentage'],
                'volume': ticker['quoteVolume'],
                'high': ticker['high'],
                'low': ticker['low'],
                'history': df['close'].tolist()
            }
        except Exception as e:
            return {'error': str(e)}

    def update(self):
        self.last_data = {
            'btc': self.fetch_btc(),
            'timestamp': datetime.now().isoformat()
        }
        return self.last_data

# ==================== 森林增強分析 ====================
class ForestAnalyzer:
    def __init__(self):
        from sklearn.ensemble import RandomForestClassifier, IsolationForest
        self.classifier = RandomForestClassifier(n_estimators=10)
        self.anomaly = IsolationForest(contamination=0.1)
        self.is_trained = False

    def analyze(self, prices):
        if len(prices) < 20:
            return {'signal': 0, 'confidence': 0.3, 'singularity': 0.1}

        # 簡單技術指標
        prices = np.array(prices)
        ma5 = np.mean(prices[-5:])
        ma20 = np.mean(prices[-20:])
        rsi = self._calculate_rsi(prices)
        volatility = np.std(prices[-20:]) / np.mean(prices[-20:])

        # 生成信號
        if ma5 > ma20 * 1.02 and rsi < 70:
            signal = 1
            confidence = min(0.9, abs(ma5/ma20 - 1) * 20)
        elif ma5 < ma20 * 0.98 and rsi > 30:
            signal = -1
            confidence = min(0.9, abs(1 - ma5/ma20) * 20)
        else:
            signal = 0
            confidence = 0.3

        # 奇點概率（異常檢測）
        features = np.array([[rsi, volatility, ma5/ma20]])
        if self.is_trained:
            singularity = float(1 - self.anomaly.score_samples(features)[0])
            singularity = 1 / (1 + np.exp(-singularity * 10))
        else:
            singularity = 0.1

        return {
            'signal': signal,
            'confidence': confidence,
            'singularity': singularity,
            'indicators': {
                'rsi': float(rsi),
                'ma5': float(ma5),
                'ma20': float(ma20),
                'volatility': float(volatility)
            }
        }

    def _calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return 50
        deltas = np.diff(prices[-period-1:])
        gain = np.mean(deltas[deltas > 0]) if any(deltas > 0) else 0
        loss = -np.mean(deltas[deltas < 0]) if any(deltas < 0) else 1
        rs = gain / loss if loss != 0 else 0
        return 100 - (100 / (1 + rs))

# ==================== 異變引擎 ====================
class StrategyGene:
    def __init__(self, params):
        self.params = params
        self.fitness = 0.0

    def mutate(self):
        new_params = self.params.copy()
        for k in new_params:
            if np.random.random() < 0.3:
                if isinstance(new_params[k], float):
                    new_params[k] *= np.random.normal(1.0, 0.1)
        return StrategyGene(new_params)

class EvolutionEngine:
    def __init__(self):
        self.genes = [
            StrategyGene({'lookback': 10, 'threshold': 1.2}),
            StrategyGene({'lookback': 20, 'threshold': 1.5}),
            StrategyGene({'lookback': 30, 'threshold': 1.8}),
            StrategyGene({'lookback': 50, 'threshold': 2.0})
        ]
        self.generation = 0

    def evolve(self):
        for g in self.genes:
            g.fitness = np.random.random()  # 模擬適應度

        self.genes.sort(key=lambda x: x.fitness, reverse=True)
        new_genes = self.genes[:2]

        for _ in range(2):
            new_genes.append(self.genes[0].mutate())
            new_genes.append(self.genes[1].mutate())

        self.genes = new_genes
        self.generation += 1
        return self.genes[0]

# ==================== 交易執行 ====================
class TradeExecutor:
    def __init__(self):
        self.paper_trading = True
        self.capital = 10000
        self.positions = {}
        self.trades = []

    def execute(self, signal, price):
        if signal['signal'] == 0:
            return {'status': 'no_action'}

        size = self.capital * 0.1 / price
        if signal['signal'] == 1:
            self.positions['BTC'] = self.positions.get('BTC', 0) + size
            self.capital -= size * price
        else:
            if 'BTC' in self.positions:
                self.capital += self.positions['BTC'] * price
                del self.positions['BTC']

        trade = {
            'timestamp': datetime.now().isoformat(),
            'action': 'BUY' if signal['signal'] == 1 else 'SELL',
            'price': price,
            'size': size,
            'confidence': signal['confidence']
        }
        self.trades.append(trade)

        return trade

# ==================== FastAPI ====================
app = FastAPI(title="EON-MarketBot")

# 掛載靜態文件（稍後創建）
os.makedirs("static", exist_ok=True)

# 全局實例
ring = QuantumRing()
perception = PerceptionField()
analyzer = ForestAnalyzer()
evolution = EvolutionEngine()
executor = TradeExecutor()

class AuthRequest(BaseModel):
    features: List[float]

@app.get("/")
async def root():
    return {"message": "EON-MarketBot 運行中", "status": "online"}

@app.post("/ring/init")
async def init_ring():
    key = ring.initialize()
    return {"status": "success", "master_key": key}

@app.post("/ring/auth")
async def auth(req: AuthRequest):
    success, conf = ring.authenticate(np.array(req.features))
    token = ring.get_token()
    return {"authenticated": success, "confidence": conf, "token": token}

@app.get("/perception/btc")
async def get_btc():
    data = perception.update()
    return data

@app.get("/analyze/btc")
async def analyze_btc():
    data = perception.update()
    if 'btc' in data and 'history' in data['btc']:
        result = analyzer.analyze(data['btc']['history'])
        return result
    return {"error": "no data"}

@app.post("/evolve")
async def evolve():
    best = evolution.evolve()
    return {
        "generation": evolution.generation,
        "best_params": best.params,
        "best_fitness": best.fitness
    }

@app.post("/trade/test")
async def test_trade():
    data = perception.update()
    if 'btc' not in data:
        return {"error": "no data"}

    analysis = analyzer.analyze(data['btc'].get('history', []))
    result = executor.execute(analysis, data['btc'].get('price', 0))

    return {
        "signal": analysis,
        "trade": result,
        "capital": executor.capital,
        "positions": executor.positions
    }

@app.get("/status")
async def status():
    return {
        "authenticated": ring.check_session(),
        "capital": executor.capital,
        "positions": executor.positions,
        "trades": len(executor.trades),
        "generation": evolution.generation
    }

# ==================== 創建簡單的靜態頁面 ====================
with open("static/index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>EON-MarketBot</title>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: #fff; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: #16213e; padding: 20px; margin: 10px 0; border-radius: 10px; }
        button { background: #0f3460; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px; cursor: pointer; }
        button:hover { background: #1a1a2e; }
        pre { background: #0f3460; padding: 10px; border-radius: 5px; overflow: auto; }
        .status { color: #4CAF50; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌌 EON-MarketBot 控制台</h1>

        <div class="card">
            <h2>量子手環</h2>
            <button onclick="initRing()">初始化</button>
            <button onclick="auth()">認證</button>
            <div id="ring-status" class="status">未認證</div>
        </div>

        <div class="card">
            <h2>市場數據</h2>
            <button onclick="fetchBTC()">獲取BTC價格</button>
            <button onclick="analyze()">技術分析</button>
            <pre id="market-data"></pre>
        </div>

        <div class="card">
            <h2>交易</h2>
            <button onclick="trade()">測試交易</button>
            <button onclick="status()">系統狀態</button>
            <pre id="trade-result"></pre>
        </div>

        <div class="card">
            <h2>異變引擎</h2>
            <button onclick="evolve()">進化一代</button>
            <pre id="evolution-data"></pre>
        </div>
    </div>

    <script>
        let token = localStorage.getItem('token');
        const api = 'http://localhost:8000';

        async function initRing() {
            const res = await fetch(api + '/ring/init', {method: 'POST'});
            const data = await res.json();
            alert('初始化成功！主密鑰: ' + data.master_key);
        }

        async function auth() {
            const features = Array(10).fill(0).map(() => Math.random());
            const res = await fetch(api + '/ring/auth', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({features})
            });
            const data = await res.json();
            if (data.authenticated) {
                document.getElementById('ring-status').innerHTML = '✅ 已認證 置信度: ' + (data.confidence*100).toFixed(1) + '%';
                localStorage.setItem('token', data.token);
            } else {
                document.getElementById('ring-status').innerHTML = '❌ 認證失敗';
            }
        }

        async function fetchBTC() {
            const res = await fetch(api + '/perception/btc');
            const data = await res.json();
            document.getElementById('market-data').innerHTML = JSON.stringify(data, null, 2);
        }

        async function analyze() {
            const res = await fetch(api + '/analyze/btc');
            const data = await res.json();
            document.getElementById('market-data').innerHTML = '分析結果:\n' + JSON.stringify(data, null, 2);
        }

        async function trade() {
            const res = await fetch(api + '/trade/test', {method: 'POST'});
            const data = await res.json();
            document.getElementById('trade-result').innerHTML = JSON.stringify(data, null, 2);
        }

        async function status() {
            const res = await fetch(api + '/status');
            const data = await res.json();
            document.getElementById('trade-result').innerHTML = JSON.stringify(data, null, 2);
        }

        async function evolve() {
            const res = await fetch(api + '/evolve', {method: 'POST'});
            const data = await res.json();
            document.getElementById('evolution-data').innerHTML = JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>
    """)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ==================== 啟動 ====================
if __name__ == "__main__":
    print("🌌 EON-MarketBot 啟動中...")
    print("訪問 http://localhost:8000/static 打開控制台")
    print("按 Ctrl+C 停止")
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# 創建啟動腳本
cat > start.sh << 'EOF'
#!/bin/bash
python app.py
EOF

chmod +x start.sh

# 創建數據目錄
mkdir -p data

# 選擇部署方式
echo ""
echo "==================================="
echo "🌌 EON-MarketBot 一鍵部署完成！"
echo "==================================="
echo ""
echo "請選擇啟動方式："
echo ""
echo "1) 本地 Python (快速啟動)"
echo "2) Docker (隔離環境)"
echo ""
read -p "請輸入選擇 [1/2]: " choice

if [ "$choice" = "2" ]; then
    echo "🐳 使用 Docker 啟動..."
    docker-compose up -d
    echo "✅ Docker 容器已啟動"
    echo "訪問: http://localhost:8000/static"
elif [ "$choice" = "1" ]; then
    echo "🐍 使用 Python 啟動..."
    echo "安裝依賴中..."
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✅ 依賴安裝完成"
    echo ""
    echo "🚀 啟動服務..."
    python app.py
else
    echo "❌ 無效選擇"
    exit 1
fi
EOF

# 執行
bash start.sh
