# 🧠 Enhanced Memory & Context System - Agent Memory Architecture

## 簡介 | Introduction

这是 OpenCode 框架的完整記憶和上下文系統，使智能體能夠：
- 💭 記住過去的經驗和決策
- 📚 蒸餾知識成可重用的洞察
- 🎯 維護完整的上下文和情境感知
- 🤝 與其他智能體分享學習成果
- ⚡ 實現持續學習和適應

This is the complete memory and context system for OpenCode framework, enabling agents to:
- Remember past experiences and decisions
- Distill knowledge into reusable insights
- Maintain full context and situational awareness
- Share learning with other agents
- Enable continuous learning and adaptation

---

## 🧭 記憶架構 | Memory Architecture

### 多層次記憶系統 | Multi-Layer Memory System

OpenCode 實現了認知科學中的6層記憶模型：

```
┌─────────────────────────────────────────────────────────┐
│          Agent Cognitive Memory System                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣  SENSORY MEMORY (感知記憶)                         │
│     ├─ Duration: < 1 second                            │
│     ├─ Capacity: Immediate perception                  │
│     └─ Example: Market tick data, price changes       │
│                                                         │
│  2️⃣  SHORT-TERM MEMORY (短期記憶)                     │
│     ├─ Duration: < 30 seconds                          │
│     ├─ Capacity: Working memory (100 items)           │
│     └─ Example: Current analysis, active decisions    │
│                                                         │
│  3️⃣  EPISODIC MEMORY (情景記憶)                       │
│     ├─ Duration: Long-term                            │
│     ├─ Capacity: 1,000 specific experiences           │
│     └─ Example: "On 2026-02-13, bought at 100, profit" │
│                                                         │
│  4️⃣  SEMANTIC MEMORY (語義記憶)                       │
│     ├─ Duration: Permanent                            │
│     ├─ Capacity: Unlimited distilled knowledge        │
│     └─ Example: "RSI < 30 = good buy signal"          │
│                                                         │
│  5️⃣  PROCEDURAL MEMORY (程序性記憶)                   │
│     ├─ Duration: Permanent                            │
│     ├─ Capacity: Learned skills & procedures          │
│     └─ Example: "RSI trading strategy steps"          │
│                                                         │
│  6️⃣  EMOTIONAL MEMORY (情感記憶)                      │
│     ├─ Duration: Adaptive                             │
│     ├─ Capacity: Performance confidence               │
│     └─ Example: High confidence after successful trade│
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 記憶條目結構 | Memory Entry Structure

每個記憶條目包含：

```python
@dataclass
class MemoryEntry:
    entry_id: str                      # 唯一識別碼
    memory_type: MemoryType            # 記憶類型
    timestamp: datetime                # 記錄時間
    content: Dict[str, Any]            # 實際內容
    importance_score: float            # 重要性 (0-1)
    relevance_score: float             # 相關性 (0-1)
    access_count: int                  # 訪問次數
    last_accessed: datetime            # 上次訪問時間
    tags: List[str]                    # 標籤用於搜索
```

**優先級計算 | Priority Calculation:**

```
Priority = Importance × Recency × Relevance × AccessFrequency

- Importance: 記憶的內在價值 (0-1)
- Recency: 時間衰減因子 (最近的記憶優先)
- Relevance: 與當前上下文的相關性 (0-1)
- AccessFrequency: 被使用的次數 (更多使用 = 更高優先級)
```

---

## 🧪 知識蒸餾 | Knowledge Distillation

### 什麼是知識蒸餾？| What is Knowledge Distillation?

知識蒸餾是將大量原始經驗轉化為簡潔、可重用的洞察的過程：

```
原始經驗 (Raw Experiences)
    ↓
    1000+ 個交易記錄、決策、結果
    ↓
知識蒸餾 (Knowledge Distillation)
    ↓
    提取模式、規則、例外情況
    ↓
蒸餾知識 (Distilled Knowledge)
    ↓
    5-10 個可重用的核心洞察
```

### 知識蒸餾流程 | Knowledge Distillation Process

```python
from opencode import EnhancedMemorySystem, KnowledgeType

memory = EnhancedMemorySystem('trading_agent')

# 1. 記錄大量經驗
for i in range(100):
    memory.store_experience({
        'action': 'buy/sell',
        'price': price,
        'success': True/False,
        'profit': amount
    }, tags=['trading', 'rsi_strategy'])

# 2. 蒸餾知識
distilled = memory.distill_knowledge_from_experiences()

# 結果: 從100個經驗中提取出5-10個核心規則
# Example:
# - "When RSI < 30 on 4H chart, buy (72% success rate)"
# - "Hold position for 2-4 hours (average profit 1.5%)"
# - "Close on RSI > 70 (minimize loss risk)"
```

### 蒸餾知識類型 | Types of Distilled Knowledge

```python
class KnowledgeType(Enum):
    STRATEGIC = "strategic"         # 長期策略 ("買入低位股票")
    TACTICAL = "tactical"           # 短期戰術 ("現在下單")
    METACOGNITIVE = "metacognitive" # 學習方法 ("這個模型學習速度快")
    CAUSAL = "causal"              # 因果關係 ("高成交量導致價格上升")
    PATTERN = "pattern"            # 重複模式 ("周一漲幅最大")
    EXCEPTION = "exception"        # 異常情況 ("黑天鵝事件時策略失效")
```

### 蒸餾知識結構 | Distilled Knowledge Structure

```python
class DistilledKnowledge:
    knowledge_type: KnowledgeType           # 知識類型
    confidence: float                       # 信心度 (0-1)
    core_insights: List[str]               # 核心洞察
    supporting_evidence: Dict[str, Any]    # 支持證據
    contradictions: List[str]              # 矛盾/例外
    applicability_conditions: Dict          # 適用條件
    success_rate: float                    # 成功率
    usage_count: int                       # 使用次數
    created_at: datetime                   # 建立時間
    last_validated: datetime               # 上次驗證時間
```

---

## 🎯 上下文管理 | Context Management

### 上下文框架 | Context Frame

每個決策時刻都捕捉完整的上下文框架：

```python
@dataclass
class ContextFrame:
    frame_id: str                   # 唯一識別碼
    timestamp: datetime             # 時間戳
    agent_id: str                   # 智能體ID
    market_state: Dict[str, Any]   # 市場狀況 {price, volume, trend}
    agent_state: Dict[str, Any]    # 智能體狀態 {portfolio, positions}
    recent_decisions: List[str]    # 最近決策
    performance_metrics: Dict       # 性能指標 {ROI, win_rate}
    active_goals: List[str]        # 活躍目標 {maximize_profit}
    constraints: List[str]         # 約束條件 {max_loss_5pct}
    context_hash: str              # 內容哈希用於去重
```

### 上下文檢索 | Context Retrieval

```python
# 查詢相關的過往上下文
similar_contexts = memory.recall_relevant_memories(
    query_context={
        'market_state': current_market,
        'tags': ['rsi_strategy', 'bull_market']
    },
    memory_type=MemoryType.EPISODIC,
    limit=5  # 返回最相關的5個
)

# 結果: 找到類似的過往情景和對應的決策
for context in similar_contexts:
    print(f"Previous similar situation: {context.content}")
    print(f"Decision made: {context.content['decision']}")
    print(f"Result: {context.content['profit']}")
```

---

## 💾 智能體必須記住的事 | What Agents Must Remember

### 1. 核心交易策略 | Core Trading Strategies

**代理必須永遠記住的：**

```python
# 存儲核心策略
memory.store_semantic_knowledge(
    knowledge_type=KnowledgeType.STRATEGIC,
    insights=[
        "Buy when RSI < 30 on 4H timeframe",
        "Sell when RSI > 70",
        "Hold for 2-4 hours for best results",
        "Stop loss at -2%",
        "Take profit at +3%"
    ],
    evidence={
        'historical_data': '2024-2026',
        'success_rate': 0.72,
        'sample_size': 500,
        'avg_profit': '1.8%'
    },
    conditions={
        'market_state': 'trending',
        'volatility': 'moderate',
        'time_frame': '4H'
    }
)
```

### 2. 過去的成功和失敗 | Past Successes and Failures

**記住什麼有效，什麼無效：**

```python
# 成功的交易
memory.store_experience({
    'strategy': 'rsi_4h',
    'entry_price': 100.5,
    'exit_price': 103.2,
    'profit': 2.7,
    'profit_pct': 2.68,
    'duration': '3.5h',
    'market_conditions': 'oversold_recovery',
    'success': True
}, importance=0.95, tags=['success', 'rsi_strategy'])

# 失敗的交易
memory.store_experience({
    'strategy': 'rsi_4h',
    'entry_price': 105.0,
    'exit_price': 102.8,
    'loss': 2.2,
    'loss_pct': 2.10,
    'reason': 'market_crashed_unexpectedly',
    'success': False
}, importance=0.85, tags=['failure', 'rsi_strategy', 'black_swan'])
```

### 3. 市場模式 | Market Patterns

**記住可以預測的市場模式：**

```python
# 周期性模式
memory.store_semantic_knowledge(
    knowledge_type=KnowledgeType.PATTERN,
    insights=[
        "Mondays: +1.2% average",
        "Fridays: -0.8% average",
        "Pre-earnings: High volatility",
        "Fed announcement days: 2-3x volatility"
    ],
    evidence={
        'data_years': 2,
        'observations': 500,
        'confidence': 0.78
    }
)
```

### 4. 風險管理規則 | Risk Management Rules

**永遠要記住的風險規則：**

```python
memory.store_procedural_memory(
    procedure_name='risk_management',
    steps=[
        '1. Check portfolio value',
        '2. Calculate max loss (5% of portfolio)',
        '3. Set stop loss at -2% per position',
        '4. Limit position size to 10% of portfolio',
        '5. Check total exposure across positions',
        '6. Reject trades that violate these rules'
    ],
    success_rate=0.98,
    parameters={
        'max_portfolio_loss': 0.05,
        'max_position_loss': 0.02,
        'max_position_size': 0.10,
        'max_total_exposure': 0.50
    }
)
```

### 5. 性能和信心 | Performance and Confidence

**追蹤績效指標：**

```python
# 更新情感狀態和信心
memory.record_emotional_state('confidence', 0.85)  # 策略表現良好
memory.record_emotional_state('frustration', 0.1)  # 最近沒有太多損失
memory.record_emotional_state('caution', 0.3)      # 保持謹慎

# 結果: 智能體記住它有85%的信心、10%的沮喪、30%的謹慎
# 這會影響它的下一個決策
```

---

## 🔄 記憶操作 | Memory Operations

### 記錄操作 | Recording

```python
from opencode import EnhancedMemorySystem, MemoryType, KnowledgeType

memory = EnhancedMemorySystem('trading_agent')

# 1. 記錄感知輸入
memory.record_sensory_input(
    content={
        'price': 100.5,
        'volume': 1000000,
        'bid_ask_spread': 0.1
    },
    importance=0.8,
    tags=['market_data', 'real_time']
)

# 2. 存儲經驗
memory.store_experience(
    experience={
        'decision': 'buy',
        'reasoning': 'RSI oversold',
        'result': 'profit_2.5%'
    },
    importance=0.9,
    tags=['trading', 'successful']
)

# 3. 存儲知識
memory.store_semantic_knowledge(
    knowledge_type=KnowledgeType.STRATEGIC,
    insights=['High volume + RSI < 30 = strong buy signal'],
    evidence={'success_rate': 0.75}
)

# 4. 存儲程序
memory.store_procedure(
    procedure_name='trade_execution',
    steps=['Check signal', 'Calculate size', 'Place order'],
    success_rate=0.99
)

# 5. 記錄情感狀態
memory.record_emotional_state('confidence', 0.9)
```

### 回憶操作 | Recall

```python
# 查詢相關記憶
relevant_memories = memory.recall_relevant_memories(
    query_context={
        'market_state': {'price': 100.5, 'trend': 'up'},
        'tags': ['rsi_strategy']
    },
    memory_type=MemoryType.EPISODIC,
    limit=10  # 返回最相關的10個
)

for mem in relevant_memories:
    print(f"Memory: {mem.entry_id}")
    print(f"Content: {mem.content}")
    print(f"Relevance: {mem.relevance_score}")
    print(f"Last accessed: {mem.last_accessed}")
```

### 蒸餾操作 | Distillation

```python
# 從經驗中提取知識
distilled = memory.distill_knowledge_from_experiences()

# 結果: 自動識別成功的模式
for knowledge_id, knowledge in distilled.items():
    print(f"Knowledge: {knowledge_id}")
    print(f"Type: {knowledge.knowledge_type.value}")
    print(f"Insights: {knowledge.core_insights}")
    print(f"Confidence: {knowledge.confidence}")
    print(f"Success rate: {knowledge.success_rate}")
```

### 上下文更新 | Context Update

```python
# 更新當前上下文
memory.update_context(
    market_state={
        'price': 101.5,
        'volume': 1200000,
        'trend': 'bullish'
    },
    agent_state={
        'portfolio_value': 10000,
        'positions': 1,
        'cash': 5000
    },
    active_goals=['maximize_profit', 'minimize_drawdown'],
    constraints=['max_loss_5%', 'max_position_10%']
)
```

---

## 🔗 多智能體知識共享 | Multi-Agent Knowledge Sharing

### 知識共享框架 | Knowledge Sharing Framework

```python
from opencode import AgentMemoryManager

# 創建記憶管理器
manager = AgentMemoryManager()

# 為每個智能體註冊記憶系統
trader_mem = manager.register_agent('trader_agent')
analyst_mem = manager.register_agent('analyst_agent')
monitor_mem = manager.register_agent('monitor_agent')

# 分享知識
manager.share_knowledge(
    source_agent='analyst_agent',
    knowledge_id='knowledge_pattern_0',  # 分析師發現的模式
    target_agents=['trader_agent', 'monitor_agent']  # 分享給交易者和監控者
)

# 結果: 所有智能體都可以使用分析師發現的模式
```

### 知識圖譜 | Knowledge Graph

```
分析師 (Analyst)
    │
    └─> 發現模式: "周一漲幅最大"
         │
         ├─> 交易者 (Trader) 使用這個模式下單
         ├─> 監控者 (Monitor) 追蹤準確度
         └─> 風險管理者 (Risk Manager) 調整風險參數
```

---

## 📊 記憶統計和監控 | Memory Statistics & Monitoring

### 獲取記憶統計 | Get Memory Stats

```python
stats = memory.get_memory_stats()

print(stats)
# Output:
# {
#     'agent_id': 'trading_agent',
#     'total_experiences': 150,
#     'total_decisions': 42,
#     'episodic_count': 98,
#     'semantic_count': 15,
#     'procedural_count': 8,
#     'context_frames': 200,
#     'sensory_buffer_size': 45,
#     'emotional_states': {
#         'confidence': 0.85,
#         'frustration': 0.1,
#         'caution': 0.3
#     },
#     'uptime_seconds': 3600.5
# }
```

### 系統級統計 | System-level Stats

```python
system_stats = manager.get_system_stats()

# 查看所有智能體的記憶統計
for agent_id, agent_stats in system_stats['agents'].items():
    print(f"Agent: {agent_id}")
    print(f"  Experiences: {agent_stats['total_experiences']}")
    print(f"  Knowledge items: {agent_stats['semantic_count']}")
    print(f"  Procedures: {agent_stats['procedural_count']}")
```

---

## 💾 記憶持久化 | Memory Persistence

### 導出記憶 | Export Memories

```python
# 導出關鍵記憶以保存或備份
exported = memory.export_critical_memories()

# 結果包含:
# - 前10個最優先的經驗
# - 所有蒸餾知識
# - 所有程序
# - 當前情感狀態

# 保存為JSON
import json
with open('agent_memories.json', 'w') as f:
    json.dump(exported, f, indent=2, default=str)
```

### 導入記憶 | Import Memories

```python
# 新智能體可以導入經驗
new_agent = EnhancedMemorySystem('new_trading_agent')

# 導入先前保存的記憶
with open('agent_memories.json', 'r') as f:
    imported_data = json.load(f)

new_agent.import_memories(imported_data)

# 結果: 新智能體立即獲得過去智能體的150+ 經驗
```

---

## 🧠 記憶遺忘和衰減 | Memory Decay

### 知識衰減機制 | Knowledge Decay Mechanism

記憶並非永久存儲。系統實施衰減機制以優化存儲：

```python
# 衰減因子計算
Priority = Importance × Recency × Relevance × AccessFrequency

# 隨著時間推移，衰減因子：
Recency factor = max(0.1, 1.0 - (days_elapsed / 30))

# 示例:
# - 1天前: 0.97 (幾乎沒有衰減)
# - 7天前: 0.77 (23% 衰減)
# - 30天前: 0.10 (90% 衰減，但保持10%以備查詢)

# 低優先級記憶自動刪除以釋放空間
if memory_size > max_episodic:
    lowest_priority_memories = sorted by priority
    delete lowest_priority_memories
```

### 情感衰減 | Emotional Decay

```python
# 情感狀態自然衰減到中性
knowledge_decay_rate = 0.001  # 每次調用衰減 0.1%

# 情感衰減示例:
current_confidence = 0.9
days_passed = 7
final_confidence = 0.9 * ((1 - 0.001) ** (7 * 24 * 3600))
# result ≈ 0.9 * 0.97 ≈ 0.87 (經過7天後略微衰減)
```

---

## 🎓 最佳實踐 | Best Practices

### 1. 定期蒸餾知識 | Regularly Distill Knowledge

```python
# 每100次經驗後蒸餾一次
if memory.total_experiences % 100 == 0:
    distilled = memory.distill_knowledge_from_experiences()
    logger.info(f"Distilled {len(distilled)} knowledge items")
```

### 2. 標籤化記憶 | Tag Memories

```python
# 使用有意義的標籤便於查詢
memory.store_experience(
    experience={...},
    tags=['rsi_strategy', 'bull_market', '4h_timeframe', 'successful']
)
```

### 3. 定期備份 | Regular Backups

```python
# 每小時備份關鍵記憶
import time
last_backup = time.time()

if time.time() - last_backup > 3600:
    exported = memory.export_critical_memories()
    backup_file = f"backups/agent_{memory.agent_id}_{time.time()}.json"
    with open(backup_file, 'w') as f:
        json.dump(exported, f)
    last_backup = time.time()
```

### 4. 監控記憶健康 | Monitor Memory Health

```python
# 定期檢查記憶系統的狀態
stats = memory.get_memory_stats()

if stats['episodic_count'] > stats['max_episodic'] * 0.9:
    logger.warning("Memory approaching capacity limit")

if stats['semantic_count'] < 5:
    logger.warning("Low semantic knowledge - need more distillation")
```

---

## 🔮 高級功能 | Advanced Features

### 記憶融合 | Memory Fusion

```python
# 合併多個智能體的記憶以創建超級記憶
agents = [trader_agent, analyst_agent, monitor_agent]
all_experiences = []

for agent in agents:
    memories = agent.export_critical_memories()
    all_experiences.extend(memories['critical_experiences'])

# 創建融合記憶
fused_memory = EnhancedMemorySystem('fused_super_agent')
for exp in all_experiences:
    fused_memory.store_experience(exp)

# 結果: 超級智能體具有所有三個智能體的經驗
```

### 記憶搜索 | Memory Search

```python
# 高級搜索功能
relevant = memory.recall_relevant_memories(
    query_context={
        'market_state': {'price': 100, 'volume': 'high'},
        'tags': ['rsi_strategy', 'volatile_market']
    },
    memory_type=MemoryType.EPISODIC,
    limit=20
)

# 按不同標準排序
by_profit = sorted(relevant, key=lambda m: m.content.get('profit', 0), reverse=True)
by_recency = sorted(relevant, key=lambda m: m.timestamp, reverse=True)
by_relevance = sorted(relevant, key=lambda m: m.relevance_score, reverse=True)
```

---

## 📈 記憶指標 | Memory Metrics

### 關鍵性能指標 (KPIs)

| 指標 | 定義 | 目標 |
|-----|------|------|
| **知識蒸餾率** | 蒸餾知識/總經驗 | > 1% |
| **記憶召回準確度** | 相關記憶/查詢 × 100 | > 80% |
| **知識有效期** | 使用知識的成功率 | > 70% |
| **記憶利用率** | 被訪問的記憶/總記憶 | > 30% |
| **情感穩定性** | 1 - 情感波動 | > 0.8 |
| **上下文匹配準確度** | 正確識別的相似上下文 | > 85% |

---

## 🐛 除錯記憶 | Debugging Memory

### 記憶檢查清單 | Memory Checklist

```python
def check_memory_health(memory: EnhancedMemorySystem):
    stats = memory.get_memory_stats()
    
    # 檢查點
    checks = {
        '✓ Episodic memories within limit': 
            stats['episodic_count'] <= stats.get('max_episodic', 1000),
        '✓ Semantic knowledge populated': 
            stats['semantic_count'] > 0,
        '✓ Procedures defined': 
            stats['procedural_count'] > 0,
        '✓ Emotional state balanced': 
            all(0 <= v <= 1 for v in stats['emotional_states'].values()),
        '✓ Context history reasonable': 
            stats['context_frames'] > 0,
        '✓ No memory bloat': 
            stats['sensory_buffer_size'] < 100,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
    
    return all(checks.values())
```

---

## 📚 完整使用示例 | Complete Usage Example

```python
from opencode import EnhancedMemorySystem, MemoryType, KnowledgeType
import json

# 1. 創建記憶系統
memory = EnhancedMemorySystem('professional_trading_agent')

# 2. 記錄市場數據
for tick in market_data:
    memory.record_sensory_input(
        {'price': tick['price'], 'volume': tick['volume']},
        tags=['market_tick']
    )

# 3. 執行交易並記錄
trade = {
    'entry_price': 100.5,
    'exit_price': 103.2,
    'profit': 2.7,
    'strategy': 'rsi_4h',
    'success': True,
    'market_conditions': 'oversold_recovery'
}
memory.store_experience(trade, importance=0.9, tags=['trading', 'successful'])

# 4. 提取和蒸餾知識
distilled = memory.distill_knowledge_from_experiences()

# 5. 更新上下文
memory.update_context(
    market_state={'price': 103.2, 'trend': 'up'},
    agent_state={'portfolio': 10500},
    active_goals=['maximize_profit'],
    constraints=['max_loss_5%']
)

# 6. 回憶相關記憶
relevant = memory.recall_relevant_memories(
    query_context={'tags': ['rsi_strategy']},
    limit=5
)

# 7. 獲取統計和備份
stats = memory.get_memory_stats()
backup = memory.export_critical_memories()

with open('agent_backup.json', 'w') as f:
    json.dump(backup, f, default=str)

print(f"Agent has {stats['total_experiences']} experiences")
print(f"Distilled {len(distilled)} knowledge items")
print(f"Currently confident: {stats['emotional_states']['confidence']}")
```

---

## 🚀 集成到 OpenCode | Integration with OpenCode

```python
from opencode import (
    create_framework, 
    create_orchestrator,
    BioInspiredAgentEnhancer
)
from opencode.agent_memory import (
    EnhancedMemorySystem,
    AgentMemoryManager,
    KnowledgeType
)

# 創建框架
framework = create_framework()
orchestrator = create_orchestrator(framework)

# 為每個智能體創建記憶系統
memory_manager = AgentMemoryManager()

for agent_id in ['trading_agent', 'analyst_agent', 'monitor_agent']:
    agent_memory = memory_manager.register_agent(agent_id)
    agent_memory.store_procedure(
        'decision_making',
        ['Check memory', 'Recall similar situations', 'Make decision'],
        success_rate=0.95
    )

# 結果: 每個智能體都有完整的記憶和上下文能力!
```

---

## 📖 更多資源 | Additional Resources

- **記憶科學**: https://en.wikipedia.org/wiki/Multi-store_model_of_memory
- **知識蒸餾**: https://en.wikipedia.org/wiki/Knowledge_distillation
- **上下文感知**: https://en.wikipedia.org/wiki/Context_awareness
- **多智能體系統**: https://en.wikipedia.org/wiki/Multi-agent_system

---

## 📝 版本歷史 | Version History

### v1.0.0 (2026-02-13)
- ✅ 6層記憶系統完成
- ✅ 知識蒸餾引擎完成
- ✅ 上下文管理完成
- ✅ 多智能體知識共享完成
- ✅ 記憶持久化完成

---

## 🏆 總結 | Summary

這個增強版的記憶系統為 OpenCode 中的智能體提供了：

✨ **完整的認知架構** - 6層記憶系統模擬人類大腦
🧪 **智能知識蒸餾** - 自動從經驗中提取可重用的洞察
🎯 **豐富的上下文感知** - 維護完整的情景和決策上下文
🤝 **多智能體協作** - 智能體可以相互學習和分享知識
💾 **持久記憶** - 記憶可以保存、加載和共享
⚡ **自適應學習** - 知識會根據使用情況自動驗證和改進

**每個智能體都記住:**
1. 過去的決策和結果
2. 有效的策略和規則
3. 市場模式和例外
4. 風險管理約束
5. 性能指標和信心

**結果**: 智能體變得更聰明、更適應、更有效！🚀

---

**Status**: 完全集成到 OpenCode 框架 ✅
**Production Ready**: 是 ✅
**Bilingual**: English + 中文 ✅
