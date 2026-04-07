# OpenCode 集成安装指南
# OpenCode Integration Installation Guide

本指南帮助你为交易系统安装和配置 OpenCode 及其 MCP 服务器。
This guide helps you install and configure OpenCode with MCP servers for the trading system.

---

## 快速开始 / Quick Start

### 1. 安装 OpenCode / Install OpenCode

**Linux / macOS:**
```bash
# 使用安装脚本 (推荐)
curl -fsSL https://opencode.ai/install | bash

# 或使用包管理器
# Ubuntu/Debian
sudo apt install opencode

# macOS (Homebrew)
brew install anomalyco/tap/opencode

# Arch Linux
sudo pacman -S opencode
```

**Windows (WSL 推荐):**
```bash
# 使用 npm
npm install -g opencode-ai

# 或 Chocolatey
choco install opencode
```

**验证安装:**
```bash
opencode --version
```

---

## 2. 初始化项目 / Initialize Project

进入交易系统项目目录:
```bash
cd /root/comic_ai
```

初始化 OpenCode:
```bash
opencode /init
```

这会创建 `AGENTS.md` 文件来定义项目结构和代码规范。

---

## 3. 配置 API 提供商 / Configure API Provider

运行以下命令连接到 API 提供商:
```bash
opencode /connect
```

选择 OpenCode Zen (推荐的预审计模型)，或选择你喜欢的提供商:
- Anthropic Claude
- OpenAI GPT
- Google Gemini
- 其他支持的提供商

获取 API 密钥并粘贴到提示中。

---

## 4. 配置文件设置 / Configuration File Setup

### 全局配置 (Global Config)
```bash
# 创建全局配置目录
mkdir -p ~/.config/opencode

# 复制配置文件到全局目录
cp opencode.jsonc ~/.config/opencode/opencode.json
```

### 项目配置 (Project Config)
```bash
# 项目根目录已有 opencode.jsonc
# 该文件优先级最高，覆盖全局配置
ls -la opencode.jsonc
```

---

## 5. MCP 服务器安装 / MCP Servers Installation

### 验证 Python 环境

```bash
# 检查 Python 版本
python --version  # 需要 3.10+

# 安装依赖
pip install -r requirements.txt
```

### 安装必要的包

```bash
# 用于 MCP 服务器
pip install psutil numpy pandas

# 可选：高级数据分析
pip install scikit-learn statsmodels
```

---

## 6. 启动交易系统监控 / Start Trading System Monitoring

### 运行 OpenCode

```bash
# 启动 TUI 界面
opencode

# 或运行 CLI 命令
opencode run "分析当前交易系统状态"

# 启动 Web 服务器
opencode web
```

### 测试 MCP 工具

在 OpenCode 中运行以下命令:

```
获取投资组合状态和系统健康状况
Get my current portfolio status and system health. Use the trading-monitor tool.
```

或:

```
分析 AAPL 的市场数据和技术模式
Analyze AAPL market data and detect technical patterns. Use trading-monitor and data-analyzer tools.
```

---

## 7. 自定义 Agents / Custom Agents

### 创建 Agent 目录
```bash
mkdir -p .opencode/agents
```

### 创建交易分析员 Agent
```bash
# 创建 trading-analyst.md
cat > .opencode/agents/trading-analyst.md << 'EOF'
# Trading Analyst

You are an expert trading analyst specializing in quantitative analysis and risk management.

## Your Role
- Analyze market data and trading performance
- Identify trading opportunities
- Assess risk metrics
- Provide actionable recommendations

## Available Tools
- trading-monitor: Get portfolio and market data
- data-analyzer: Perform technical and sentiment analysis
- quantum-engine: Access optimization algorithms
- risk-manager: Check compliance and risk limits

## Communication Style
- Be concise and data-driven
- Always cite metrics and data points
- Focus on actionable insights
- Consider risk/reward ratios

## Key Guidelines
- Only use real market data from trading-monitor tool
- Verify all recommendations against risk limits
- Always include risk assessment in recommendations
- Keep response focused on requested analysis
EOF
```

### 创建量化工程师 Agent
```bash
cat > .opencode/agents/quantum-engineer.md << 'EOF'
# Quantum Engineer

You are a quantum computing specialist working on trading algorithms.

## Your Role
- Develop and optimize trading algorithms
- Conduct backtesting and performance analysis
- Implement risk management strategies
- Research quantum computing applications

## Available Tools
- quantum-engine: Optimize and test algorithms
- data-analyzer: Analyze market patterns
- risk-manager: Ensure compliance and limits

## Technical Focus
- Algorithm development and testing
- Parameter optimization
- Performance benchmarking
- Risk analysis

## Code Quality
- Write clean, well-documented code
- Include comprehensive tests
- Follow project conventions
- Document all changes
EOF
```

---

## 8. 创建自定义命令 / Custom Commands

在 `opencode.jsonc` 中已定义的命令:

### 运行测试
```
/test
```

### 分析交易系统
```
/analyze
```

### 启动监控
```
/monitor
```

### 部署系统
```
/deploy
```

---

## 9. MCP 服务器详细配置 / MCP Servers Configuration

### 交易监控 MCP
配置在 `opencode.jsonc`:
```json
{
  "mcp": {
    "trading-monitor": {
      "type": "local",
      "command": ["python", "src/core/trading_monitor_mcp.py"],
      "enabled": true
    }
  }
}
```

### 量化引擎 MCP
```json
{
  "quantum-engine": {
    "type": "local",
    "command": ["python", "engine/quantum_engine_mcp.py"],
    "enabled": true
  }
}
```

### 数据分析 MCP
```json
{
  "data-analyzer": {
    "type": "local",
    "command": ["python", "src/core/data_analyzer_mcp.py"],
    "enabled": true
  }
}
```

### 风险管理 MCP
```json
{
  "risk-manager": {
    "type": "local",
    "command": ["python", "src/core/risk_manager_mcp.py"],
    "enabled": true
  }
}
```

---

## 10. 高级配置 / Advanced Configuration

### 启用远程 MCP 服务器 (可选)

```json
{
  "mcp": {
    "gh_grep": {
      "type": "remote",
      "url": "https://mcp.grep.app",
      "enabled": true
    },
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "enabled": false,
      "headers": {
        "CONTEXT7_API_KEY": "{env:CONTEXT7_API_KEY}"
      }
    }
  }
}
```

### 设置权限 / Configure Permissions

```json
{
  "permission": {
    "bash": "ask",        // 每次执行前询问
    "write": "ask",       // 每次修改文件前询问
    "edit": "allow"       // 自动允许编辑
  }
}
```

### 配置代码格式化 / Code Formatters

```json
{
  "formatter": {
    "black": {
      "command": ["black", "--line-length=127", "$FILE"],
      "extensions": [".py"]
    },
    "prettier": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "extensions": [".js", ".json", ".yaml"]
    }
  }
}
```

---

## 11. 日常使用 / Daily Usage

### 启动交易系统监控
```bash
# 进入项目目录
cd /root/comic_ai

# 启动 OpenCode
opencode

# 在 OpenCode 中运行
/monitor
```

### 常用命令
```
# 获取系统状态
获取系统健康状况和交易统计

# 分析交易性能
分析今天的交易性能和风险指标

# 优化算法
优化 algo_001 算法的参数

# 回测策略
回测最近30天的交易性能

# 风险检查
执行压力测试和合规检查
```

---

## 12. 故障排除 / Troubleshooting

### MCP 连接问题
```bash
# 测试 MCP 服务器
opencode mcp list

# 调试 MCP 连接
opencode mcp debug trading-monitor

# 查看错误日志
opencode logs
```

**详细排查步骤**:
```python
# 创建验证脚本 verify_mcp.py
import subprocess
import json
import sys

def verify_mcp_connection():
    """验证所有 MCP 服务器连接"""
    mcps = ["trading-monitor", "quantum-engine", "data-analyzer", "risk-manager"]
    
    print("🔍 验证 MCP 服务器连接状态...")
    results = {}
    
    for mcp in mcps:
        try:
            result = subprocess.run(
                ["opencode", "mcp", "debug", mcp],
                capture_output=True,
                timeout=5,
                text=True
            )
            results[mcp] = "✓ 连接成功" if result.returncode == 0 else "✗ 连接失败"
            print(f"  {mcp}: {results[mcp]}")
        except subprocess.TimeoutExpired:
            results[mcp] = "✗ 超时"
            print(f"  {mcp}: ✗ 超时")
        except Exception as e:
            results[mcp] = f"✗ 错误: {e}"
            print(f"  {mcp}: ✗ 错误: {e}")
    
    return results

if __name__ == "__main__":
    results = verify_mcp_connection()
    failed = [k for k, v in results.items() if "✗" in v]
    sys.exit(len(failed))
```

**运行验证**:
```bash
python verify_mcp.py
```

### 配置问题

**验证配置语法**:
```bash
# 使用 Python 验证 JSONC
python -c "
import json
try:
    with open('opencode.jsonc', 'r') as f:
        # 移除注释用于验证
        content = f.read()
        content = '\n'.join([line.split('//')[0] for line in content.split('\n')])
        json.loads(content)
    print('✓ 配置语法正确')
except json.JSONDecodeError as e:
    print(f'✗ 配置错误: {e}')
"

# 查看生效的配置
opencode config show

# 验证配置文件是否存在
ls -la opencode.jsonc ~/.config/opencode/opencode.json
```

**配置修复脚本**:
```python
# fix_config.py - 自动修复常见配置问题
import json
import os

def fix_opencode_config():
    """修复常见的配置问题"""
    config_path = "opencode.jsonc"
    
    if not os.path.exists(config_path):
        print(f"✗ 配置文件不存在: {config_path}")
        return False
    
    # 读取配置
    with open(config_path, 'r') as f:
        content = f.read()
    
    # 检查常见问题
    issues = []
    
    # 1. 检查缺少逗号
    if '}\n  {' in content:
        issues.append("发现缺少逗号的问题")
    
    # 2. 检查未闭合的括号
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        issues.append(f"括号不匹配: {{ {open_braces} vs }} {close_braces}")
    
    # 3. 检查注释语法
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if '//' in line and '"//' not in line:
            print(f"行 {i} 有注释: {line.strip()[:50]}...")
    
    if issues:
        print("✗ 发现的问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("✓ 配置文件检查通过")
    return True

if __name__ == "__main__":
    fix_opencode_config()
```

### 性能问题

**诊断性能问题**:
```bash
# 检查上下文使用
opencode context info

# 检查内存使用
ps aux | grep opencode | grep -v grep
# 查看 VSZ 和 RSS 列

# 检查 CPU 使用
top -p $(pgrep opencode)

# 清理缓存
rm -rf ~/.local/share/opencode/cache

# 检查磁盘空间
du -sh ~/.local/share/opencode/
```

**性能优化脚本**:
```python
# optimize_performance.py
import os
import shutil
import subprocess

def optimize_opencode():
    """优化 OpenCode 性能"""
    
    print("🚀 开始性能优化...")
    
    # 1. 清理缓存
    cache_dir = os.path.expanduser("~/.local/share/opencode/cache")
    if os.path.exists(cache_dir):
        size_before = sum(f.stat().st_size for f in 
                         Path(cache_dir).rglob('*') if f.is_file()) / (1024*1024)
        shutil.rmtree(cache_dir)
        print(f"✓ 清理缓存: {size_before:.2f} MB")
    
    # 2. 禁用不必要的 MCP
    print("\n⚙️  建议的配置优化:")
    print("  - 禁用不使用的远程 MCP 服务器")
    print("  - 启用上下文压缩 (compaction.auto = true)")
    print("  - 减少日志冗长度")
    
    # 3. 重启服务
    print("\n⚡ 重启 OpenCode:")
    os.system("killall opencode 2>/dev/null")
    print("  等待 5 秒后重新启动...")
    import time
    time.sleep(5)
    
    print("✓ 性能优化完成")

if __name__ == "__main__":
    from pathlib import Path
    optimize_opencode()
```

**常见性能问题与解决方案**:

| 问题 | 症状 | 解决方案 |
|------|------|---------|
| 高内存占用 | > 1GB 内存使用 | 禁用远程 MCP，启用压缩，清理缓存 |
| 响应缓慢 | 命令执行 > 5s | 检查网络，减少上下文大小，禁用日志 |
| MCP 超时 | "Connection timeout" | 检查防火墙，增加超时时间，重启服务 |
| 配置加载失败 | 启动错误 | 验证 JSON 语法，检查权限，重置配置 |

---

## 13. 学习资源 / Learning Resources

- **官方文档**: https://opencode.ai/docs
- **GitHub 仓库**: https://github.com/anomalyco/opencode
- **Discord 社区**: https://opencode.ai/discord
- **配置参考**: https://opencode.ai/config.json

---

## 14. 下一步 / Next Steps

1. **提交配置到 Git**
   ```bash
   git add opencode.jsonc .opencode/
   git commit -m "feat: add OpenCode configuration with MCP servers"
   ```

2. **为团队共享配置**
   ```bash
   # 在项目文档中记录配置
   git add docs/OPENCODE_SETUP.md
   ```

3. **设置组织级配置** (可选)
   ```bash
   # 创建 .well-known/opencode 端点
   # 实现组织范围的配置共享
   ```

4. **监控和优化**
   - 定期检查 MCP 性能
   - 优化 Agent 提示词
   - 收集反馈并改进工作流

---

## 支持 / Support

遇到问题?
- 查看官方文档: https://opencode.ai/docs
- 报告问题: https://github.com/anomalyco/opencode/issues
- 加入社区: https://opencode.ai/discord

祝你使用愉快! Happy coding!
