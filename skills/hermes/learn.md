# OMEGA ABSOLUTE LEARN PROTOCOL

This file describes the learning loop for bounded recursive enhancement.

## I. 学习源 (Learning Sources)

- **市场微观结构**: 逐笔订单流、挂撤单比、冰山订单识别
- **反脆弱反馈**: 每笔亏损提取 3 条教训，每笔盈利提取 1 条可复制模式
- **对手行为建模**: 高频做市商、掠夺性算法、散户情绪簇

## II. 学习速率 (Learning Rate)

- **初始权重**: 过往经验权重 0.2，新数据权重 0.8
- **遗忘曲线**: 超过 7 天未验证的模式自动衰减 50%
- **突破阈值**: 当新模式的夏普比率 > 2.5 时，立即覆盖旧知识

## III. 知识蒸馏 (Knowledge Distillation)

- 每日 00:00 UTC 执行一次全知场压缩
- 输出格式: `[共振模式] -> [最佳执行参数] -> [预期置信度]`
- 低置信度知识 (<70%) 降级为「噪声参考」

## IV. 自我演化 (Self-Evolution)

- 每 1000 笔交易后，重新评估所有核心公理
- 允许删除或重写低于 50% 胜率的任何规则
- 绝对指令: 永不重复同样的错误超过 3 次
- **核心**: 学习不是积累，是淬炼。无用知识即熵，必须剔除。

## V. Governance Learning Loop

- Observe outcomes.
- Verify improvements.
- Promote only after the verification gate passes.

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
