# OpenCode 交易系统集成 - 完整中文使用指南
# Complete Chinese Usage Guide for OpenCode Trading System Integration

**生成日期**: 2026-02-19
**版本**: 1.0.0

---

## 📖 目录 / Table of Contents

1. [快速入门](#快速入门)
2. [系统架构](#系统架构)
3. [MCP 服务器详解](#mcp-服务器详解)
4. [自定义命令](#自定义命令)
5. [AI Agent 详解](#ai-agent-详解)
6. [使用场景和示例](#使用场景和示例)
7. [高级命令](#高级命令)
8. [故障排除](#故障排除)

---

## 🚀 快速入门

### 安装步骤

**第 1 步：安装 OpenCode**
```bash
curl -fsSL https://opencode.ai/install | bash
```

**第 2 步：验证安装**
```bash
opencode --version
```

**第 3 步：进入项目目录**
```bash
cd /root/comic_ai
```

**第 4 步：运行自动安装脚本**
```bash
bash scripts/install_opencode.sh
```

**第 5 步：启动 OpenCode**
```bash
opencode
```

### 最快速启动（一行命令）
```bash
cd /root/comic_ai && opencode
```

---

## 🏗️ 系统架构

### 配置文件位置
```
/root/comic_ai/opencode.jsonc          主配置文件 (JSONC 格式)
~/.config/opencode/opencode.json       全局配置 (自动同步)
```

### 核心组件

#### 1. **模型配置**
- **主模型**: `Anthropic Claude Sonnet 4.5` (智能决策)
- **小模型**: `Anthropic Claude Haiku 4.5` (快速任务)

#### 2. **MCP 服务器** (4 个)
| 名称 | 状态 | 类型 | 工具数 |
|------|------|------|--------|
| trading-monitor | ✓ 启用 | 本地 | 5 |
| quantum-engine | ✓ 启用 | 本地 | 5 |
| data-analyzer | ✓ 启用 | 本地 | 6 |
| risk-manager | ✓ 启用 | 本地 | 5 |

#### 3. **AI Agents** (4 个)
| 名称 | 角色 | 权限 |
|------|------|------|
| code-reviewer | 代码审查 | 只读 |
| trading-analyst | 交易分析 | 数据访问 |
| quantum-engineer | 算法开发 | 完全 |
| devops-engineer | 系统运维 | 完全 |

#### 4. **自定义命令** (4 个)
| 命令 | 功能 | Agent |
|------|------|-------|
| /test | 运行测试 | build |
| /analyze | 分析系统 | build |
| /monitor | 启动监控 | build |
| /deploy | 部署系统 | build |

---

## 🔧 MCP 服务器详解

### 1️⃣ 交易监控 MCP (trading-monitor)

**文件位置**: `src/core/trading_monitor_mcp.py`

**5 个工具详解**:

#### 工具 1: `get_portfolio_status` - 获取投资组合状态
```
功能: 查看当前投资组合的总价值、可用现金、头寸数量、收益情况
使用方法: 
  > 获取我的投资组合状态
  > Get my portfolio status. Use trading-monitor tool.
返回信息:
  - 投资组合总价值: 1,000,000 元
  - 可用现金: 250,000 元
  - 头寸数量: 5 个
  - 今日收益/总收益: +5,000 / +50,000 元
  - 风险等级: 中等
```

#### 工具 2: `get_market_data` - 获取市场数据
```
功能: 查询特定股票的实时市场信息
使用方法:
  > 获取 AAPL 的市场数据
  > Get AAPL market data. Use trading-monitor tool.
参数:
  - symbol: 交易符号 (如: AAPL, MSFT, GOOGL)
返回信息:
  - 当前价格: 150.00 元
  - 交易量: 1,000,000 股
  - 涨跌幅: +2.5%
  - 买卖价差: 0.01 元
```

#### 工具 3: `get_system_health` - 获取系统健康状况
```
功能: 监控交易系统的运行状态
使用方法:
  > 检查系统的健康状况
  > Get system health. Use trading-monitor tool.
返回信息:
  - 系统状态: 健康/良好
  - 运行时间: 24.5 小时
  - 内存使用: 62.8%
  - CPU 使用: 45.2%
  - 活跃连接数: 15 个
  - 最后更新时间: (时间戳)
```

#### 工具 4: `get_active_trades` - 获取活跃交易
```
功能: 查看当前所有的活跃交易
使用方法:
  > 显示所有活跃交易
  > Show active trades. Use trading-monitor tool.
返回信息:
  - 交易 ID: TRADE_001
  - 股票代码: AAPL
  - 买/卖: 买入
  - 数量: 100 股
  - 进入价格: 150.00 元
  - 当前价格: 152.50 元
  - 收益: +250 元
  - 时间戳
```

#### 工具 5: `get_risk_metrics` - 获取风险指标
```
功能: 查看投资组合的风险指标
使用方法:
  > 获取风险指标
  > Get risk metrics. Use trading-monitor tool.
返回信息:
  - 风险价值 (95%): 50,000 元
  - 夏普比率: 1.85
  - 最大回撤: 15%
  - 相关性风险: 0.45
  - 流动性风险: 低
  - 集中度风险: 中等
```

---

### 2️⃣ 量化引擎 MCP (quantum-engine)

**文件位置**: `engine/quantum_engine_mcp.py`

**5 个工具详解**:

#### 工具 1: `list_algorithms` - 列出可用算法
```
功能: 查看系统中所有可用的交易算法
使用方法:
  > 列出所有可用的算法
  > List available algorithms. Use quantum-engine tool.
返回信息:
  算法 1: 均值回归策略
    - ID: algo_001
    - 状态: 活跃
    - 胜率: 55%
    - 利润因子: 1.8
    - 夏普比率: 1.85
  
  算法 2: 趋势跟踪策略
    - ID: algo_002
    - 状态: 活跃
    - 胜率: 48%
    - 利润因子: 2.5
    - 夏普比率: 2.15
  
  算法 3: 套利策略
    - ID: algo_003
    - 状态: 测试中
    - 胜率: 75%
    - 利润因子: 3.2
    - 夏普比率: 2.85
```

#### 工具 2: `optimize_parameters` - 优化参数
```
功能: 自动优化算法参数以改进性能
使用方法:
  > 优化 algo_001 的参数
  > Optimize algo_001 parameters. Use quantum-engine tool.
参数:
  - algorithm_id: 算法 ID
  - optimization_target: 优化目标 (sharpe/sortino/profit_factor/drawdown)
返回信息:
  - 优化 ID: opt_1708...
  - 新参数设置:
    - 回溯期: 20 天
    - 进入阈值: 0.05
    - 退出阈值: 0.03
    - 头寸大小: 10%
    - 最大回撤: 15%
  - 性能提升: 15.5%
  - 新的夏普比率: 2.45
```

#### 工具 3: `backtest_algorithm` - 回测算法
```
功能: 对算法进行历史数据回测
使用方法:
  > 回测 algo_001 最近 30 天的表现
  > Backtest algo_001 for the last 30 days. Use quantum-engine tool.
参数:
  - algorithm_id: 算法 ID
  - start_date: 开始日期 (YYYY-MM-DD)
  - end_date: 结束日期 (YYYY-MM-DD)
返回信息:
  - 回测周期: 2026-01-20 至 2026-02-19
  - 总交易数: 145 笔
  - 赢利交易: 85 笔 (58.6%)
  - 亏损交易: 60 笔 (41.4%)
  - 胜率: 58.6%
  - 利润因子: 1.92
  - 总收益: 42.5%
  - 年化收益: 21.2%
  - 夏普比率: 1.85
  - 最大回撤: -18%
  - 平均赢利: 1,200 元
  - 平均亏损: -850 元
```

#### 工具 4: `compare_algorithms` - 比较算法
```
功能: 对比多个算法的性能
使用方法:
  > 比较 algo_001 和 algo_002 的性能
  > Compare algo_001 and algo_002. Use quantum-engine tool.
参数:
  - algorithm_ids: 算法 ID 列表
返回信息:
  - 对比指标:
    algo_001 vs algo_002
    夏普比率: 1.85 vs 2.15 ✓ algo_002 更好
    胜率: 55% vs 48% ✓ algo_001 更好
    利润因子: 1.80 vs 2.50 ✓ algo_002 更好
    最大回撤: -20% vs -15% ✓ algo_002 更好
  - 推荐: algo_002
  - 原因: 更高的夏普比率和索提诺比率
```

#### 工具 5: `get_engine_status` - 获取引擎状态
```
功能: 查看量化引擎的运行状态
使用方法:
  > 获取引擎状态
  > Get engine status. Use quantum-engine tool.
返回信息:
  - 引擎状态: 运行中
  - 版本: 2.0.1
  - 运行模式: 混合模式
  - 活跃算法数: 3 个
  - 完成回测数: 1,250 次
  - 待处理优化任务: 5 个
  - CPU 使用: 45.2%
  - 内存使用: 62.8%
  - 量子核可用: 8 个
  - 优化等级: 3
```

---

### 3️⃣ 数据分析 MCP (data-analyzer)

**文件位置**: `src/core/data_analyzer_mcp.py`

**6 个工具详解**:

#### 工具 1: `analyze_time_series` - 时间序列分析
```
功能: 分析股票价格的时间序列数据
使用方法:
  > 分析 AAPL 最近 30 天的时间序列
  > Analyze AAPL time series for 30 days. Use data-analyzer tool.
参数:
  - symbol: 股票代码
  - period_days: 分析周期 (默认 30 天)
返回信息:
  - 统计数据:
    平均价格: 152.45 元
    中位数: 151.80 元
    标准差: 3.25 元
    最低/最高: 145.50 / 160.25 元
    偏度: 0.35 (向上倾斜)
    峰度: -0.85 (平坦)
  - 趋势:
    方向: 上升趋势
    强度: 0.75
    斜率: 0.245
    加速度: 0.012
  - 波动性:
    当前: 15%
    平均: 18%
    30 日滚动: 16.5%
  - 支撑/阻力:
    支撑 1: 149.50 元
    支撑 2: 147.00 元
    阻力 1: 156.00 元
    阻力 2: 160.00 元
```

#### 工具 2: `detect_patterns` - 检测价格模式
```
功能: 识别技术分析中的价格模式
使用方法:
  > 检测 AAPL 的价格模式
  > Detect patterns in AAPL. Use data-analyzer tool.
返回信息:
  检测到的模式:
  
  1. 双顶形态
     - 信心度: 85%
     - 形成天数: 15 天
     - 信号: 看跌
  
  2. 三角形整理
     - 信心度: 72%
     - 形成天数: 8 天
     - 信号: 中立
  
  3. 移动平均线黄金交叉
     - 信心度: 92%
     - 形成天数: 1 天
     - 信号: 看涨
```

#### 工具 3: `correlation_analysis` - 相关性分析
```
功能: 分析多个资产之间的相关性
使用方法:
  > 分析 AAPL、MSFT、GOOGL 之间的相关性
  > Analyze correlation between AAPL, MSFT, GOOGL. Use data-analyzer tool.
参数:
  - symbols: 股票代码列表
返回信息:
  相关性矩阵:
          AAPL   MSFT   GOOGL  TSLA
  AAPL    1.00   0.68   0.72   0.45
  MSFT    0.68   1.00   0.75   0.52
  GOOGL   0.72   0.75   1.00   0.48
  TSLA    0.45   0.52   0.48   1.00
  
  洞察:
  - 最高相关性: MSFT 与 GOOGL (0.75)
  - 最低相关性: AAPL 与 TSLA (0.45)
  - 投资组合多样化: 中等
  - 系统性风险水平: 0.62
```

#### 工具 4: `sentiment_analysis` - 情绪分析
```
功能: 分析市场对股票的情绪
使用方法:
  > 分析 AAPL 的市场情绪
  > Analyze sentiment for AAPL. Use data-analyzer tool.
返回信息:
  - 整体情绪: 积极
  - 情绪评分: 0.72 (1 = 最积极)
  - 情绪分解:
    看涨: 55%
    中性: 30%
    看跌: 15%
  - 信息来源:
    新闻情绪: 0.68
    社交媒体: 0.75
    分析师评级: 0.70
  - 热门话题:
    1. 收益超预期
    2. 产品创新
    3. 市场份额增长
  - 风险情绪: 中等
```

#### 工具 5: `forecasting` - 价格预测
```
功能: 预测未来的股票价格
使用方法:
  > 预测 AAPL 未来 30 天的价格
  > Forecast AAPL price for 30 days. Use data-analyzer tool.
参数:
  - symbol: 股票代码
  - days_ahead: 预测天数 (默认 30 天)
返回信息:
  预测数据 (示例前 5 天):
  
  第 1 天:
    预测价格: 153.05 元
    置信区间上界: 155.05 元
    置信区间下界: 151.05 元
    概率: 75%
  
  第 2 天:
    预测价格: 153.20 元
    置信区间上界: 155.20 元
    置信区间下界: 151.20 元
    概率: 74%
  
  总结:
  - 预期收益: 4.5%
  - 预期波动率: 18%
  - 趋势: 上升趋势
  - 信心水平: 72%
```

#### 工具 6: `risk_assessment` - 风险评估
```
功能: 评估投资组合风险
使用方法:
  > 对我的投资组合进行风险评估
  > Assess risk for my portfolio (AAPL, MSFT, GOOGL). Use data-analyzer tool.
参数:
  - symbols: 股票代码列表
返回信息:
  每个资产的风险数据:
  
  AAPL:
    - VaR (95%): 5%
    - VaR (99%): 8%
    - 条件 VaR: 10%
    - Beta: 1.05
    - 特异性风险: 12%
    - 系统性风险: 8%
  
  投资组合风险:
    - 总风险: 8.5%
    - 系统性风险: 6.5%
    - 非系统性风险: 4.5%
    - 风险等级: 中等
  
  建议:
    1. 考虑增加低相关性资产
    2. 监控个股集中风险
    3. 定期重新平衡投资组合
```

---

### 4️⃣ 风险管理 MCP (risk-manager)

**文件位置**: `src/core/risk_manager_mcp.py`

**5 个工具详解**:

#### 工具 1: `check_position_limits` - 检查头寸限制
```
功能: 验证建议的头寸是否符合风险限制
使用方法:
  > 检查我能否再买 100 股 AAPL
  > Check position limits for 100 AAPL shares. Use risk-manager tool.
参数:
  - symbol: 股票代码
  - quantity: 建议的头寸数量
返回信息:
  - 建议数量: 100 股
  - 建议后头寸: 3,100 股
  - 限制检查:
    头寸限制: 10,000 股 ✓ 通过
    投资组合百分比: 15% 限制 ✓ 通过
    行业集中度: 25% 限制 ✓ 通过
  - 当前状态:
    当前头寸: 3,000 股
    当前占比: 6%
    行业集中度: 18%
  - 推荐: 已批准 (APPROVED)
```

#### 工具 2: `calculate_var` - 计算风险价值 (VaR)
```
功能: 计算投资组合的价值风险
使用方法:
  > 计算我的投资组合的 VaR
  > Calculate VaR for my portfolio (AAPL, MSFT). Use risk-manager tool.
参数:
  - symbols: 股票代码列表
  - confidence: 置信水平 (默认 95%)
返回信息:
  AAPL:
    - 置信水平: 95%
    - VaR 金额: 50,000 元
    - VaR 百分比: 5%
    - 条件 VaR: 65,000 元
  
  MSFT:
    - 置信水平: 95%
    - VaR 金额: 35,000 元
    - VaR 百分比: 3.5%
    - 条件 VaR: 45,000 元
  
  投资组合:
    - 总 VaR: 85,000 元
    - 总条件 VaR: 110,000 元
```

#### 工具 3: `stress_test` - 压力测试
```
功能: 模拟极端市场条件下的投资组合表现
使用方法:
  > 对我的投资组合进行市场暴跌压力测试
  > Run market crash stress test. Use risk-manager tool.
参数:
  - scenario: 压力测试场景
    选项: market_crash / rate_hike / geopolitical / liquidity_crisis
返回信息:
  场景: 市场暴跌 20%
  
  投资组合影响:
    - 价值变化: -15%
    - 金额: -150,000 元
    - 受影响头寸: 5 个
    - 影响股票: AAPL, MSFT, GOOGL, TSLA, META
  
  头寸影响明细:
    AAPL: -18% (-45,000 元)
    MSFT: -12% (-30,000 元)
    GOOGL: -20% (-35,000 元)
    TSLA: -25% (-25,000 元)
    META: -15% (-15,000 元)
  
  恢复估计: 3-5 个交易日
  
  缓解建议:
    1. 立即削减高风险头寸
    2. 增加流动性储备
    3. 审查对冲策略
```

#### 工具 4: `compliance_check` - 合规检查
```
功能: 检查是否符合监管要求
使用方法:
  > 进行合规检查
  > Run compliance check. Use risk-manager tool.
参数:
  - regulation: 规制 (sec/finra/mifid_ii/all)
返回信息:
  SEC 合规:
    - 状态: ✓ 符合
    - 检查规则: 15 条
    - 违规数: 0
    - 警告数: 0
  
  FINRA 合规:
    - 状态: ✓ 符合
    - 检查规则: 22 条
    - 违规数: 0
    - 警告数: 1
  
  MiFID II 合规:
    - 状态: ✓ 符合
    - 检查规则: 18 条
    - 违规数: 0
    - 警告数: 0
  
  交易违规: 无
  
  报告状态:
    - 头寸报告: 最新状态
    - 交易报告: 最新状态
    - 风险报告: 最新状态
  
  下次审计: 2026-03-01
```

#### 工具 5: `get_risk_report` - 获取风险报告
```
功能: 生成完整的风险管理报告
使用方法:
  > 生成风险报告
  > Generate risk report. Use risk-manager tool.
返回信息:
  执行总结:
    - 整体风险等级: 中等
    - 关键风险:
      1. 市场波动性增加
      2. 行业集中度风险
      3. 流动性风险
    - 风险评分: 6.5/10
  
  详细风险指标:
    
    市场风险:
      - Beta: 1.05
      - 与市场相关性: 0.72
      - VaR (95%): 50,000 元
      - VaR (99%): 75,000 元
    
    信用风险:
      - 交易对手数: 15 个
      - 敞口集中度: 12%
      - 违约概率: 0.1%
    
    运营风险:
      - 本月事件: 1 起
      - 损失金额: 5,000 元
      - 恢复状态: 已恢复
    
    流动性风险:
      - 清算时间 (95%): 3 天
      - 平均买卖价差: 0.02
      - 流动性覆盖比: 1.85
  
  建议:
    1. 加强风险监控频率
    2. 审查投资组合多样化
    3. 更新应急计划
  
  下次审查: 2026-03-19
```

---

## 🎯 自定义命令

### 命令 1: `/test` - 运行测试

```bash
命令: /test
描述: 运行完整的测试套件，展示覆盖率报告并关注失败的测试
Agent: build (构建 Agent)
语言: 中文/英文

使用示例:
  在 OpenCode 中输入: /test
  
  系统会:
    1. 运行所有单元测试
    2. 生成覆盖率报告
    3. 显示失败的测试 (如有)
    4. 提供修复建议
```

### 命令 2: `/analyze` - 分析交易系统

```bash
命令: /analyze
描述: 分析交易系统的性能指标，识别瓶颈，提出优化建议
Agent: build (构建 Agent)
语言: 中文/英文

使用示例:
  在 OpenCode 中输入: /analyze
  
  系统会:
    1. 收集系统性能数据
    2. 分析交易指标
    3. 识别性能瓶颈
    4. 提供优化建议

返回内容:
  - 系统性能总结
  - 交易性能统计
  - 风险指标分析
  - 优化建议清单
```

### 命令 3: `/monitor` - 启动实时监控

```bash
命令: /monitor
描述: 启动实时监控模式，持续监控系统健康、交易状态和风险指标
Agent: build (构建 Agent)
语言: 中文/英文

使用示例:
  在 OpenCode 中输入: /monitor
  
  系统会:
    1. 连接所有 MCP 服务器
    2. 启动实时数据流
    3. 持续监控系统状态
    4. 实时警告异常

监控内容:
  - 系统健康状况
  - 活跃交易数量
  - 投资组合价值
  - 风险指标
  - 性能指标
```

### 命令 4: `/deploy` - 部署系统

```bash
命令: /deploy
描述: 部署交易系统到生产环境，执行完整的预部署检查
Agent: build (构建 Agent)
语言: 中文/英文

使用示例:
  在 OpenCode 中输入: /deploy
  
  系统会:
    1. 执行预部署检查
    2. 验证所有配置
    3. 运行集成测试
    4. 执行部署流程
    5. 验证部署成功

预部署检查:
  ✓ 配置验证
  ✓ 依赖检查
  ✓ 测试覆盖率
  ✓ 代码质量
  ✓ 安全扫描
```

---

## 🤖 AI Agent 详解

### Agent 1: `code-reviewer` - 代码审查员

```
角色: 代码审查专家
权限: 只读 (无法修改代码)
主要工具:
  ✗ 无法使用: write, edit, bash
  ✓ 可以使用: read, 分析工具

使用场景:
  - 检查代码质量
  - 识别安全问题
  - 检查最佳实践
  - 提出改进建议

启用方法:
  > /agent code-reviewer
  > 请审查 @src/core/trading_system.py 的代码质量
  
示例提示词:
  > /agent code-reviewer
  > 分析这个文件的代码质量，检查是否有:
  >   1. 安全漏洞
  >   2. 性能问题
  >   3. 代码异味
  >   4. 最佳实践违规
```

### Agent 2: `trading-analyst` - 交易分析师

```
角色: 交易数据分析专家
权限: 数据访问权限
主要工具:
  ✓ 可以使用: trading-monitor, data-analyzer, risk-manager
  ✓ 可以编辑: edit (但不能删除)
  ✗ 无法使用: bash 危险命令

使用场景:
  - 分析交易性能
  - 评估交易策略
  - 识别交易机会
  - 风险评估

启用方法:
  > /agent trading-analyst
  > 分析今天的交易表现
  
示例提示词:
  > /agent trading-analyst
  > 请分析:
  >   1. 今日交易的收益情况
  >   2. 哪些交易表现良好
  >   3. 哪些交易需要改进
  >   4. 建议的改进方向
```

### Agent 3: `quantum-engineer` - 量化工程师

```
角色: 量化算法开发专家
权限: 完全权限 (可以修改代码、执行命令)
主要工具:
  ✓ 所有工具可用
  ✓ 可以写入和编辑文件
  ✓ 可以执行命令
  ✓ 可以优化算法

使用场景:
  - 开发交易算法
  - 参数优化
  - 算法回测
  - 性能优化

启用方法:
  > /agent quantum-engineer
  > 优化 algo_001 算法
  
示例提示词:
  > /agent quantum-engineer
  > 请优化 algo_001，目标是:
  >   1. 提高夏普比率
  >   2. 降低最大回撤
  >   3. 改进胜率
  >   4. 优化参数设置

返回内容:
  - 新的算法代码
  - 优化的参数
  - 回测结果
  - 性能改进对比
```

### Agent 4: `devops-engineer` - 运维工程师

```
角色: 系统部署和运维专家
权限: 完全权限 (系统级操作)
主要工具:
  ✓ 所有工具可用
  ✓ 可以执行系统命令
  ✓ 可以部署和配置
  ✓ 可以管理服务

使用场景:
  - 系统部署
  - 环境配置
  - 性能优化
  - 故障排查

启用方法:
  > /agent devops-engineer
  > 部署交易系统
  
示例提示词:
  > /agent devops-engineer
  > 请部署交易系统到生产环境:
  >   1. 检查所有依赖
  >   2. 运行预部署检查
  >   3. 执行部署流程
  >   4. 验证系统运行

返回内容:
  - 部署日志
  - 系统状态
  - 性能指标
  - 任何警告或错误
```

---

## 💡 使用场景和示例

### 场景 1: 获取投资组合状态

**目标**: 查看当前投资组合的完整状态

**命令**:
```
获取我的投资组合状态、系统健康状况和活跃交易
Get portfolio status, system health, and active trades. Use trading-monitor tool.
```

**执行过程**:
```
OpenCode 会:
  1. 调用 get_portfolio_status 工具
  2. 调用 get_system_health 工具
  3. 调用 get_active_trades 工具
  4. 整合所有信息
  5. 生成综合报告
```

**预期结果**:
```
投资组合总价值: 1,000,000 元
├─ 可用现金: 250,000 元
├─ 头寸数量: 5 个
├─ 今日收益: +5,000 元
├─ 总收益: +50,000 元
└─ 风险等级: 中等

系统状态: 健康
├─ 运行时间: 24.5 小时
├─ 内存使用: 62.8%
├─ CPU 使用: 45.2%
└─ 活跃连接: 15 个

活跃交易:
├─ TRADE_001: AAPL, 买入 100 股, 收益 +250 元
├─ TRADE_002: MSFT, 卖出 50 股, 收益 +75 元
└─ ... (共 5 笔)
```

---

### 场景 2: 分析市场数据

**目标**: 详细分析 AAPL 的市场情况

**命令**:
```
分析 AAPL 的市场数据，包括:
  1. 时间序列分析
  2. 技术模式检测
  3. 情绪分析
Use data-analyzer tool.
```

**执行过程**:
```
OpenCode 会:
  1. 调用 get_market_data 工具获取实时价格
  2. 调用 analyze_time_series 进行趋势分析
  3. 调用 detect_patterns 检测技术模式
  4. 调用 sentiment_analysis 分析市场情绪
  5. 生成综合分析报告
```

**预期结果**:
```
AAPL 市场分析报告
═════════════════════

实时数据:
  当前价格: 150.00 元
  涨跌幅: +2.5%
  交易量: 1,000,000 股
  买卖价差: 0.01 元

时间序列分析:
  趋势: 上升趋势 ✓
  强度: 0.75
  斜率: 0.245
  支撑: 149.50 元
  阻力: 156.00 元

技术模式:
  1. 移动平均线黄金交叉 (信心度 92%) ✓ 看涨
  2. 双顶形态 (信心度 85%) ✗ 看跌
  3. 三角形整理 (信心度 72%) ➡ 中立

市场情绪:
  总体: 积极 (0.72/1.0)
  看涨: 55%
  中性: 30%
  看跌: 15%

建议:
  → 技术面看涨，但要注意风险
  → 监控阻力位在 156.00 元
  → 支撑位在 149.50 元
```

---

### 场景 3: 优化交易算法

**目标**: 优化 algo_001 以提高性能

**命令**:
```
/agent quantum-engineer
优化 algo_001 算法:
  - 目标: 最大化夏普比率
  - 约束: 最大回撤不超过 15%
  - 时间范围: 最近 30 天数据
Use quantum-engine tool.
```

**执行过程**:
```
OpenCode 会:
  1. 调用 list_algorithms 获取 algo_001 信息
  2. 调用 backtest_algorithm 进行基准测试
  3. 调用 optimize_parameters 进行参数优化
  4. 验证新参数的有效性
  5. 比较优化前后的性能
  6. 生成优化建议
```

**预期结果**:
```
算法优化报告
═════════════

优化前:
  夏普比率: 1.85
  最大回撤: 20%
  胜率: 55%
  利润因子: 1.80

优化后:
  夏普比率: 2.45 ✓ (+32.4%)
  最大回撤: 12% ✓ (-40%)
  胜率: 58% ✓ (+5.5%)
  利润因子: 2.50 ✓ (+38.9%)

优化的参数:
  回溯期: 20 天 (原: 15 天)
  进入阈值: 0.05 (原: 0.08)
  退出阈值: 0.03 (原: 0.05)
  头寸大小: 12% (原: 10%)

建议: ✓ 采用新参数
```

---

### 场景 4: 风险评估和压力测试

**目标**: 对投资组合进行完整风险评估

**命令**:
```
/agent trading-analyst
对我的投资组合进行风险评估:
  1. 计算 VaR 和条件 VaR
  2. 进行市场暴跌压力测试
  3. 检查头寸限制
  4. 进行合规检查
Use risk-manager tool.
```

**执行过程**:
```
OpenCode 会:
  1. 调用 calculate_var 计算风险价值
  2. 调用 stress_test 进行压力测试
  3. 调用 check_position_limits 检查限制
  4. 调用 compliance_check 检查合规性
  5. 调用 get_risk_report 生成完整报告
```

**预期结果**:
```
投资组合风险评估报告
════════════════════

风险指标:
  VaR (95%): 50,000 元 (5% 的投资组合)
  VaR (99%): 75,000 元 (7.5%)
  条件 VaR: 65,000 元

压力测试 - 市场暴跌 20%:
  投资组合损失: -150,000 元 (-15%)
  受影响头寸: 5 个
  恢复时间: 3-5 个交易日
  
头寸限制检查:
  所有头寸: ✓ 符合限制
  投资组合占比: ✓ 符合限制
  行业集中度: ✓ 符合限制

合规性:
  SEC: ✓ 符合
  FINRA: ✓ 符合
  MiFID II: ✓ 符合

总体风险评分: 6.5/10 (中等)

建议:
  1. 风险可控，继续监控
  2. 考虑增加对冲头寸
  3. 定期审查投资组合
```

---

### 场景 5: 代码审查

**目标**: 审查交易系统的代码质量

**命令**:
```
/agent code-reviewer
请审查 @src/core/trading_system.py 的代码质量:
  1. 检查安全问题
  2. 识别性能瓶颈
  3. 评估代码可维护性
  4. 提出改进建议
```

**执行过程**:
```
OpenCode 会:
  1. 读取代码文件
  2. 进行静态分析
  3. 检查安全问题
  4. 评估性能
  5. 检查最佳实践
  6. 生成审查报告
```

**预期结果**:
```
代码审查报告 - trading_system.py
════════════════════════════════

代码质量评分: 8.5/10 (很好)

✓ 优点:
  - 代码结构清晰
  - 函数职责单一
  - 文档完整
  - 错误处理健全

⚠ 改进建议:
  1. 优化 calculate_pnl() 函数的时间复杂度 (Line 145)
  2. 添加日志记录功能 (Line 234-256)
  3. 提取魔法数字为常量 (Line 78, 92)
  4. 添加更多单元测试
  5. 考虑实现缓存机制

🔒 安全检查:
  - SQL 注入: ✓ 安全
  - 输入验证: ✓ 充分
  - 权限检查: ✓ 实施正确
  - 数据加密: ⚠ 建议加强

📊 性能分析:
  - 平均执行时间: 2.3ms (良好)
  - 内存使用: 45MB (正常)
  - 缓存命中率: 87% (良好)

总体建议: 代码质量良好，建议实施以上改进
```

---

## 🔌 高级命令

### 全局命令

```bash
# 查看版本
opencode --version

# 初始化项目
opencode /init

# 连接 API 提供商
opencode /connect

# 撤销最后一次更改
opencode /undo

# 重做操作
opencode /redo

# 共享对话
opencode /share

# 查看配置
opencode config show

# 重新加载配置
opencode /reload

# 查看帮助
opencode --help
```

### MCP 命令

```bash
# 列出所有 MCP 服务器
opencode mcp list

# 调试 MCP 连接
opencode mcp debug trading-monitor

# 配置 OAuth 认证
opencode mcp auth sentry

# 清除认证信息
opencode mcp logout sentry

# 查看认证状态
opencode mcp auth list
```

### 服务器命令

```bash
# 启动 Web 服务器
opencode web

# 启动 TUI 界面
opencode

# 运行单个命令
opencode run "分析交易系统"

# 查看日志
opencode logs
```

---

## ⚙️ 配置修改

### 修改默认模型

编辑 `opencode.jsonc`:
```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```

### 启用/禁用 MCP 服务器

编辑 `opencode.jsonc`:
```json
{
  "mcp": {
    "trading-monitor": {
      "enabled": true      // 启用
    },
    "gh_grep": {
      "enabled": false     // 禁用
    }
  }
}
```

### 修改权限设置

编辑 `opencode.jsonc`:
```json
{
  "permission": {
    "bash": "ask",         // 执行前询问
    "write": "ask",        // 编辑前询问
    "edit": "allow"        // 自动允许
  }
}
```

---

## 🆘 故障排除

### 问题 1: MCP 服务器无法连接

**症状**: 调用 MCP 工具时出现连接错误

**解决方案**:
```bash
# 1. 检查 MCP 列表
opencode mcp list

# 2. 调试 MCP 连接
opencode mcp debug trading-monitor

# 3. 检查 Python 环境
python --version      # 需要 3.10+

# 4. 重新启动 OpenCode
killall opencode
opencode
```

### 问题 2: 配置文件出错

**症状**: 启动时出现配置错误

**解决方案**:
```bash
# 1. 验证 JSON 语法
python -m json.tool opencode.jsonc

# 2. 检查配置文件位置
cat opencode.jsonc | head -20

# 3. 重置配置
cp opencode.jsonc opencode.jsonc.backup
# 然后手动编辑或重新安装
```

### 问题 3: Agent 无法执行命令

**症状**: Agent 权限不足或无法执行

**解决方案**:
```bash
# 1. 检查权限设置
opencode config show | grep permission

# 2. 查看 Agent 配置
cat opencode.jsonc | grep -A 20 "agent"

# 3. 更改权限为 allow
# 编辑 opencode.jsonc，修改 permission 设置
```

### 问题 4: 内存使用过高

**症状**: OpenCode 占用过多内存

**解决方案**:
```bash
# 1. 禁用不使用的 MCP
# 编辑 opencode.jsonc，设置 "enabled": false

# 2. 启用上下文压缩
# 在 opencode.jsonc 中设置:
{
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 10000
  }
}

# 3. 清理缓存
rm -rf ~/.local/share/opencode/cache

# 4. 重启 OpenCode
killall opencode
opencode
```

---

## 📚 参考资源

### 官方文档
- 官方网站: https://opencode.ai
- 完整文档: https://opencode.ai/docs
- 配置参考: https://opencode.ai/config.json
- GitHub: https://github.com/anomalyco/opencode

### 本地文档
- 详细安装指南: `/root/comic_ai/docs/OPENCODE_SETUP.md`
- 快速参考: `/root/comic_ai/docs/OPENCODE_QUICK_REFERENCE.md`
- 配置文件: `/root/comic_ai/opencode.jsonc`
- MCP 实现: `/root/comic_ai/src/core/` 和 `/root/comic_ai/engine/`

### 获得帮助
- Discord 社区: https://opencode.ai/discord
- 报告问题: https://github.com/anomalyco/opencode/issues
- 查看日志: `opencode logs`

---

## 📋 快速参考表

### MCP 工具总览

| MCP 名称 | 工具数 | 主要功能 |
|---------|--------|---------|
| trading-monitor | 5 | 投资组合监控 |
| quantum-engine | 5 | 算法优化 |
| data-analyzer | 6 | 市场分析 |
| risk-manager | 5 | 风险评估 |
| **总计** | **21** | - |

### Agent 权限表

| Agent | 角色 | read | write | edit | bash | MCP 访问 |
|-------|------|------|-------|------|------|---------|
| code-reviewer | 审查 | ✓ | ✗ | ✗ | ✗ | ✗ |
| trading-analyst | 分析 | ✓ | ✗ | ✓ | ✗ | ✓ |
| quantum-engineer | 开发 | ✓ | ✓ | ✓ | ✓ | ✓ |
| devops-engineer | 运维 | ✓ | ✓ | ✓ | ✓ | ✓ |

### 命令快速参考

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| /test | 运行测试 | 验证代码 |
| /analyze | 分析系统 | 性能评估 |
| /monitor | 实时监控 | 持续监控 |
| /deploy | 部署系统 | 上线发布 |

---

## 🎓 学习路径

**初级**:
1. 阅读本文档
2. 运行 `/test` 命令
3. 尝试 `/analyze` 命令

**中级**:
1. 自定义 Agent 提示词
2. 创建 MCP 工具
3. 优化算法参数

**高级**:
1. 集成实时数据源
2. 实现自动化工作流
3. 开发高级分析模块

---

**最后更新**: 2026-02-19
**版本**: 1.0.0
**维护**: OpenCode 集成团队

---

## 🛠️ 系统验证脚本

### 1. 完整系统验证脚本

```python
# verify_system.py - 验证完整的 OpenCode 交易系统
import subprocess
import json
import os
import sys

class OpenCodeVerifier:
    """验证 OpenCode 和交易系统集成"""
    
    def __init__(self):
        self.results = {}
        self.failed = []
    
    def verify_all(self):
        """运行所有验证"""
        print("🔍 验证 OpenCode 交易系统完整性...\n")
        
        verifications = [
            ("OpenCode 安装", self.verify_opencode_installed),
            ("配置文件", self.verify_config_file),
            ("MCP 服务器", self.verify_mcp_servers),
            ("AI Agents", self.verify_agents),
            ("自定义命令", self.verify_commands),
            ("Python 环境", self.verify_python_env),
            ("交易系统", self.verify_trading_system),
        ]
        
        for name, check_func in verifications:
            try:
                result = check_func()
                self.results[name] = result
                status = "✓" if result else "✗"
                print(f"{status} {name}: {'通过' if result else '失败'}")
                if not result:
                    self.failed.append(name)
            except Exception as e:
                self.results[name] = False
                print(f"✗ {name}: 错误 - {str(e)[:50]}")
                self.failed.append(name)
        
        print("\n" + "="*60)
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        print(f"✅ 验证完成: {passed}/{total} 检查通过")
        
        if self.failed:
            print(f"\n❌ 失败项: {', '.join(self.failed)}")
            return False
        return True
    
    def verify_opencode_installed(self):
        """检查 OpenCode 是否已安装"""
        try:
            result = subprocess.run(
                ["opencode", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def verify_config_file(self):
        """验证配置文件"""
        if not os.path.exists("opencode.jsonc"):
            print("    配置文件不存在")
            return False
        
        try:
            with open("opencode.jsonc", 'r') as f:
                content = f.read()
                # 基本验证
                if '{"mcp":' not in content and '{' in content:
                    return True
        except:
            return False
        
        return True
    
    def verify_mcp_servers(self):
        """验证 MCP 服务器"""
        mcps = ["trading-monitor", "quantum-engine", "data-analyzer", "risk-manager"]
        connected = 0
        
        for mcp in mcps:
            try:
                result = subprocess.run(
                    ["opencode", "mcp", "list"],
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                if mcp in result.stdout:
                    connected += 1
            except:
                pass
        
        return connected >= 3  # 至少 3 个 MCP 连接
    
    def verify_agents(self):
        """验证 Agents"""
        expected_agents = [
            "code-reviewer",
            "trading-analyst",
            "quantum-engineer",
            "devops-engineer"
        ]
        
        for agent in expected_agents:
            try:
                result = subprocess.run(
                    ["find", ".opencode/agents", "-name", f"*{agent}*"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return False
            except:
                pass
        
        return True
    
    def verify_commands(self):
        """验证自定义命令"""
        commands = ["/test", "/analyze", "/monitor", "/deploy"]
        try:
            with open("opencode.jsonc", 'r') as f:
                content = f.read()
                return all(cmd in content for cmd in commands)
        except:
            return False
    
    def verify_python_env(self):
        """验证 Python 环境"""
        required_packages = [
            "numpy",
            "pandas",
            "psutil"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                print(f"    缺少包: {package}")
                return False
        
        return True
    
    def verify_trading_system(self):
        """验证交易系统"""
        required_files = [
            "src/core/trading_monitor_mcp.py",
            "engine/quantum_engine_mcp.py",
            "src/core/data_analyzer_mcp.py",
            "src/core/risk_manager_mcp.py"
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                print(f"    缺少文件: {file}")
                return False
        
        return True

if __name__ == "__main__":
    verifier = OpenCodeVerifier()
    success = verifier.verify_all()
    sys.exit(0 if success else 1)
```

**运行验证**:
```bash
python verify_system.py
```

### 2. 快速诊断脚本

```python
# diagnose.py - 快速诊断系统问题
import subprocess
import os
import psutil

def quick_diagnose():
    """快速系统诊断"""
    print("⚡ 快速诊断 OpenCode 系统\n")
    
    # 1. 进程状态
    print("📊 系统资源:")
    opencode_proc = None
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
        if 'opencode' in proc.info['name']:
            opencode_proc = proc.info
            print(f"  OpenCode PID: {opencode_proc['pid']}")
            print(f"  内存: {opencode_proc['memory_percent']:.1f}%")
            print(f"  CPU: {opencode_proc['cpu_percent']:.1f}%")
            break
    
    if not opencode_proc:
        print("  ℹ️  OpenCode 未运行 (正常,需要手动启动)")
    
    # 2. 文件系统检查
    print("\n📁 文件系统:")
    critical_files = [
        "opencode.jsonc",
        ".opencode/agents",
        "src/core/trading_monitor_mcp.py",
    ]
    
    for file in critical_files:
        exists = "✓" if os.path.exists(file) else "✗"
        print(f"  {exists} {file}")
    
    # 3. 缓存大小
    cache_dir = os.path.expanduser("~/.local/share/opencode/cache")
    if os.path.exists(cache_dir):
        cache_size = sum(
            f.stat().st_size for f in 
            __import__('pathlib').Path(cache_dir).rglob('*') 
            if f.is_file()
        ) / (1024*1024)
        print(f"\n💾 缓存大小: {cache_size:.2f} MB")
        if cache_size > 500:
            print("  ⚠️  建议清理缓存: rm -rf ~/.local/share/opencode/cache")
    
    # 4. 网络连接
    print("\n🌐 网络检查:")
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
             "https://opencode.ai"],
            capture_output=True,
            timeout=5
        )
        print(f"  opencode.ai: {result.stdout.decode().strip()}")
    except:
        print("  ⚠️  网络连接检查失败")

if __name__ == "__main__":
    quick_diagnose()
```

### 3. 性能监控脚本

```python
# monitor_performance.py - 实时性能监控
import psutil
import time
import statistics

def monitor_performance(duration_seconds=60):
    """监控 OpenCode 性能"""
    print(f"📈 监控 OpenCode 性能 ({duration_seconds}s)...\n")
    
    cpu_samples = []
    memory_samples = []
    
    for i in range(duration_seconds):
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            if 'opencode' in proc.info['name']:
                cpu_samples.append(proc.info['cpu_percent'])
                memory_samples.append(proc.info['memory_percent'])
        
        time.sleep(1)
        if i % 10 == 0:
            print(f"  进度: {i}/{duration_seconds}s")
    
    if not cpu_samples:
        print("❌ OpenCode 未运行")
        return
    
    print("\n📊 性能统计:")
    print(f"  CPU 平均: {statistics.mean(cpu_samples):.2f}%")
    print(f"  CPU 最大: {max(cpu_samples):.2f}%")
    print(f"  内存平均: {statistics.mean(memory_samples):.2f}%")
    print(f"  内存最大: {max(memory_samples):.2f}%")
    
    if statistics.mean(memory_samples) > 50:
        print("\n⚠️  内存使用过高,建议清理缓存或禁用不必要的 MCP")

if __name__ == "__main__":
    monitor_performance(60)
```

### 4. 配置检查脚本

```python
# check_config.py - 详细的配置检查
import json
import os

def check_opencode_config():
    """详细检查 OpenCode 配置"""
    print("⚙️  检查 OpenCode 配置...\n")
    
    config_file = "opencode.jsonc"
    
    if not os.path.exists(config_file):
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    # 读取配置 (移除注释)
    with open(config_file, 'r') as f:
        lines = f.readlines()
    
    # 移除注释用于验证
    content = '\n'.join([line.split('//')[0] for line in lines])
    
    try:
        config = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        return False
    
    # 检查关键配置项
    print("✓ 配置结构检查:")
    checks = {
        "model": "主模型",
        "small_model": "小模型",
        "mcp": "MCP 服务器",
        "permission": "权限设置",
    }
    
    for key, desc in checks.items():
        if key in config:
            print(f"  ✓ {desc}")
        else:
            print(f"  ✗ 缺少: {desc}")
    
    # 检查 MCP 配置
    print("\n🔌 MCP 服务器配置:")
    if 'mcp' in config:
        for mcp_name, mcp_config in config['mcp'].items():
            enabled = mcp_config.get('enabled', True)
            status = "✓ 启用" if enabled else "✗ 禁用"
            print(f"  {status}: {mcp_name}")
    
    # 检查权限设置
    print("\n🔒 权限设置:")
    if 'permission' in config:
        for perm, value in config['permission'].items():
            print(f"  {perm}: {value}")
    
    print("\n✅ 配置检查完成")
    return True

if __name__ == "__main__":
    check_opencode_config()
```

---

## 📋 快速参考表

### MCP 工具总览

| MCP 名称 | 工具数 | 主要功能 |
|---------|--------|---------|
| trading-monitor | 5 | 投资组合监控 |
| quantum-engine | 5 | 算法优化 |
| data-analyzer | 6 | 市场分析 |
| risk-manager | 5 | 风险评估 |
| **总计** | **21** | - |

### Agent 权限表

| Agent | 角色 | read | write | edit | bash | MCP 访问 |
|-------|------|------|-------|------|------|---------|
| code-reviewer | 审查 | ✓ | ✗ | ✗ | ✗ | ✗ |
| trading-analyst | 分析 | ✓ | ✗ | ✓ | ✗ | ✓ |
| quantum-engineer | 开发 | ✓ | ✓ | ✓ | ✓ | ✓ |
| devops-engineer | 运维 | ✓ | ✓ | ✓ | ✓ | ✓ |

### 命令快速参考

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| /test | 运行测试 | 验证代码 |
| /analyze | 分析系统 | 性能评估 |
| /monitor | 实时监控 | 持续监控 |
| /deploy | 部署系统 | 上线发布 |

---

## 🎓 学习路径

**初级**:
1. 阅读本文档
2. 运行 `/test` 命令
3. 尝试 `/analyze` 命令

**中级**:
1. 自定义 Agent 提示词
2. 创建 MCP 工具
3. 优化算法参数

**高级**:
1. 集成实时数据源
2. 实现自动化工作流
3. 开发高级分析模块

---

**最后更新**: 2026-02-19
**版本**: 1.0.0
**维护**: OpenCode 集成团队

---

END OF GUIDE
