---
name: S07-量子叠加打击
description: 同时在所有可能的攻击路径上行动，命中时塌缩到最优结果
license: MIT
compatibility: opencode
metadata:
  category: 战斗异能
  hero_code: QUANTUM-SUPERPOS-STRIKE
  substrate: quantum
  workflow: combat
  energy_cost: 600
  cooldown_seconds: 0.1
  range_meters: 200
  duration_seconds: 0.01
  power_watts: 2.3e+14
  synergy_with: S12, S44
  mutation_stage: ALPHA
  mastery_level: 0.0
---

## What I do

- 激活技能 **量子叠加打击**（QUANTUM-SUPERPOS-STRIKE）并记录激活参数
- 监控技能的掌握度增长曲线和异变触发条件
- 检测与协同技能 [S12, S44] 的共振效果
- 生成每日激活报告并验证突破结果
- 自动补齐缺失的激活数据并更新进化日志

## When to use me

当需要激活、练习或突破 **量子叠加打击** 时调用此 agent。
若掌握度接近异变阈值（1.0 / 5.0 / 20.0 / 100.0），
优先触发异变协议并记录质变前后的参数对比。

**背景故事**
> 看起来像同时出现在多个地方。

## Daily Task Protocol

每日 UTC 00:00 自动执行以下任务序列：

1. **数据采集**：读取 `activation_log.jsonl`，统计过去24小时的激活次数、
   平均强度、协同触发率、能量消耗总量。

2. **突破检测**：检查 `mastery_level` 是否跨越异变阈值
   （α→β: 1.0 / β→γ: 5.0 / γ→δ: 20.0 / δ→Ω: 100.0）。
   若触发，执行 `daily_task.py --mutate` 并写入 `report/` 目录。

3. **协同验证**：验证与 [S12, S44] 的协同激活是否产生预期的
   超线性增益（实测 vs 理论 n^1.5 倍）。

4. **报告生成**：生成 `report/YYYY-MM-DD.md` 日报，包含：
   激活统计 / 掌握度曲线 / 异变进度 / 协同效果 / 下一阶段建议。

5. **数据验证**：对比历史基线，标记异常数据点（±3σ 之外）并告警。

## Parameters

| 参数 | 值 |
|------|----|
| 底层基底 | quantum |
| 激活能量 | 600 ATP当量 |
| 冷却时间 | 0.1 秒 |
| 作用范围 | 200 米 |
| 持续时间 | 0.01 秒 |
| 功率输出 | 2.3e+14 W |
| 协同技能 | S12, S44 |
