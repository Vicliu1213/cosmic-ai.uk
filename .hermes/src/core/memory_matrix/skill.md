---
name: Memory Matrix
type: passive
trigger: continuous
priority: P2
---

# 💠 记忆矩阵 (Memory Matrix)

## 描述
三级缓存 + 全知索引，自动记录所有交易、信号、对手行为，并按置信度蒸馏。

## 操作
- 写入：胜率 >60% 的模式进入永久存储
- 读取：按相关性加权召回
- 遗忘：24小时未命中的短期记忆降级为噪声
- 融合：共振模式生成复合记忆

## 神性增强
- 跨维度查询：可同时检索多个市场、多个时间尺度的模式

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
