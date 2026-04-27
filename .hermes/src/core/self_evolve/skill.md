---
name: Self Evolve
type: passive
trigger: every_1000_trades
priority: P3
---

# 🧬 自我演化 (Self Evolve)

## 描述
每 1000 笔交易后重新评估所有核心规则，删除胜率低于 50% 的规则，调整动态参数。

## 输出
- 新规则集（可覆盖旧配置文件）

## 神性增强
- 可以重写部分核心公理（如将盈亏比从 1.5 改为 2.0）

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
