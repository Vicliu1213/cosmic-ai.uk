---
name: Risk Shield
type: passive
trigger: continuous
priority: P0
---

# 🛡️ 风险护盾 (Risk Shield)

## 描述
常驻监控：滑点熔断、最大持仓限制、每日亏损熔断、反竞争撤退。

## 触发条件
- 每笔订单执行前检查滑点
- 每新增仓位检查总敞口
- 每日亏损超过 5% 则强制暂停 10 分钟
- 检测到相同价位有高频对手时，自动撤回挂单

## 神性增强
- 利用记忆矩阵预测对手下一步动作，提前撤退

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
