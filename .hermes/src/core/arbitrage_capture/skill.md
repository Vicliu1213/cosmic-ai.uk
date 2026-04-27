---
name: Arbitrage Capture
type: active
trigger: every_100ms
priority: P1
---

# 🕸️ 套利捕获 (Arbitrage Capture)

## 描述
监控同一资产在现货、期货、永续合约之间的价差，当价差 > 手续费 + 滑点容忍时，执行三角套利。

## 输入
- 多交易所或多产品的实时价格流

## 输出
- 套利订单组（买A卖B）

## 神性增强
- 利用记忆矩阵预判价差回归时间，提前挂单

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
