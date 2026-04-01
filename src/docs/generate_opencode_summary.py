#!/usr/bin/env python3
"""
OpenCode 配置总结生成工具
OpenCode Configuration Summary Generator

This script generates a comprehensive summary of all OpenCode configurations
and MCP server installations for the trading system.
"""

import json
import os
from pathlib import Path
from datetime import datetime


def generate_summary():
    """生成配置总结"""
    
    project_dir = Path("/root/comic_ai")
    config_file = project_dir / "opencode.jsonc"
    
    # 读取配置
    with open(config_file, 'r') as f:
        content = f.read()
    
    # 解析配置（简化处理）
    config = json.loads(content.split('//')[0] if '//' in content else content)
    
    summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              OpenCode 交易系统集成配置总结                                     ║
║              OpenCode Trading System Integration Summary                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

生成时间 / Generated: {datetime.now().isoformat()}
项目位置 / Project Path: {project_dir}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 核心配置 / CORE CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

配置文件 / Config File:
  位置 / Location: {config_file}
  格式 / Format: JSONC (JSON with Comments)
  架构 / Schema: https://opencode.ai/config.json

默认模型 / Default Model:
  主模型 / Main: {config.get('model', 'Not set')}
  小模型 / Small: {config.get('small_model', 'Not set')}

提供商 / Provider:
  {config.get('provider', {})}

主题 / Theme: {config.get('theme', 'default')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. MCP 服务器配置 / MCP SERVERS CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

已配置的 MCP 服务器 / Configured MCP Servers:
"""
    
    mcp_config = config.get('mcp', {})
    for mcp_name, mcp_settings in mcp_config.items():
        mcp_type = mcp_settings.get('type', 'unknown')
        enabled = mcp_settings.get('enabled', False)
        status = "✓ 已启用" if enabled else "✗ 已禁用"
        
        summary += f"\n  {status} {mcp_name} ({mcp_type})"
        
        if mcp_type == "local":
            cmd = mcp_settings.get('command', [])
            summary += f"\n      命令 / Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}"
        elif mcp_type == "remote":
            url = mcp_settings.get('url', '')
            summary += f"\n      URL: {url}"
    
    summary += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. MCP 服务器文件 / MCP SERVER FILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

本地 MCP 服务器文件 / Local MCP Server Files:

  ✓ 交易监控 / Trading Monitor
    文件 / File: src/core/trading_monitor_mcp.py
    工具 / Tools:
      - get_portfolio_status      投资组合状态
      - get_market_data          市场数据
      - get_system_health        系统健康
      - get_active_trades        活跃交易
      - get_risk_metrics         风险指标

  ✓ 量化引擎 / Quantum Engine
    文件 / File: engine/quantum_engine_mcp.py
    工具 / Tools:
      - list_algorithms          列出算法
      - optimize_parameters      优化参数
      - backtest_algorithm       回测算法
      - compare_algorithms       比较算法
      - get_engine_status        引擎状态

  ✓ 数据分析 / Data Analyzer
    文件 / File: src/core/data_analyzer_mcp.py
    工具 / Tools:
      - analyze_time_series      时间序列分析
      - detect_patterns          模式检测
      - correlation_analysis     相关性分析
      - sentiment_analysis       情绪分析
      - forecasting              价格预测
      - risk_assessment          风险评估

  ✓ 风险管理 / Risk Manager
    文件 / File: src/core/risk_manager_mcp.py
    工具 / Tools:
      - check_position_limits    检查头寸限制
      - calculate_var            计算 VaR
      - stress_test              压力测试
      - compliance_check         合规检查
      - get_risk_report          风险报告

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. Agent 配置 / AGENT CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

配置的 Agents:

  ✓ code-reviewer
    描述 / Description: 代码审查员 - 检查代码最佳实践
    禁用工具 / Disabled Tools: write, edit, bash

  ✓ trading-analyst
    描述 / Description: 交易分析员 - 分析交易数据和策略性能
    启用工具 / Enabled Tools: trading-monitor, data-analyzer, risk-manager

  ✓ quantum-engineer
    描述 / Description: 量化工程师 - 开发和优化量化算法
    启用工具 / Enabled Tools: quantum-engine, data-analyzer, edit, write

  ✓ devops-engineer
    描述 / Description: 运维工程师 - 系统部署和监控
    启用工具 / Enabled Tools: bash, write, edit

默认 Agent / Default Agent: {config.get('default_agent', 'build')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. 自定义命令 / CUSTOM COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

可用命令 / Available Commands:

  /test
    描述 / Description: 运行完整的测试套件
    Agent: build

  /analyze
    描述 / Description: 分析交易系统的性能指标
    Agent: build

  /monitor
    描述 / Description: 启动实时监控模式
    Agent: build

  /deploy
    描述 / Description: 部署交易系统到生产环境
    Agent: build

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. 权限和工具 / PERMISSIONS & TOOLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

启用的工具 / Enabled Tools:
  ✓ write       - 创建文件 / Create files
  ✓ edit        - 编辑文件 / Edit files
  ✓ bash        - 执行命令 / Execute commands
  ✓ read        - 读取文件 / Read files

权限设置 / Permissions:
  bash: ask     - 执行前询问 / Ask before executing
  write: ask    - 修改前询问 / Ask before modifying

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. 安装和配置 / INSTALLATION & SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

快速开始 / Quick Start:

  1. 安装 OpenCode (如果未安装)
     curl -fsSL https://opencode.ai/install | bash

  2. 运行安装脚本
     bash scripts/install_opencode.sh

  3. 启动 OpenCode
     opencode

  4. 使用命令
     /monitor                    # 启动监控
     /analyze                    # 分析系统
     /test                       # 运行测试

关键文件 / Key Files:

  配置文件 / Config:
    - opencode.jsonc            主配置文件
    - ~/.config/opencode/opencode.json  全局配置

  文档 / Documentation:
    - docs/OPENCODE_SETUP.md    详细安装指南
    - AGENTS.md                 项目 Agent 定义

  脚本 / Scripts:
    - scripts/install_opencode.sh  自动安装脚本

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8. 下一步 / NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. 验证 OpenCode 安装
     opencode --version

  2. 初始化项目 (如需要)
     opencode /init

  3. 配置 API 提供商
     opencode /connect

  4. 查看可用 MCP 工具
     opencode mcp list

  5. 测试 MCP 连接
     opencode mcp debug trading-monitor

  6. 开始使用
     opencode run "获取投资组合状态"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9. 支持和资源 / SUPPORT & RESOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

官方资源 / Official Resources:
  - 官方文档: https://opencode.ai/docs
  - 配置参考: https://opencode.ai/config.json
  - GitHub: https://github.com/anomalyco/opencode
  - Discord: https://opencode.ai/discord

本地资源 / Local Resources:
  - 详细指南: docs/OPENCODE_SETUP.md
  - 项目指南: AGENTS.md
  - 快速参考: docs/OPENCODE_QUICK_REFERENCE.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ OpenCode 配置完成! / OpenCode configuration complete!

提交更改到 Git:
git add opencode.jsonc .opencode/ docs/OPENCODE_SETUP.md scripts/install_opencode.sh
git commit -m "feat: add OpenCode integration with MCP servers for trading system"

╚══════════════════════════════════════════════════════════════════════════════╝
"""
    
    return summary


if __name__ == "__main__":
    summary = generate_summary()
    print(summary)
    
    # 保存到文件
    output_file = Path("/root/comic_ai/OPENCODE_CONFIG_SUMMARY.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n✓ 配置总结已保存到: {output_file}")
