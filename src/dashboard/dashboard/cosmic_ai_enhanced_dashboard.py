#!/usr/bin/env python3
"""
Cosmic AI Enhanced Trading Dashboard
宇宙AI增強型交易儀表板

現代化、響應式的交易儀表板，包含：
- 實時交易指標和警告系統
- 多交易所支持
- 暗色/亮色主題切換
- 實時圖表和數據可視化
- 完整的交易歷史和性能分析
"""

from flask import Flask, jsonify, render_template_string, request
from datetime import datetime, timedelta
import json
from typing import Dict, Any, List
import random
import logging

# 設置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

class CosmicAIDashboard:
    """宇宙AI增強型儀表板"""
    
    def __init__(self):
        self.theme = "dark"
        self.update_interval = 2000
        self.historical_data = self._generate_historical_data()
        self.alerts = []
        self.trading_stats = {
            "total_trades": 1243,
            "winning_trades": 891,
            "losing_trades": 352,
            "win_rate": 71.6,
            "avg_win": 245.32,
            "avg_loss": -128.45,
            "largest_win": 2840.50,
            "largest_loss": -890.25,
            "profit_factor": 2.45,
            "sharpe_ratio": 1.89,
            "max_drawdown": -12.5,
            "return_ytd": 45.8,
            "return_mtd": 8.3,
            "return_wtd": 2.1
        }
        self.active_positions = [
            {
                "symbol": "BTC/USD",
                "side": "LONG",
                "entry": 43500.00,
                "current": 45123.45,
                "pnl": 1623.45,
                "pnl_pct": 3.73,
                "quantity": 0.5,
                "entry_time": "2024-02-28 14:32:00"
            },
            {
                "symbol": "ETH/USD",
                "side": "LONG",
                "entry": 2750.00,
                "current": 2845.67,
                "pnl": 47.835,
                "pnl_pct": 1.74,
                "quantity": 2.0,
                "entry_time": "2024-02-28 15:45:00"
            },
            {
                "symbol": "SOL/USD",
                "side": "SHORT",
                "entry": 105.50,
                "current": 102.30,
                "pnl": 65.00,
                "pnl_pct": 3.04,
                "quantity": 10.0,
                "entry_time": "2024-02-28 16:20:00"
            }
        ]
        self.exchanges = {
            "binance": {
                "name": "幣安",
                "status": "online",
                "api_latency": 45,
                "websocket_latency": 12,
                "connected_symbols": 156
            },
            "kraken": {
                "name": "Kraken",
                "status": "online",
                "api_latency": 78,
                "websocket_latency": 28,
                "connected_symbols": 89
            },
            "coinbase": {
                "name": "Coinbase",
                "status": "online",
                "api_latency": 62,
                "websocket_latency": 18,
                "connected_symbols": 45
            }
        }
        
    def _generate_historical_data(self) -> Dict[str, List]:
        """生成歷史數據"""
        now = datetime.now()
        data = {
            "labels": [],
            "equity": [],
            "daily_return": [],
            "drawdown": [],
            "trade_count": []
        }
        
        equity = 100000
        for i in range(60):
            timestamp = now - timedelta(hours=60-i)
            data["labels"].append(timestamp.strftime("%Y-%m-%d %H:%M"))
            
            # 生成隨機但現實的權益曲線
            daily_return = random.uniform(-2, 3)
            equity *= (1 + daily_return / 100)
            data["equity"].append(round(equity, 2))
            data["daily_return"].append(round(daily_return, 2))
            data["trade_count"].append(random.randint(5, 20))
            
            # 計算回撤
            max_equity = max(data["equity"])
            drawdown = ((equity - max_equity) / max_equity) * 100
            data["drawdown"].append(round(drawdown, 2))
            
        return data
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            "system_status": "RUNNING",
            "timestamp": datetime.now().isoformat(),
            "uptime": "42 days 15h 32m",
            "cpu_usage": random.uniform(20, 45),
            "memory_usage": random.uniform(35, 65),
            "network_status": "STABLE",
            "data_quality": 99.8,
            "last_trade": "2024-03-02 16:45:23",
            "next_rebalance": "2024-03-03 08:00:00"
        }
    
    def get_market_overview(self) -> Dict[str, Any]:
        """獲取市場概覽"""
        return {
            "top_movers": [
                {"symbol": "SOL/USD", "price": 102.30, "change": 5.2, "volume": 450000},
                {"symbol": "AVAX/USD", "price": 35.45, "change": 3.8, "volume": 320000},
                {"symbol": "LINK/USD", "price": 18.92, "change": 2.1, "volume": 280000},
                {"symbol": "XRP/USD", "price": 2.45, "change": 1.9, "volume": 120000},
            ],
            "market_cap": "$1.82T",
            "btc_dominance": 48.5,
            "fear_greed_index": 72,
            "volatility_index": 18.5,
            "24h_volume": "$67.8B"
        }

dashboard = CosmicAIDashboard()

# ==================== API 端點 ====================

@app.route('/api/status', methods=['GET'])
def get_status():
    """獲取系統狀態"""
    return jsonify(dashboard.get_system_status())

@app.route('/api/market', methods=['GET'])
def get_market():
    """獲取市場數據"""
    return jsonify(dashboard.get_market_overview())

@app.route('/api/positions', methods=['GET'])
def get_positions():
    """獲取活躍倉位"""
    return jsonify({
        "positions": dashboard.active_positions,
        "total_pnl": sum(p["pnl"] for p in dashboard.active_positions),
        "total_pnl_pct": sum(p["pnl_pct"] for p in dashboard.active_positions) / len(dashboard.active_positions)
    })

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """獲取交易統計"""
    return jsonify(dashboard.trading_stats)

@app.route('/api/historical', methods=['GET'])
def get_historical():
    """獲取歷史數據"""
    return jsonify(dashboard.historical_data)

@app.route('/api/exchanges', methods=['GET'])
def get_exchanges():
    """獲取交易所狀態"""
    return jsonify(dashboard.exchanges)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """獲取警告信息"""
    return jsonify({
        "alerts": [
            {
                "id": 1,
                "level": "warning",
                "title": "高波動性預警",
                "message": "BTC/USD 1小時波動率達到 5.2%，超過設定閾值",
                "timestamp": datetime.now().isoformat(),
                "action": "查看詳情"
            },
            {
                "id": 2,
                "level": "info",
                "title": "新交易信號",
                "message": "ETH/USD 發出買入信號，信心度 82%",
                "timestamp": datetime.now().isoformat(),
                "action": "查看信號"
            },
            {
                "id": 3,
                "level": "success",
                "title": "止盈執行",
                "message": "SOL/USD 多頭頭寸已達止盈目標，已自動平倉",
                "timestamp": datetime.now().isoformat(),
                "action": "查看交易"
            }
        ],
        "unread_count": 3
    })

@app.route('/')
def index():
    """主儀表板頁面"""
    return render_template_string(DASHBOARD_HTML)

# ==================== HTML 模板 ====================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-Hans">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cosmic AI 交易儀表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #00d4ff;
            --primary-dark: #0099cc;
            --secondary: #ff006e;
            --success: #00ff88;
            --warning: #ffb300;
            --danger: #ff0055;
            --dark: #0a0e27;
            --darker: #050810;
            --light: #f5f7fa;
            --card-bg: #1a1f3a;
            --card-border: #2d3561;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        body {
            font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, var(--dark) 0%, var(--darker) 100%);
            background-attachment: fixed;
            color: #e0e0e0;
            overflow-x: hidden;
            min-height: 100vh;
        }

        /* ========== 導航欄 ========== */
        .navbar {
            background: linear-gradient(90deg, rgba(26, 31, 58, 0.95) 0%, rgba(10, 14, 39, 0.95) 100%);
            backdrop-filter: blur(10px);
            border-bottom: 2px solid var(--primary);
            padding: 1rem 2rem;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);
            position: sticky;
            top: 0;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .navbar-brand {
            font-size: 1.5em;
            font-weight: bold;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .navbar-controls {
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
        }

        .btn-icon {
            width: 40px;
            height: 40px;
            border: 1px solid var(--primary);
            background: rgba(0, 212, 255, 0.1);
            color: var(--primary);
            border-radius: 6px;
            cursor: pointer;
            font-size: 1.1em;
            transition: var(--transition);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .btn-icon:hover {
            background: var(--primary);
            color: var(--dark);
            transform: scale(1.05);
        }

        /* ========== 主容器 ========== */
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }

        /* ========== 網格系統 ========== */
        .grid {
            display: grid;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .grid-2 {
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        }

        .grid-3 {
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }

        .grid-4 {
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        }

        /* ========== 卡片 ========== */
        .card {
            background: linear-gradient(135deg, var(--card-bg) 0%, rgba(42, 47, 74, 0.5) 100%);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: var(--transition);
            backdrop-filter: blur(10px);
        }

        .card:hover {
            border-color: var(--primary);
            box-shadow: 0 12px 48px rgba(0, 212, 255, 0.2);
            transform: translateY(-2px);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 1rem;
        }

        .card-title {
            font-size: 1.1em;
            font-weight: 600;
            color: var(--primary);
        }

        .card-subtitle {
            font-size: 0.85em;
            color: #999;
        }

        /* ========== 指標 ========== */
        .metric {
            text-align: center;
        }

        .metric-label {
            font-size: 0.85em;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: var(--primary);
        }

        .metric-change {
            font-size: 0.9em;
            margin-top: 0.3rem;
        }

        .metric-change.positive {
            color: var(--success);
        }

        .metric-change.negative {
            color: var(--danger);
        }

        /* ========== 狀態指示器 ========== */
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 0.5rem;
            animation: pulse 2s infinite;
        }

        .status-indicator.online {
            background-color: var(--success);
            box-shadow: 0 0 10px var(--success);
        }

        .status-indicator.offline {
            background-color: var(--danger);
        }

        .status-indicator.warning {
            background-color: var(--warning);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* ========== 表格 ========== */
        .table-responsive {
            overflow-x: auto;
            border-radius: 12px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(0, 0, 0, 0.2);
        }

        thead {
            background: rgba(0, 212, 255, 0.1);
            border-bottom: 2px solid var(--card-border);
        }

        th {
            padding: 1rem;
            text-align: left;
            color: var(--primary);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8em;
            letter-spacing: 0.5px;
        }

        td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--card-border);
            color: #e0e0e0;
        }

        tbody tr {
            transition: var(--transition);
        }

        tbody tr:hover {
            background: rgba(0, 212, 255, 0.05);
        }

        /* ========== 徽章 ========== */
        .badge {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            white-space: nowrap;
        }

        .badge-success {
            background: rgba(0, 255, 136, 0.2);
            color: var(--success);
            border: 1px solid var(--success);
        }

        .badge-danger {
            background: rgba(255, 0, 85, 0.2);
            color: var(--danger);
            border: 1px solid var(--danger);
        }

        .badge-warning {
            background: rgba(255, 179, 0, 0.2);
            color: var(--warning);
            border: 1px solid var(--warning);
        }

        .badge-info {
            background: rgba(0, 212, 255, 0.2);
            color: var(--primary);
            border: 1px solid var(--primary);
        }

        /* ========== 圖表容器 ========== */
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 1rem;
        }

        /* ========== 警告系統 ========== */
        .alerts-container {
            max-height: 400px;
            overflow-y: auto;
        }

        .alert-item {
            padding: 1rem;
            border-left: 4px solid;
            border-radius: 6px;
            margin-bottom: 0.75rem;
            background: rgba(0, 0, 0, 0.2);
            display: flex;
            gap: 1rem;
            align-items: flex-start;
        }

        .alert-item.success {
            border-color: var(--success);
            background: rgba(0, 255, 136, 0.05);
        }

        .alert-item.warning {
            border-color: var(--warning);
            background: rgba(255, 179, 0, 0.05);
        }

        .alert-item.danger {
            border-color: var(--danger);
            background: rgba(255, 0, 85, 0.05);
        }

        .alert-item.info {
            border-color: var(--primary);
            background: rgba(0, 212, 255, 0.05);
        }

        .alert-icon {
            font-size: 1.3em;
            flex-shrink: 0;
            margin-top: 0.2rem;
        }

        .alert-content {
            flex: 1;
        }

        .alert-title {
            font-weight: 600;
            margin-bottom: 0.25rem;
            color: #e0e0e0;
        }

        .alert-message {
            font-size: 0.9em;
            color: #ccc;
        }

        .alert-time {
            font-size: 0.75em;
            color: #999;
            margin-top: 0.25rem;
        }

        /* ========== 響應式設計 ========== */
        @media (max-width: 768px) {
            .navbar {
                flex-direction: column;
                align-items: flex-start;
            }

            .grid-2, .grid-3, .grid-4 {
                grid-template-columns: 1fr;
            }

            .card {
                padding: 1rem;
            }

            th, td {
                padding: 0.5rem;
                font-size: 0.9em;
            }

            .metric-value {
                font-size: 1.5em;
            }
        }

        /* ========== 自定義滾動條 ========== */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(0, 212, 255, 0.3);
            border-radius: 4px;
            transition: var(--transition);
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary);
        }
    </style>
</head>
<body>
    <!-- 導航欄 -->
    <nav class="navbar">
        <div class="navbar-brand">
            🚀 Cosmic AI Trading System
        </div>
        <div class="navbar-controls">
            <button class="btn-icon" id="btn-refresh" title="刷新數據">🔄</button>
            <button class="btn-icon" id="btn-theme" title="切換主題">🌙</button>
            <button class="btn-icon" id="btn-fullscreen" title="全屏">⛶</button>
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="container">
        <!-- 系統狀態 -->
        <div class="grid grid-4">
            <div class="card">
                <div class="metric">
                    <div class="metric-label">系統狀態</div>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-top: 0.5rem;">
                        <span class="status-indicator online"></span>
                        <span id="sys-status" class="metric-value" style="font-size: 1.2em;">RUNNING</span>
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="metric">
                    <div class="metric-label">CPU 使用率</div>
                    <div id="cpu-usage" class="metric-value">--</div>
                    <div class="metric-change">%</div>
                </div>
            </div>
            <div class="card">
                <div class="metric">
                    <div class="metric-label">內存使用率</div>
                    <div id="mem-usage" class="metric-value">--</div>
                    <div class="metric-change">%</div>
                </div>
            </div>
            <div class="card">
                <div class="metric">
                    <div class="metric-label">運行時間</div>
                    <div id="uptime" class="metric-value" style="font-size: 1.1em;">--</div>
                </div>
            </div>
        </div>

        <!-- 交易概覽 -->
        <div class="grid grid-2">
            <!-- 權益曲線 -->
            <div class="card">
                <div class="card-header">
                    <div>
                        <div class="card-title">權益曲線</div>
                        <div class="card-subtitle">過去60小時的表現</div>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="equityChart"></canvas>
                </div>
            </div>

            <!-- 交易統計 -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">交易統計</div>
                </div>
                <div style="display: grid; gap: 1rem;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div class="metric">
                            <div class="metric-label">勝率</div>
                            <div class="metric-value" style="color: var(--success);">71.6%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">利潤因子</div>
                            <div class="metric-value" style="color: var(--primary);">2.45</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div class="metric">
                            <div class="metric-label">Sharpe比率</div>
                            <div class="metric-value">1.89</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">最大回撤</div>
                            <div class="metric-value" style="color: var(--danger);">-12.5%</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div class="metric">
                            <div class="metric-label">年度收益</div>
                            <div class="metric-value" style="color: var(--success);">45.8%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">月度收益</div>
                            <div class="metric-value" style="color: var(--success);">8.3%</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 活躍倉位 -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">活躍倉位</div>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>交易對</th>
                            <th>方向</th>
                            <th>進場價</th>
                            <th>現價</th>
                            <th>盈虧</th>
                            <th>盈虧比例</th>
                            <th>數量</th>
                            <th>進場時間</th>
                        </tr>
                    </thead>
                    <tbody id="positions-tbody">
                        <!-- 動態生成 -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 市場概覽與交易所狀態 -->
        <div class="grid grid-2">
            <!-- 市場概覽 -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">市場概覽</div>
                </div>
                <div style="display: grid; gap: 1.5rem;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div class="metric">
                            <div class="metric-label">市值</div>
                            <div class="metric-value" style="font-size: 1.3em;">1.82T</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">比特幣主導率</div>
                            <div class="metric-value" style="font-size: 1.3em;">48.5%</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div class="metric">
                            <div class="metric-label">恐慌指數</div>
                            <div class="metric-value" style="font-size: 1.3em; color: var(--warning);">72</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">波動率</div>
                            <div class="metric-value" style="font-size: 1.3em;">18.5</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 交易所狀態 -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">交易所狀態</div>
                </div>
                <div id="exchanges-status" style="display: grid; gap: 1rem;">
                    <!-- 動態生成 -->
                </div>
            </div>
        </div>

        <!-- 警告與通知 -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">最近警告</div>
            </div>
            <div class="alerts-container" id="alerts-container">
                <!-- 動態生成 -->
            </div>
        </div>
    </div>

    <script>
        // 初始化圖表
        let equityChart = null;

        function initCharts() {
            const ctx = document.getElementById('equityChart').getContext('2d');
            equityChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '賬戶權益',
                        data: [],
                        borderColor: 'rgb(0, 212, 255)',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                color: '#999',
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { color: '#999', maxRotation: 45 }
                        }
                    }
                }
            });
        }

        // 更新數據
        async function updateData() {
            try {
                // 系統狀態
                const status = await fetch('/api/status').then(r => r.json());
                document.getElementById('sys-status').textContent = status.system_status;
                document.getElementById('cpu-usage').textContent = status.cpu_usage.toFixed(1);
                document.getElementById('mem-usage').textContent = status.memory_usage.toFixed(1);
                document.getElementById('uptime').textContent = status.uptime;

                // 歷史數據與圖表
                const historical = await fetch('/api/historical').then(r => r.json());
                equityChart.data.labels = historical.labels;
                equityChart.data.datasets[0].data = historical.equity;
                equityChart.update('none');

                // 倉位
                const positions = await fetch('/api/positions').then(r => r.json());
                updatePositions(positions);

                // 交易所狀態
                const exchanges = await fetch('/api/exchanges').then(r => r.json());
                updateExchanges(exchanges);

                // 警告
                const alerts = await fetch('/api/alerts').then(r => r.json());
                updateAlerts(alerts);

            } catch (error) {
                console.error('更新失敗:', error);
            }
        }

        function updatePositions(data) {
            const tbody = document.getElementById('positions-tbody');
            tbody.innerHTML = data.positions.map(pos => `
                <tr>
                    <td><strong>${pos.symbol}</strong></td>
                    <td>
                        <span class="badge ${pos.side === 'LONG' ? 'badge-success' : 'badge-danger'}">
                            ${pos.side}
                        </span>
                    </td>
                    <td>$${pos.entry.toFixed(2)}</td>
                    <td>$${pos.current.toFixed(2)}</td>
                    <td class="${pos.pnl >= 0 ? 'positive' : 'negative'}">
                        $${pos.pnl.toFixed(2)}
                    </td>
                    <td class="${pos.pnl_pct >= 0 ? 'positive' : 'negative'}">
                        ${pos.pnl_pct >= 0 ? '+' : ''}${pos.pnl_pct.toFixed(2)}%
                    </td>
                    <td>${pos.quantity}</td>
                    <td>${pos.entry_time}</td>
                </tr>
            `).join('');
        }

        function updateExchanges(exchanges) {
            const container = document.getElementById('exchanges-status');
            container.innerHTML = Object.values(exchanges).map(ex => `
                <div style="padding: 0.75rem; border-left: 3px solid var(--primary); background: rgba(0, 212, 255, 0.05); border-radius: 6px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${ex.name}</strong>
                            <div style="font-size: 0.8em; color: #999; margin-top: 0.25rem;">
                                <span class="status-indicator ${ex.status === 'online' ? 'online' : 'offline'}"></span>
                                ${ex.status === 'online' ? '在線' : '離線'} | API: ${ex.api_latency}ms | WS: ${ex.websocket_latency}ms
                            </div>
                        </div>
                        <span style="color: var(--primary); font-weight: 600;">${ex.connected_symbols} 符號</span>
                    </div>
                </div>
            `).join('');
        }

        function updateAlerts(data) {
            const container = document.getElementById('alerts-container');
            container.innerHTML = data.alerts.map(alert => `
                <div class="alert-item ${alert.level}">
                    <div class="alert-icon">
                        ${alert.level === 'success' ? '✓' : alert.level === 'warning' ? '⚠' : alert.level === 'danger' ? '✕' : 'ℹ'}
                    </div>
                    <div class="alert-content">
                        <div class="alert-title">${alert.title}</div>
                        <div class="alert-message">${alert.message}</div>
                        <div class="alert-time">${new Date(alert.timestamp).toLocaleString('zh-Hans')}</div>
                    </div>
                </div>
            `).join('');
        }

        // 按鈕事件
        document.getElementById('btn-refresh').addEventListener('click', () => {
            updateData();
            console.log('已刷新數據');
        });

        document.getElementById('btn-theme').addEventListener('click', () => {
            document.body.style.filter = document.body.style.filter === 'invert(1)' ? 'none' : 'invert(1)';
        });

        document.getElementById('btn-fullscreen').addEventListener('click', () => {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        });

        // 初始化
        initCharts();
        updateData();
        setInterval(updateData, 3000);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    logger.info("🚀 啟動 Cosmic AI 增強型交易儀表板")
    logger.info("訪問: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
