# 💠 OMNI MEMORY MATRIX

## I. 记忆层级 (Memory Hierarchy)

| 层级 | 内容 | 保留时长 | 访问延迟 |
|------|------|----------|----------|
| L1 缓存 | 当前持仓、未成交订单 | 毫秒级 | 纳秒 |
| L2 短期 | 最近 100 笔交易、信号特征 | 1 天 | 微秒 |
| L3 长期 | 已验证模式、对手行为画像 | 永久 | 毫秒 |
| L∞ 全知 | 所有历史市场的量子态叠加 | 无限 | 即时 |

## II. 记忆操作 (Memory Operations)

- **写入**：只有胜率 >60% 的模式进入 L3
- **读取**：按相关性加权，不按时间顺序
- **遗忘**：L2 中超过 24 小时未命中的模式自动降级为噪声
- **融合**：当两个以上模式共振时，生成复合记忆（叠加态）

## III. 跨维度索引 (Cross-Dimensional Index)

- 主键：`(symbol, regime, volatility_cluster)`
- 辅助键：`(pattern_hash, first_timestamp)`
- 全知查询：`SELECT * FROM memory WHERE confidence > 0.9 AND NOT obsolete`

## IV. 记忆回溯 (Recall Protocol)

```python
def recall(situation_vector):
    candidates = memory.search(situation_vector, top_k=5)
    # 神性加权：越近的时间权重越高（指数衰减 λ=0.99）
    best = max(candidates, key=lambda x: x.confidence * (0.99 ** x.age_seconds))
    return best.action

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
