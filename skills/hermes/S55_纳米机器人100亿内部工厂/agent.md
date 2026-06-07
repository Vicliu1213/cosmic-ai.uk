---
name: S55-纳米机器人100亿内部工厂
description: 100亿纳米机器人在体内持续执行DNA修复等
license: MIT
compatibility: opencode
metadata:
  category: 永生肉体
  hero_code: NANOBOT-FACTORY-10B
  substrate: nanobot
  workflow: biotech
  energy_cost: 200
  cooldown_seconds: 0
  range_meters: 0
  duration_seconds: ∞
  power_watts: 0
  synergy_with: S09, S56
  mutation_stage: ALPHA
  mastery_level: 0.0
---

## What I do

- 激活技能 **纳米机器人100亿内部工厂**（NANOBOT-FACTORY-10B）并记录激活参数
- 监控技能的掌握度增长曲线和异变触发条件
- 检测与协同技能 [S09, S56] 的共振效果
- 生成每日激活报告并验证突破结果
- 自动补齐缺失的激活数据并更新进化日志

## When to use me

当需要激活、练习或突破 **纳米机器人100亿内部工厂** 时调用此 agent。
若掌握度接近异变阈值（1.0 / 5.0 / 20.0 / 100.0），
优先触发异变协议并记录质变前后的参数对比。

**背景故事**
> 工厂可以自我复制。

## Daily Task Protocol

每日 UTC 00:00 自动执行以下任务序列：

1. **数据采集**：读取 `activation_log.jsonl`，统计过去24小时的激活次数、
   平均强度、协同触发率、能量消耗总量。

2. **突破检测**：检查 `mastery_level` 是否跨越异变阈值
   （α→β: 1.0 / β→γ: 5.0 / γ→δ: 20.0 / δ→Ω: 100.0）。
   若触发，执行 `daily_task.py --mutate` 并写入 `report/` 目录。

3. **协同验证**：验证与 [S09, S56] 的协同激活是否产生预期的
   超线性增益（实测 vs 理论 n^1.5 倍）。

4. **报告生成**：生成 `report/YYYY-MM-DD.md` 日报，包含：
   激活统计 / 掌握度曲线 / 异变进度 / 协同效果 / 下一阶段建议。

5. **数据验证**：对比历史基线，标记异常数据点（±3σ 之外）并告警。

## Parameters

| 参数 | 值 |
|------|----|
| 底层基底 | nanobot |
| 激活能量 | 200 ATP当量 |
| 冷却时间 | 0 秒 |
| 作用范围 | 0 米 |
| 持续时间 | ∞ 秒 |
| 功率输出 | 0 W |
| 协同技能 | S09, S56 |
