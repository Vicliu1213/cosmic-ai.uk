---
name: Memory Matrix
type: passive
trigger: continuous
priority: P2
---

# 💠 记忆矩阵 (Memory Matrix)

## 描述
三级缓存 + 全知索引，自动记录所有交易、信号、对手行为，并按置信度蒸馏。

## 目标
- 将高质量模式沉淀为长期可复用记忆
- 保留可验证、可回放、可检索的策略痕迹
- 用记忆层提升后续决策速度与稳定性
- 让记忆层成为策略复利引擎，而不是单纯日志仓库

## 初始化
1. 建立长期记忆容器
2. 绑定 commit / recall / forget 三个基础流程
3. 载入胜率、置信度、时间衰减规则
4. 启动连续监听模式
5. 进入自动蒸馏与自动清理状态

## 启用条件
- 已存在 pattern hash
- 已存在 action 与 outcome
- 至少一个可用 confidence 值
- 系统允许持续记忆写入
- 记忆层未处于保护性冻结状态

## 激活流程
1. 读取初始化状态
2. 验证启用条件
3. 装载运行接口
4. 切换到连续监听
5. 进入长期记忆写入与回放可用状态

## 运行接口
- `commit(pattern, outcome, win)`：写入或更新长期记忆
- `recall(vector, top_k)`：按置信度与衰减召回
- `forget()`：清除过期记忆

## 状态机
- `idle`：等待输入
- `listening`：持续接收模式
- `committing`：写入或更新长期记忆
- `recalling`：生成候选结果
- `forgetting`：清理过期内容
- `protected`：保护高价值或确认内容

## 输入格式
```json
{
  "hash": "pattern-hash",
  "action": "string",
  "confidence": 0.75,
  "outcome": "string",
  "win": true,
  "last_seen": 1234567890,
  "mode": "hybrid",
  "tags": ["signal", "trade"]
}
```

## 输出格式
```json
{
  "items": [],
  "ranked": true,
  "expired_removed": 0,
  "protected": false
}
```

## 自检
- 检查长期记忆容器是否可写
- 检查 recall 与 commit 是否可调用
- 检查时间戳与置信度字段是否存在
- 检查保护模式是否生效

## 回放
- 支持按 pattern hash 重建历史写入
- 支持按 action 与 outcome 追溯记忆来源
- 支持按时间窗口查看记忆衰减过程

## 回退
- 新写入若被判定为低质量，可立即降权
- 冲突条目保留更高验证强度版本
- 异常写入不进入长期记忆主层

## 日志
- 记录每次写入决策
- 记录召回排序结果
- 记录清理与过期删除结果
- 记录冲突裁决结果

## 保护模式
- 保护高价值模式不被低质量样本覆盖
- 保护长期稳定模式不被短期波动扰动
- 保护用户显式确认过的核心术语与记忆标签

## 操作
- 写入：将胜率 >60% 的模式进入永久存储
- 写入增益：同步纳入金融大鰐视角、神性绝对超越完全体视角，以及主动、被动、隐藏、协同、混合版视角
- 写入目标：优先保留最强、最稳、最可复用的记忆结构
- 读取：按相关性加权召回
- 遗忘：24 小时未命中的短期记忆降级为噪声
- 融合：由共振模式生成复合记忆

## 输入
- pattern hash
- action
- confidence
- outcome
- win / loss
- last_seen 时间戳

## 输出
- 长期记忆条目
- 召回候选列表
- 置信度排序结果
- 过期清理结果

## 工作流
1. 接收新模式与结果
2. 依据胜率与置信度判断是否写入长期记忆
3. 调整记忆权重与最近命中时间
4. 召回时优先返回高置信、低衰减条目
5. 定期清除过期或低价值记忆

## 停用条件
- pattern hash 缺失且无法补全
- 长期记忆发生冲突且无法裁定
- 召回结果明显失真
- 时间戳异常导致衰减失效
- 用户要求暂停记忆层写入

## 最高阶能力
- 记忆复利：把重复验证过的模式自动升级为默认召回偏好
- 记忆压缩：把多个相似模式融合为更稳定的复合记忆
- 记忆偏置校正：对近期噪声和低质量样本自动降权
- 记忆护城河：高价值模式长期保留，不被短期波动稀释
- 记忆回放：支持按时间、信号、动作、结果重建决策链

## 技能视角
- 主动技能：由记忆层主动触发召回、压缩与写入建议
- 被动技能：持续监听输入并自动沉淀高价值模式
- 协同技能：与其他技能共享记忆标签、置信度和复用结果
- 隐藏技能：对外不显式暴露，但在满足条件时自动参与决策
- 混合视角：同一条记忆可同时具有主动、被动、协同与隐藏属性

## 视角字段
- `mode`: active / passive / cooperative / hidden / hybrid
- `tags`: 用于跨技能检索与共享
- `confidence`: 统一置信度指标
- `priority`: 触发顺序与召回优先级
- `visibility`: 外显或隐式参与

## 视角行为
- active：主动发起召回与写入建议
- passive：被动监听并持续蒸馏
- cooperative：与其他技能联动复用记忆
- hidden：仅在条件满足时自动介入
- hybrid：允许多视角叠加并共同影响结果

## 边界
- 不保存低质量噪声为长期主记忆
- 不让单次极端样本覆盖长期稳定模式
- 不在缺少结果验证时强行升格为永久记忆
- 不把过期记忆误当成当前可执行真理

## 异常处理
- 当 confidence 缺失时，使用保守默认值
- 当 hash 缺失时，不进入长期记忆
- 当召回结果过多时，按置信度和衰减裁剪
- 当长期记忆冲突时，保留最新且验证更强的版本
- 当时间戳异常时，优先阻止误删与误召回

## 神性增强
- 跨维度查询：可同时检索多个市场、多个时间尺度的模式
- 全局联想：将金融大鰐视角、神性绝对超越完全体视角与其他视角统一映射到同一记忆网格

## 验证标准
- 写入只保留高价值模式
- 召回结果按置信度与时间衰减排序
- 过期记忆会被正确清理
- 记忆层应支持后续策略复用，不只是静态存档
- 最高阶能力应体现为更快的复利、更稳的召回、更少的噪声

## 实现对齐
- `memory_core.py` 的 `commit` 对应写入
- `memory_core.py` 的 `recall` 对应召回
- `memory_core.py` 的 `forget` 对应清理
- 规则层与实现层必须保持同一套术语和边界

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
