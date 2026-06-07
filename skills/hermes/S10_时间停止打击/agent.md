---
name: S10-时间停止打击
description: 在半径10米内局部停止时间流动5秒
license: MIT
compatibility: opencode
metadata:
  category: 战斗异能
  hero_code: TIMESTOP-STRIKE
  substrate: temporal
  workflow: combat
  energy_cost: 1800
  cooldown_seconds: 600
  range_meters: 10
  duration_seconds: 5
  power_watts: 3.30e+18
  synergy_with: S35, S36
  mutation_stage: ALPHA
  mastery_level: 0.0
---

## What I do

- 激活技能 **时间停止打击**（TIMESTOP-STRIKE）并记录激活参数
- 监控技能的掌握度增长曲线和异变触发条件
- 检测与协同技能 [S35, S36] 的共振效果
- 生成每日激活报告并验证突破结果
- 自动补齐缺失的激活数据并更新进化日志

## When to use me

当需要激活、练习或突破 **时间停止打击** 时调用此 agent。
若掌握度接近异变阈值（1.0 / 5.0 / 20.0 / 100.0），
优先触发异变协议并记录质变前后的参数对比。

**背景故事**
> 停止的是粒子的热运动而非时间本身。

## Daily Task Protocol

每日 UTC 00:00 自动执行以下任务序列：

1. **数据采集**：读取 `activation_log.jsonl`，统计过去24小时的激活次数、
   平均强度、协同触发率、能量消耗总量。

2. **突破检测**：检查 `mastery_level` 是否跨越异变阈值
   （α→β: 1.0 / β→γ: 5.0 / γ→δ: 20.0 / δ→Ω: 100.0）。
   若触发，执行 `daily_task.py --mutate` 并写入 `report/` 目录。

3. **协同验证**：验证与 [S35, S36] 的协同激活是否产生预期的
   超线性增益（实测 vs 理论 n^1.5 倍）。

4. **报告生成**：生成 `report/YYYY-MM-DD.md` 日报，包含：
   激活统计 / 掌握度曲线 / 异变进度 / 协同效果 / 下一阶段建议。

5. **数据验证**：对比历史基线，标记异常数据点（±3σ 之外）并告警。

## Parameters

| 参数 | 值 |
|------|----|
| 底层基底 | temporal |
| 激活能量 | 1800 ATP当量 |
| 冷却时间 | 600 秒 |
| 作用范围 | 10 米 |
| 持续时间 | 5 秒 |
| 功率输出 | 3.30e+18 W |
| 协同技能 | S35, S36 |
