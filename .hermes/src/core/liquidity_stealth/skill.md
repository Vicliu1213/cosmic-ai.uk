---
name: Liquidity Stealth
type: active
trigger: before_order_placement
priority: P0
---

# 🥷 流动性隐蔽 (Liquidity Stealth)

## 描述
在下单前，将大额订单拆分为冰山订单，并随机化时间间隔，避免被其他高频算法检测。

## 输入
- 原始订单（数量、价格）

## 输出
- 拆分后的子订单列表

## 神性增强
- 根据订单流不平衡动态调整拆分粒度：不平衡越高，拆分越细

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
