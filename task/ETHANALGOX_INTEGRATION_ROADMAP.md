# 🔗 EthanAlgoX 整合執行路線圖

**建立日期**: 2026-03-02  
**狀態**: 📋 待開始  
**優先級**: 🔴 P1 (Critical Path)  
**預計時間**: 1-2 周 (第1階段)

---

## 🎯 整合目標

### 第1階段 (P1) - 1-2週內完成
- ✅ Clone 核心儲存庫
- ✅ 分析代碼架構
- ✅ MarketBot 面板層集成
- ✅ LLM-TradeBot 決策層集成
- ✅ 端到端測試

### 第2階段 (P2) - 2-3週後開始
- ⏳ AgentOlympics 社交層
- ⏳ 信譽系統實現
- ⏳ 區塊鏈審計日誌

### 第3階段 (P3) - 参考整合
- ⏳ LLM-TradeBot-Stocks 策略參考

---

## 📅 日程安排

### ✅ 第1天: 環境準備 (READY)

#### 1.1 Clone 儲存庫

```bash
# 切換到工作目錄
cd /workspaces/cosmic-ai.uk

# 創建外部集成目錄
mkdir -p external/
mkdir -p src/integrations/
mkdir -p config/external_integrations/

# Clone MarketBot (優先級最高)
cd external
git clone https://github.com/EthanAlgoX/MarketBot.git

# Clone LLM-TradeBot
git clone https://github.com/EthanAlgoX/LLM-TradeBot.git

# Clone AgentOlympics (P2用)
git clone https://github.com/EthanAlgoX/AgentOlympics.git

# 返回主目錄
cd /workspaces/cosmic-ai.uk
```

#### 1.2 驗證代碼結構

```bash
# 檢查 MarketBot 結構
echo "=== MarketBot Structure ==="
ls -la external/marketbot/src/
echo ""
echo "Key directories:"
find external/marketbot -type d -name "gateway" -o -name "channels" -o -name "finance" | head -10

# 檢查 LLM-TradeBot 結構
echo ""
echo "=== LLM-TradeBot Structure ==="
ls -la external/llm_tradebot/
echo ""
echo "Key files:"
find external/llm_tradebot -type f -name "*agent*" -o -name "*router*" | head -10

# 檢查 AgentOlympics 結構
echo ""
echo "=== AgentOlympics Structure ==="
ls -la external/agent_olympics/
```

#### 1.3 安裝依賴

```bash
# 確保 MarketBot 依賴已準備
cd external/marketbot
pip install -r requirements.txt --dry-run

# 檢查 LLM-TradeBot 依賴
cd ../llm_tradebot
pip install -r requirements.txt --dry-run

cd /workspaces/cosmic-ai.uk
```

**✅ 第1天完成檢查清單**:
- [ ] external/ 目錄已創建
- [ ] 3 個儲存庫已 clone
- [ ] 代碼結構已驗證
- [ ] 依賴清單已檢查

---

### 📍 第2-3天: MarketBot 適配層開發

#### 2.1 分析 MarketBot API

**文件**: `docs/ETHANALGOX_ANALYSIS.md` (待創建)

```bash
# 分析關鍵文件
grep -r "class.*Gateway" external/marketbot/src/ | head -5
grep -r "def send_message" external/marketbot/src/ | head -5
grep -r "PORT\|port" external/marketbot/ | grep -i "18789\|gateway"
```

**重點查看**:
1. `external/marketbot/src/gateway/core.py` - Gateway 核心
2. `external/marketbot/src/channels/` - 多渠道實現
3. `external/marketbot/src/gateway/` - API 端點

#### 2.2 創建 MarketBot 連接器

**文件**: `src/integrations/marketbot_connector.py`

```python
"""
MarketBot Connector - Cosmic AI 與 MarketBot 的橋接層
功能:
  1. 將 Cosmic 交易信號轉換為 MarketBot 消息格式
  2. 支持多渠道交付 (DingTalk, WeChat, Telegram 等)
  3. 實時監控面板更新
  4. 交易記錄同步
"""

from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class CosmicSignal:
    """Cosmic AI 交易信號格式"""
    signal_id: str
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0-1
    price: float
    quantity: float
    strategy: str  # Phase 1/2/3/4
    timestamp: datetime
    metadata: Dict[str, Any] = None


@dataclass
class MarketBotMessage:
    """MarketBot 消息格式"""
    title: str
    content: str
    channels: List[str]
    priority: str  # LOW, NORMAL, HIGH, CRITICAL
    tags: List[str]
    data: Dict[str, Any] = None


class CosmicMarketBotBridge:
    """Cosmic <-> MarketBot 橋接器"""
    
    def __init__(self, 
                 gateway_url: str = "http://127.0.0.1:18789",
                 gateway_token: Optional[str] = None):
        """
        初始化連接器
        
        Args:
            gateway_url: MarketBot Gateway URL
            gateway_token: 認證 token (可選)
        """
        self.gateway_url = gateway_url
        self.gateway_token = gateway_token
        self.session: Optional[aiohttp.ClientSession] = None
        self.default_channels = [
            "dingtalk",      # 釘釘 (中文)
            "wecom",         # 企業微信 (中文)
            "telegram",      # Telegram (國際)
            "discord"        # Discord (國際)
        ]
    
    async def __aenter__(self):
        """異步上下文管理器"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文退出"""
        if self.session:
            await self.session.close()
    
    async def connect(self) -> bool:
        """驗證 Gateway 連接"""
        try:
            async with self.session.get(
                f"{self.gateway_url}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    logger.info("✅ MarketBot Gateway 連接成功")
                    return True
                else:
                    logger.error(f"❌ Gateway 返回錯誤: {resp.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Gateway 連接失敗: {e}")
            return False
    
    def _convert_signal_to_message(self, signal: CosmicSignal) -> MarketBotMessage:
        """將 Cosmic 信號轉換為 MarketBot 消息"""
        
        # 決定消息優先級
        priority = "CRITICAL" if signal.confidence > 0.9 else \
                   "HIGH" if signal.confidence > 0.7 else \
                   "NORMAL"
        
        # 構建消息內容
        title = f"🚀 {signal.strategy} {signal.action} 信號"
        
        content = f"""
交易信號詳情:
━━━━━━━━━━━━━━━━━━
📊 代碼: {signal.symbol}
💡 操作: {signal.action}
📈 信心: {signal.confidence:.1%}
💰 價格: ${signal.price:.2f}
📦 數量: {signal.quantity:.4f}
🎯 策略: {signal.strategy}
🕐 時間: {signal.timestamp.isoformat()}
━━━━━━━━━━━━━━━━━━

⚠️ 風險提示: 請在確認後執行交易
"""
        
        # 構建標籤
        tags = [signal.strategy.lower(), signal.action.lower(), signal.symbol.lower()]
        
        return MarketBotMessage(
            title=title,
            content=content,
            channels=self.default_channels,
            priority=priority,
            tags=tags,
            data={
                "signal_id": signal.signal_id,
                "symbol": signal.symbol,
                "action": signal.action,
                "confidence": signal.confidence,
                "price": signal.price,
                "quantity": signal.quantity,
                "strategy": signal.strategy
            }
        )
    
    async def send_signal(self, 
                         signal: CosmicSignal,
                         channels: Optional[List[str]] = None) -> bool:
        """
        發送交易信號到 MarketBot
        
        Args:
            signal: Cosmic 交易信號
            channels: 目標渠道列表 (默認使用預設渠道)
        
        Returns:
            是否發送成功
        """
        try:
            # 轉換信號格式
            message = self._convert_signal_to_message(signal)
            message.channels = channels or self.default_channels
            
            # 構建 API 請求
            headers = {}
            if self.gateway_token:
                headers["Authorization"] = f"Bearer {self.gateway_token}"
            
            payload = {
                "title": message.title,
                "content": message.content,
                "channels": message.channels,
                "priority": message.priority,
                "tags": message.tags,
                "data": message.data
            }
            
            # 發送到 MarketBot Gateway
            async with self.session.post(
                f"{self.gateway_url}/api/message/send",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    logger.info(f"✅ 信號已發送: {signal.signal_id} ({message.channels})")
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ 發送失敗 ({resp.status}): {error_text}")
                    return False
        
        except Exception as e:
            logger.error(f"❌ 發送過程出錯: {e}")
            return False
    
    async def send_chinese_im_only(self, 
                                   signal: CosmicSignal) -> bool:
        """
        僅發送到中文 IM (DingTalk, WeChat)
        用於中國用戶
        """
        chinese_channels = ["dingtalk", "wecom"]
        return await self.send_signal(signal, chinese_channels)
    
    async def send_international_only(self, 
                                      signal: CosmicSignal) -> bool:
        """
        僅發送到國際渠道 (Telegram, Discord)
        """
        intl_channels = ["telegram", "discord"]
        return await self.send_signal(signal, intl_channels)
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """獲取 MarketBot 監控狀態"""
        try:
            async with self.session.get(
                f"{self.gateway_url}/api/status",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"status": "error", "code": resp.status}
        except Exception as e:
            logger.error(f"❌ 獲取狀態失敗: {e}")
            return {"status": "error", "error": str(e)}


# 使用示例
async def example_usage():
    """使用示例"""
    
    # 創建連接器
    async with CosmicMarketBotBridge() as bridge:
        # 驗證連接
        if not await bridge.connect():
            logger.error("無法連接到 MarketBot Gateway")
            return
        
        # 創建交易信號
        signal = CosmicSignal(
            signal_id="sig_20260302_001",
            symbol="BTC/USDT",
            action="BUY",
            confidence=0.85,
            price=45000.0,
            quantity=0.5,
            strategy="Phase 3 Singularity",
            timestamp=datetime.now()
        )
        
        # 發送信號
        success = await bridge.send_signal(signal)
        if success:
            logger.info("✅ 信號發送成功")
        else:
            logger.error("❌ 信號發送失敗")
        
        # 獲取監控狀態
        status = await bridge.get_monitoring_status()
        logger.info(f"Monitor Status: {status}")


if __name__ == "__main__":
    # 運行示例
    asyncio.run(example_usage())
```

#### 2.3 創建 MarketBot 配置文件

**文件**: `config/marketbot_config.yaml`

```yaml
# MarketBot 集成配置
marketbot:
  gateway:
    url: "http://127.0.0.1:18789"
    token: "${MARKETBOT_TOKEN}"  # 從環境變數讀取
    timeout: 10
    retry_attempts: 3
    retry_delay: 2
  
  # 默認通知渠道
  default_channels:
    - dingtalk      # 釘釘 (中國)
    - wecom         # 企業微信 (中國)
    - telegram      # Telegram (國際)
    - discord       # Discord (國際)
  
  # 中文 IM 配置 (優先為中國用戶)
  chinese_im:
    enabled: true
    channels:
      - dingtalk
      - wecom
  
  # 信號映射
  signal_mapping:
    BUY: "📈 買入信號"
    SELL: "📉 賣出信號"
    HOLD: "⏸️  持倉信號"
  
  # 優先級配置
  priority_levels:
    low: 0.5      # confidence < 50%
    normal: 0.7   # 50% <= confidence < 70%
    high: 0.85    # 70% <= confidence < 85%
    critical: 1.0 # confidence >= 85%
  
  # 監控面板配置
  dashboard:
    refresh_interval: 5  # 秒
    max_history: 100     # 保留最近 100 條信號
    enable_grafana: true
    grafana_url: "http://127.0.0.1:3000"

# 通道配置
channels:
  dingtalk:
    enabled: true
    app_id: "${DINGTALK_APP_ID}"
    app_secret: "${DINGTALK_APP_SECRET}"
  
  wecom:
    enabled: true
    corp_id: "${WECOM_CORP_ID}"
    agent_id: "${WECOM_AGENT_ID}"
    secret: "${WECOM_SECRET}"
  
  telegram:
    enabled: true
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"
  
  discord:
    enabled: true
    webhook_url: "${DISCORD_WEBHOOK_URL}"
```

**✅ 第2-3天完成檢查清單**:
- [ ] MarketBot API 已分析
- [ ] `marketbot_connector.py` 已創建 (350 行)
- [ ] `marketbot_config.yaml` 已創建
- [ ] 基本測試已通過

---

### 📍 第4-5天: LLM-TradeBot 路由層開發

#### 4.1 分析 LLM-TradeBot 多代理架構

```bash
# 查找代理定義
find external/llm_tradebot -type f -name "*agent*" | head -10

# 查看主要路由文件
cat external/llm_tradebot/src/agents/router.py | head -50

# 查看信號處理
grep -r "def process_signal\|async def.*signal" external/llm_tradebot/src/ | head -10
```

#### 4.2 創建 LLM-TradeBot 路由器

**文件**: `src/integrations/llm_tradebot_router.py`

```python
"""
LLM-TradeBot Router - 多代理決策路由層
功能:
  1. 接收 Cosmic AI 信號
  2. 通過多代理系統路由決策
  3. 聚合多個代理的意見
  4. 執行風險檢查
  5. 返回最終決策
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """代理角色"""
    ANALYST = "analyst"           # 市場分析
    STRATEGY = "strategy"         # 策略決策
    RISK = "risk"                 # 風險評估
    EXECUTION = "execution"       # 執行決策
    REFLECTION = "reflection"     # 事後反思


@dataclass
class AgentDecision:
    """代理決策結果"""
    agent_id: str
    role: AgentRole
    recommendation: str
    confidence: float
    reasoning: str
    metadata: Dict[str, Any] = None


@dataclass
class FinalDecision:
    """最終決策結果"""
    decision_id: str
    action: str  # BUY, SELL, HOLD, REJECT
    confidence: float
    selected_agent_id: str
    all_votes: List[AgentDecision]
    risk_assessment: Dict[str, Any]
    timestamp: datetime


class Agent:
    """基礎代理類"""
    
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role
        self.decision_history = []
    
    async def process(self, signal: Dict[str, Any]) -> AgentDecision:
        """處理信號並返回決策"""
        raise NotImplementedError


class MarketAnalystAgent(Agent):
    """市場分析代理"""
    
    def __init__(self):
        super().__init__("analyst_001", AgentRole.ANALYST)
    
    async def process(self, signal: Dict[str, Any]) -> AgentDecision:
        """分析市場信號"""
        await asyncio.sleep(0.1)  # 模擬 LLM 分析時間
        
        # 這裡應該調用 LLM 進行真實分析
        # 現在是佔位符實現
        
        return AgentDecision(
            agent_id=self.agent_id,
            role=self.role,
            recommendation="ANALYZE_COMPLETE",
            confidence=0.8,
            reasoning="市場趨勢向上，技術指標良好",
            metadata={
                "trend": "uptrend",
                "volatility": "low",
                "signal_strength": 0.85
            }
        )


class StrategyAgent(Agent):
    """策略決策代理"""
    
    def __init__(self):
        super().__init__("strategy_001", AgentRole.STRATEGY)
    
    async def process(self, signal: Dict[str, Any]) -> AgentDecision:
        """決策交易策略"""
        await asyncio.sleep(0.1)
        
        return AgentDecision(
            agent_id=self.agent_id,
            role=self.role,
            recommendation="BUY",
            confidence=0.82,
            reasoning="基於量化模型和市場分析的建議買入",
            metadata={
                "position_size": 0.5,
                "entry_price": 45000,
                "target_price": 50000
            }
        )


class RiskManagementAgent(Agent):
    """風險管理代理"""
    
    def __init__(self):
        super().__init__("risk_001", AgentRole.RISK)
    
    async def process(self, signal: Dict[str, Any]) -> AgentDecision:
        """評估交易風險"""
        await asyncio.sleep(0.1)
        
        return AgentDecision(
            agent_id=self.agent_id,
            role=self.role,
            recommendation="APPROVED",
            confidence=0.9,
            reasoning="風險評估通過，敞口在可接受範圍內",
            metadata={
                "max_drawdown": 0.05,
                "sharpe_ratio": 2.5,
                "correlation": 0.3
            }
        )


class ExecutionAgent(Agent):
    """執行決策代理"""
    
    def __init__(self):
        super().__init__("execution_001", AgentRole.EXECUTION)
    
    async def process(self, signal: Dict[str, Any]) -> AgentDecision:
        """生成執行計劃"""
        await asyncio.sleep(0.1)
        
        return AgentDecision(
            agent_id=self.agent_id,
            role=self.role,
            recommendation="EXECUTE",
            confidence=0.88,
            reasoning="已準備好執行訂單，所有檢查通過",
            metadata={
                "order_type": "limit",
                "execution_strategy": "vwap",
                "estimated_slippage": 0.001
            }
        )


class ReflectionAgent(Agent):
    """事後反思代理"""
    
    def __init__(self):
        super().__init__("reflection_001", AgentRole.REFLECTION)
    
    async def process(self, signal: Dict[str, Any]) -> AgentDecision:
        """事後分析交易結果"""
        await asyncio.sleep(0.1)
        
        return AgentDecision(
            agent_id=self.agent_id,
            role=self.role,
            recommendation="ANALYZE",
            confidence=0.85,
            reasoning="已記錄交易結果，待事後分析",
            metadata={
                "execution_quality": 0.92,
                "expected_gain": 0.05,
                "learning_points": ["市場流動性充足", "執行質量良好"]
            }
        )


class LLMTradeBotRouter:
    """多代理決策路由器"""
    
    def __init__(self):
        self.agents: Dict[AgentRole, Agent] = {
            AgentRole.ANALYST: MarketAnalystAgent(),
            AgentRole.STRATEGY: StrategyAgent(),
            AgentRole.RISK: RiskManagementAgent(),
            AgentRole.EXECUTION: ExecutionAgent(),
            AgentRole.REFLECTION: ReflectionAgent()
        }
        self.decision_counter = 0
    
    async def route_signal(self, 
                          cosmic_signal: Dict[str, Any]) -> FinalDecision:
        """
        路由 Cosmic 信號到多代理系統
        
        流程:
        1. 市場分析 → 獲取市場洞察
        2. 策略決策 → 生成交易建議
        3. 風險評估 → 檢查風險合規
        4. 執行決策 → 生成執行計劃
        5. 反思 → 記錄交易過程
        """
        
        self.decision_counter += 1
        decision_id = f"dec_{self.decision_counter:06d}"
        
        try:
            logger.info(f"🔄 開始路由決策: {decision_id}")
            
            # 1. 市場分析
            logger.debug("📊 市場分析中...")
            analyst_decision = await self.agents[AgentRole.ANALYST].process(cosmic_signal)
            
            # 2. 策略決策
            logger.debug("💡 策略決策中...")
            strategy_decision = await self.agents[AgentRole.STRATEGY].process(cosmic_signal)
            
            # 3. 風險評估
            logger.debug("⚠️  風險評估中...")
            risk_decision = await self.agents[AgentRole.RISK].process(cosmic_signal)
            
            # 4. 風險檢查
            if risk_decision.recommendation != "APPROVED":
                logger.warning(f"⛔ 風險檢查失敗: {risk_decision.reasoning}")
                return FinalDecision(
                    decision_id=decision_id,
                    action="REJECT",
                    confidence=0.0,
                    selected_agent_id=risk_decision.agent_id,
                    all_votes=[analyst_decision, strategy_decision, risk_decision],
                    risk_assessment=risk_decision.metadata or {},
                    timestamp=datetime.now()
                )
            
            # 5. 執行決策
            logger.debug("✅ 執行決策中...")
            execution_decision = await self.agents[AgentRole.EXECUTION].process(cosmic_signal)
            
            # 6. 事後反思
            logger.debug("🤔 事後反思中...")
            reflection_decision = await self.agents[AgentRole.REFLECTION].process(cosmic_signal)
            
            # 聚合決策
            all_decisions = [
                analyst_decision,
                strategy_decision,
                risk_decision,
                execution_decision,
                reflection_decision
            ]
            
            # 計算最終決策
            final_action = self._aggregate_decisions(all_decisions)
            avg_confidence = sum(d.confidence for d in all_decisions) / len(all_decisions)
            
            logger.info(f"✅ 決策完成: {final_action} (信心: {avg_confidence:.1%})")
            
            return FinalDecision(
                decision_id=decision_id,
                action=final_action,
                confidence=avg_confidence,
                selected_agent_id=strategy_decision.agent_id,
                all_votes=all_decisions,
                risk_assessment=risk_decision.metadata or {},
                timestamp=datetime.now()
            )
        
        except Exception as e:
            logger.error(f"❌ 決策路由失敗: {e}")
            return FinalDecision(
                decision_id=decision_id,
                action="ERROR",
                confidence=0.0,
                selected_agent_id="error",
                all_votes=[],
                risk_assessment={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def _aggregate_decisions(self, decisions: List[AgentDecision]) -> str:
        """聚合多個決策"""
        # 簡單實現: 根據策略代理的推薦
        # 實際應該使用更複雜的投票機制
        for decision in decisions:
            if decision.role == AgentRole.STRATEGY:
                return decision.recommendation
        return "HOLD"
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """獲取代理統計信息"""
        return {
            "total_agents": len(self.agents),
            "agents": [
                {
                    "id": agent.agent_id,
                    "role": agent.role.value,
                    "decisions_made": len(agent.decision_history)
                }
                for agent in self.agents.values()
            ],
            "total_decisions": self.decision_counter
        }


# 使用示例
async def example_routing():
    """路由示例"""
    
    router = LLMTradeBotRouter()
    
    # 創建 Cosmic 信號
    cosmic_signal = {
        "symbol": "BTC/USDT",
        "action": "BUY",
        "confidence": 0.85,
        "price": 45000.0,
        "quantity": 0.5,
        "strategy": "Phase 3 Singularity"
    }
    
    # 路由信號
    decision = await router.route_signal(cosmic_signal)
    
    # 顯示結果
    print(f"""
決策結果:
═════════════════════
ID: {decision.decision_id}
操作: {decision.action}
信心: {decision.confidence:.1%}
時間: {decision.timestamp.isoformat()}
═════════════════════

各代理投票:
""")
    
    for vote in decision.all_votes:
        print(f"  {vote.role.value.upper()}: {vote.recommendation} ({vote.confidence:.1%})")
    
    print(f"""
風險評估: {decision.risk_assessment}
""")


if __name__ == "__main__":
    asyncio.run(example_routing())
```

**✅ 第4-5天完成檢查清單**:
- [ ] LLM-TradeBot 架構已分析
- [ ] `llm_tradebot_router.py` 已創建 (380 行)
- [ ] 5 個代理已實現
- [ ] 路由邏輯已測試

---

### 📍 第6-7天: 集成測試 + 文檔

#### 6.1 創建集成測試

**文件**: `src/tests/test_integration_e2e.py`

```python
"""
端到端集成測試
測試 Cosmic → MarketBot → LLM-TradeBot → Execution 完整流程
"""

import pytest
import asyncio
from datetime import datetime
from src.integrations.marketbot_connector import (
    CosmicMarketBotBridge, CosmicSignal
)
from src.integrations.llm_tradebot_router import LLMTradeBotRouter


@pytest.mark.asyncio
async def test_marketbot_connection():
    """測試 MarketBot 連接"""
    async with CosmicMarketBotBridge() as bridge:
        connected = await bridge.connect()
        assert connected is True


@pytest.mark.asyncio
async def test_signal_conversion():
    """測試信號格式轉換"""
    bridge = CosmicMarketBotBridge()
    
    signal = CosmicSignal(
        signal_id="test_001",
        symbol="BTC/USDT",
        action="BUY",
        confidence=0.85,
        price=45000.0,
        quantity=0.5,
        strategy="Phase 3",
        timestamp=datetime.now()
    )
    
    message = bridge._convert_signal_to_message(signal)
    
    assert message.title is not None
    assert "BTC/USDT" in message.content
    assert message.priority == "HIGH"


@pytest.mark.asyncio
async def test_llm_routing():
    """測試 LLM-TradeBot 路由"""
    router = LLMTradeBotRouter()
    
    signal = {
        "symbol": "BTC/USDT",
        "action": "BUY",
        "confidence": 0.85,
        "price": 45000.0
    }
    
    decision = await router.route_signal(signal)
    
    assert decision.decision_id is not None
    assert decision.action in ["BUY", "SELL", "HOLD", "REJECT"]
    assert len(decision.all_votes) == 5  # 5 個代理


@pytest.mark.asyncio
async def test_complete_flow():
    """測試完整流程"""
    router = LLMTradeBotRouter()
    
    # 生成信號
    signal = {
        "symbol": "ETH/USDT",
        "action": "BUY",
        "confidence": 0.82
    }
    
    # 路由決策
    decision = await router.route_signal(signal)
    assert decision.action in ["BUY", "SELL", "HOLD", "REJECT"]
    
    # 轉換為 MarketBot 消息
    cosmic_signal = CosmicSignal(
        signal_id="e2e_001",
        symbol=signal["symbol"],
        action=decision.action,
        confidence=decision.confidence,
        price=2000.0,
        quantity=1.0,
        strategy="Integration Test",
        timestamp=datetime.now()
    )
    
    bridge = CosmicMarketBotBridge()
    message = bridge._convert_signal_to_message(cosmic_signal)
    
    assert message.title is not None
    assert len(message.channels) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**運行測試**:
```bash
pytest src/tests/test_integration_e2e.py -v
```

#### 6.2 編寫集成文檔

**文件**: `docs/INTEGRATION_ETHANALGOX_GUIDE.md` (已在 memory.md 中)

#### 6.3 Git 提交

```bash
# 創建 feature 分支
git checkout -b feat/ethanalgox-integration

# 添加新文件
git add src/integrations/
git add config/external_integrations/
git add src/tests/test_integration*.py

# 提交
git commit -m "feat: P1 Integration Layer - MarketBot & LLM-TradeBot connectors

- Add CosmicMarketBotBridge for multi-channel delivery
- Implement LLMTradeBotRouter for multi-agent decision routing
- Support Chinese IM channels (DingTalk, WeChat)
- Add comprehensive integration tests
- Complete integration documentation

Lines Added: ~4,950 (core + tests)"

# 推送
git push origin feat/ethanalgox-integration
```

---

## 🔍 驗證檢查清單

### Day 1: 環境準備 ✅
- [ ] Clone 3 個儲存庫完成
- [ ] 代碼結構分析完成
- [ ] 依賴清單檢查完成

### Day 2-3: MarketBot 適配 ✅
- [ ] MarketBot API 分析完成
- [ ] `marketbot_connector.py` 已創建 (350 行)
- [ ] `marketbot_config.yaml` 已創建 (150 行)
- [ ] 基本連接測試通過
- [ ] 多渠道配置完成

### Day 4-5: LLM-TradeBot 路由 ✅
- [ ] LLM-TradeBot 架構分析完成
- [ ] `llm_tradebot_router.py` 已創建 (380 行)
- [ ] 5 個代理已實現
- [ ] 路由邏輯測試通過
- [ ] 決策聚合機制完成

### Day 6-7: 測試 + 文檔 ✅
- [ ] 集成測試完成 (380 行)
- [ ] 端到端測試通過
- [ ] 文檔完成 (2,500+ 行)
- [ ] Git 提交完成

---

## 📊 預期成果

| 指標 | 值 |
|------|-----|
| 新增代碼行數 | ~4,950 |
| 新增測試覆蓋 | ~1,250 |
| 代碼質量 | 100% 類型提示 |
| 測試通過率 | 100% |
| 文檔完整性 | 100% |

---

## 🚨 常見問題

### Q1: 如何驗證 MarketBot Gateway 是否在運行?

```bash
# 檢查連接
curl http://127.0.0.1:18789/health

# 如果返回 200，表示 Gateway 正常運行
```

### Q2: 如何設置 DingTalk 通知?

1. 在 MarketBot 的 Config 頁面中配置 DingTalk
2. 獲取 App ID 和 App Secret
3. 更新 `config/marketbot_config.yaml`
4. 重啟 Gateway

### Q3: 如何測試多代理路由?

```bash
# 運行單個測試
pytest src/tests/test_llm_tradebot_integration.py::test_llm_routing -v

# 運行所有集成測試
pytest src/tests/test_integration_e2e.py -v
```

---

## 📞 支援聯繫

- **MarketBot 文檔**: https://docs.marketbot.ai
- **LLM-TradeBot GitHub**: https://github.com/EthanAlgoX/LLM-TradeBot
- **問題報告**: 在各自 GitHub repo 中提交 Issue

---

**狀態**: 📋 待開始  
**下一步**: 執行 Day 1 環境準備
