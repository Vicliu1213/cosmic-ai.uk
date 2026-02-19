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
