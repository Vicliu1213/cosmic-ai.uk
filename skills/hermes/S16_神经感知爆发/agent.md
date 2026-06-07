---
name: S16-神经感知爆发
description: 感知能力提升至普通人10000倍
license: MIT
compatibility: opencode
metadata:
  category: 战斗异能
  hero_code: NEURAL-SENSE-BURST
  substrate: neural
  workflow: combat
  energy_cost: 150
  cooldown_seconds: 5
  range_meters: 2000
  duration_seconds: 30
  power_watts: 0
  synergy_with: S08, S25
  mutation_stage: ALPHA
  mastery_level: 0.0
---

## What I do

- 激活技能 **神经感知爆发**（NEURAL-SENSE-BURST）并记录激活参数
- 监控技能的掌握度增长曲线和异变触发条件
- 检测与协同技能 [S08, S25] 的共振效果
- 生成每日激活报告并验证突破结果
- 自动补齐缺失的激活数据并更新进化日志

## When to use me

当需要激活、练习或突破 **神经感知爆发** 时调用此 agent。
若掌握度接近异变阈值（1.0 / 5.0 / 20.0 / 100.0），
优先触发异变协议并记录质变前后的参数对比。

**背景故事**
> 副作用是感知过载。

## Daily Task Protocol

每日 UTC 00:00 自动执行以下任务序列：

1. **数据采集**：读取 `activation_log.jsonl`，统计过去24小时的激活次数、
   平均强度、协同触发率、能量消耗总量。

2. **突破检测**：检查 `mastery_level` 是否跨越异变阈值
   （α→β: 1.0 / β→γ: 5.0 / γ→δ: 20.0 / δ→Ω: 100.0）。
   若触发，执行 `daily_task.py --mutate` 并写入 `report/` 目录。

3. **协同验证**：验证与 [S08, S25] 的协同激活是否产生预期的
   超线性增益（实测 vs 理论 n^1.5 倍）。

4. **报告生成**：生成 `report/YYYY-MM-DD.md` 日报，包含：
   激活统计 / 掌握度曲线 / 异变进度 / 协同效果 / 下一阶段建议。

5. **数据验证**：对比历史基线，标记异常数据点（±3σ 之外）并告警。

## Parameters

| 参数 | 值 |
|------|----|
| 底层基底 | neural |
| 激活能量 | 150 ATP当量 |
| 冷却时间 | 5 秒 |
| 作用范围 | 2000 米 |
| 持续时间 | 30 秒 |
| 功率输出 | 0 W |
| 协同技能 | S08, S25 |
