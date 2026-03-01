# OpenCode 快速参考指南
# OpenCode Quick Reference Guide

## 🚀 快速开始 / Quick Start (30 秒)

```bash
# 1. 进入项目
cd /root/comic_ai

# 2. 运行安装脚本
bash scripts/install_opencode.sh

# 3. 启动 OpenCode
opencode

# 4. 在 OpenCode 中运行命令
/monitor
```

---

## 🛠️ 快速验证脚本

### 系统健康检查

```python
# quick_health_check.py - 快速系统健康检查
import subprocess
import sys

def quick_health_check():
    """30秒内完成系统健康检查"""
    
    checks = {
        "OpenCode": lambda: subprocess.run(["opencode", "--version"], capture_output=True).returncode == 0,
        "Config": lambda: __import__('os').path.exists("opencode.jsonc"),
        "Python": lambda: sys.version_info >= (3, 10),
        "Dependencies": lambda: subprocess.run(["pip", "list"], capture_output=True).returncode == 0,
    }
    
    print("⚡ 快速系统检查\n")
    results = {}
    
    for check_name, check_func in checks.items():
        try:
            result = check_func()
            status = "✓" if result else "✗"
            results[check_name] = result
            print(f"  {status} {check_name}")
        except Exception as e:
            print(f"  ✗ {check_name}: {str(e)[:30]}")
            results[check_name] = False
    
    print(f"\n总体: {'✓ 通过' if all(results.values()) else '✗ 需要修复'}")
    return all(results.values())

if __name__ == "__main__":
    success = quick_health_check()
    sys.exit(0 if success else 1)
```

**运行**:
```bash
python quick_health_check.py
```

---

## 📋 核心文件 / Core Files

| 文件 | 描述 | 位置 |
|------|------|------|
| **配置** | OpenCode 主配置文件 | `opencode.jsonc` |
| **MCP: 交易监控** | 实时交易系统监控 | `src/core/trading_monitor_mcp.py` |
| **MCP: 量化引擎** | 算法优化和回测 | `engine/quantum_engine_mcp.py` |
| **MCP: 数据分析** | 市场数据和技术分析 | `src/core/data_analyzer_mcp.py` |
| **MCP: 风险管理** | 风险评估和合规 | `src/core/risk_manager_mcp.py` |
| **安装脚本** | 自动安装工具 | `scripts/install_opencode.sh` |
| **文档** | 详细设置指南 | `docs/OPENCODE_SETUP.md` |

---

## 🛠️ 常用命令 / Common Commands

### 系统命令
```bash
opencode                      # 启动 TUI 界面
opencode web                  # 启动 Web 服务器
opencode run "命令"           # 运行单个命令
opencode --version            # 查看版本
```

### 配置命令
```bash
opencode /init                # 初始化项目
opencode /connect             # 连接 API 提供商
opencode config show          # 查看生效的配置
```

### MCP 命令
```bash
opencode mcp list             # 列出所有 MCP 服务器
opencode mcp debug <name>     # 调试 MCP 连接
opencode mcp auth <name>      # 配置 OAuth 认证
opencode mcp logout <name>    # 清除认证信息
```

### 会话管理
```bash
opencode /undo                # 撤销最后一次更改
opencode /redo                # 重做操作
opencode /share               # 共享对话链接
```

---

## 🔧 自定义命令 / Custom Commands

在 OpenCode 中运行:

```
/test                         # 运行测试套件
/analyze                      # 分析交易系统
/monitor                      # 启动实时监控
/deploy                       # 部署到生产环境
```

### 命令详解

#### /test - 运行测试
```python
# 执行后会:
# 1. 运行所有单元测试
# 2. 生成覆盖率报告
# 3. 显示测试统计
# 4. 提供修复建议 (如有失败)

# 调用方式:
# /test
# 或在 OpenCode 中输入: /test
```

#### /analyze - 分析系统
```python
# 执行后会:
# 1. 收集性能指标
# 2. 分析交易性能
# 3. 识别瓶颈
# 4. 提供优化建议

# 调用方式:
# /analyze
```

#### /monitor - 实时监控
```python
# 持续监控:
# • 系统健康状态
# • 活跃交易数量
# • 投资组合价值
# • 风险指标

# 调用方式:
# /monitor
# (持续运行直到 Ctrl+C)
```

#### /deploy - 部署系统
```python
# 完整的部署流程:
# 1. 预部署检查
# 2. 验证配置
# 3. 运行集成测试
# 4. 执行部署
# 5. 验证成功

# 调用方式:
# /deploy
# (需要确认)
```

---

## 🤖 Agents

### code-reviewer
用于代码审查，不能修改文件

```
/agent code-reviewer
请审查 @src/core/trading_system.py 的代码质量
```

### trading-analyst
用于交易分析，有权访问交易和数据工具

```
/agent trading-analyst
分析今天的交易性能和风险指标
```

### quantum-engineer
用于算法开发和优化

```
/agent quantum-engineer
优化 algo_001 算法的参数
```

### devops-engineer
用于系统部署和运维

```
/agent devops-engineer
部署交易系统到生产环境
```

---

## 🚨 常见问题快速解决

| 问题 | 解决方案 | 验证命令 |
|------|--------|---------|
| MCP 连接失败 | `opencode mcp list` + `opencode mcp debug <name>` | `opencode mcp list` |
| 配置错误 | 检查 `opencode.jsonc` 语法 | `python -m json.tool opencode.jsonc` |
| 内存占用高 | 禁用不必要的 MCP | 编辑 `opencode.jsonc` |
| 响应缓慢 | 清理缓存 `rm -rf ~/.local/share/opencode/cache` | 重启 OpenCode |

---

## 📊 MCP 工具速查表

### trading-monitor
```
• get_portfolio_status()        获取投资组合状态
• get_market_data(symbol)       获取市场数据
• get_system_health()           获取系统健康状态
• get_active_trades()           获取活跃交易
• get_risk_metrics()            获取风险指标
```

### quantum-engine
```
• list_algorithms()             列出所有算法
• optimize_parameters()         优化参数
• backtest_algorithm()          回测算法
• compare_algorithms()          比较算法
• get_engine_status()           获取引擎状态
```

### data-analyzer
```
• analyze_time_series()         时间序列分析
• detect_patterns()             检测价格模式
• correlation_analysis()        相关性分析
• sentiment_analysis()          情绪分析
• forecasting()                 价格预测
• risk_assessment()             风险评估
```

### risk-manager
```
• check_position_limits()       检查头寸限制
• calculate_var()               计算 VaR
• stress_test()                 压力测试
• compliance_check()            合规检查
• get_risk_report()             获取风险报告
```

---

## ⚙️ 配置速查表

### 启用/禁用 MCP
```json
{
  "mcp": {
    "trading-monitor": {
      "enabled": true
    }
  }
}
```

### 修改权限
```json
{
  "permission": {
    "bash": "ask",       // 执行前询问
    "write": "ask",      // 修改前询问
    "edit": "allow"      // 自动允许
  }
}
```

### 切换模型
```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```

---

## 🎯 典型工作流

### 1. 日常监控 (每天早上)
```bash
opencode run "检查今天的投资组合状态和风险指标"
```

### 2. 性能分析 (每周一次)
```bash
opencode /analyze
```

### 3. 算法优化 (按需)
```
/agent quantum-engineer
优化 algo_001 以提高夏普比率
```

### 4. 系统部署 (按需)
```bash
opencode /deploy
```

---

## 📚 相关文档

- **详细安装**: `docs/OPENCODE_SETUP.md`
- **完整指南**: `docs/OPENCODE_中文使用指南.md`
- **MCP 参考**: `docs/COMPLETE_DOCUMENTATION_INDEX.md`
- **快速参考**: `docs/QUICK_REFERENCE_GUIDE.md`

---

### quantum-engineer
用于算法开发，可以修改代码

```
/agent quantum-engineer
优化 algo_001 算法的参数
```

### devops-engineer
用于系统部署，有完全权限

```
/agent devops-engineer
部署交易系统到生产环境
```

---

## 📊 MCP 工具使用示例 / Usage Examples

### 1. 获取交易系统状态
```
获取当前投资组合状态、系统健康状况和活跃交易
Get portfolio status, system health, and active trades. Use trading-monitor tool.
```

### 2. 分析市场数据
```
分析 AAPL 的市场数据，包括技术模式和情绪分析
Analyze AAPL market data including technical patterns and sentiment. Use data-analyzer tool.
```

### 3. 优化交易算法
```
使用量化引擎优化 algo_001 算法以最大化夏普比率
Use quantum-engine to optimize algo_001 for maximum Sharpe ratio
```

### 4. 风险评估
```
对当前投资组合进行完整的风险评估和压力测试
Perform comprehensive risk assessment and stress testing on the portfolio. Use risk-manager tool.
```

### 5. 合规检查
```
执行 SEC、FINRA 和 MiFID II 合规检查
Run SEC, FINRA, and MiFID II compliance checks. Use risk-manager tool.
```

---

## 🎨 配置选项 / Configuration Options

### 模型设置
```jsonc
{
  "model": "anthropic/claude-sonnet-4-5",           // 主模型
  "small_model": "anthropic/claude-haiku-4-5",       // 轻量级模型
  "default_agent": "build"                           // 默认 Agent
}
```

### 工具权限
```jsonc
{
  "permission": {
    "bash": "ask",           // 执行前询问
    "write": "ask",          // 编辑前询问
    "edit": "allow"          // 自动允许
  }
}
```

### MCP 启用/禁用
```jsonc
{
  "mcp": {
    "trading-monitor": {
      "enabled": true        // 启用
    },
    "gh_grep": {
      "enabled": false       // 禁用
    }
  }
}
```

---

## 📝 提示和技巧 / Tips & Tricks

### 提高性能
1. 禁用不使用的 MCP 服务器
2. 使用小模型处理简单任务
3. 定期清理会话缓存
4. 启用上下文压缩

### 更好的结果
1. 在提示中包含具体的指标和要求
2. 使用 @file 引用特定文件
3. 让 OpenCode 为复杂任务创建计划
4. 使用正确的 Agent 进行专业任务

### 调试
1. 使用 `opencode mcp debug <name>` 调试连接
2. 检查日志文件获取错误信息
3. 验证配置语法：`python -m json.tool opencode.jsonc`
4. 尝试简化提示排除问题

---

## 🔗 重要链接 / Important Links

- **官方文档**: https://opencode.ai/docs
- **配置架构**: https://opencode.ai/config.json
- **GitHub**: https://github.com/anomalyco/opencode
- **Discord**: https://opencode.ai/discord
- **问题报告**: https://github.com/anomalyco/opencode/issues

---

## ⚙️ 高级配置 / Advanced Configuration

### 启用远程 MCP 服务器
```jsonc
{
  "mcp": {
    "sentry": {
      "type": "remote",
      "url": "https://mcp.sentry.dev/mcp",
      "oauth": {}
    }
  }
}
```

### 自定义代码格式化
```jsonc
{
  "formatter": {
    "black": {
      "command": ["black", "--line-length=127", "$FILE"],
      "extensions": [".py"]
    }
  }
}
```

### 监视文件的模式排除
```jsonc
{
  "watcher": {
    "ignore": ["node_modules/**", "venv/**", ".git/**"]
  }
}
```

---

## 🆘 故障排除 / Troubleshooting

### MCP 不工作
```bash
# 列出所有 MCP
opencode mcp list

# 调试特定 MCP
opencode mcp debug trading-monitor

# 查看完整日志
opencode logs
```

### 配置问题
```bash
# 验证 JSON 语法
python -m json.tool opencode.jsonc

# 重新加载配置
opencode /reload

# 使用自定义配置路径
export OPENCODE_CONFIG=/path/to/config.json
opencode
```

### 性能问题
```bash
# 检查上下文使用
opencode context info

# 清理缓存
rm -rf ~/.local/share/opencode/cache

# 禁用自动更新
# 在 opencode.jsonc 中设置: "autoupdate": false
```

---

## 📚 学习资源 / Learning Resources

1. **开始使用**: 
   - 查看官方文档主页
   - 运行 `opencode /init` 了解项目结构

2. **深入学习**:
   - 阅读 `docs/OPENCODE_SETUP.md`
   - 查看 Agent 定义示例
   - 研究 MCP 服务器实现

3. **获取帮助**:
   - Discord 社区: https://opencode.ai/discord
   - GitHub Issues: https://github.com/anomalyco/opencode/issues
   - 本地文档: `docs/OPENCODE_SETUP.md`

---

**最后更新**: 2026-02-19
**版本**: OpenCode Trading System Integration v1.0
