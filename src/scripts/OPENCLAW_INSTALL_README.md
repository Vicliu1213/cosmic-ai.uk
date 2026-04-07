# OpenClaw 安装指南

## 快速开始

### 方法 1：运行本地脚本
```bash
bash src/scripts/install-openclaw.sh
```

### 方法 2：从远程运行官方安装脚本
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### 方法 3：使用 curl 和本地脚本
```bash
bash src/scripts/install-openclaw.sh --no-onboard
```

## 支持的选项

本脚本支持以下环境变量进行配置：

| 变量 | 值 | 说明 |
|------|-----|------|
| `OPENCLAW_VERSION` | latest/next/版本号 | OpenClaw 版本（默认：latest） |
| `OPENCLAW_NO_PROMPT` | 0/1 | 禁用提示（默认：0） |
| `OPENCLAW_NO_ONBOARD` | 0/1 | 跳过入门（默认：0） |
| `OPENCLAW_VERBOSE` | 0/1 | 启用调试输出（默认：0） |

## 系统要求

- **操作系统**：macOS 或 Linux（包括 WSL）
- **Node.js**：v20+ 或更高
- **npm**：npm 9+ 或更高
- **包管理器**：apt-get（Debian/Ubuntu）、dnf（Fedora）、yum（CentOS）或 Homebrew（macOS）

## 脚本功能

### 自动检测和安装

脚本会自动：

1. ✅ 检测操作系统（macOS 或 Linux）
2. ✅ 检查 Node.js 是否已安装
3. ✅ 检查 Git 是否已安装
4. ✅ 如果需要，自动安装 Node.js
5. ✅ 如果需要，自动安装 Homebrew（macOS）
6. ✅ 通过 npm 全局安装 OpenClaw
7. ✅ 显示安装成功的消息和下一步说明

### 高级功能

- **gum UI 支持**：如果可用，使用漂亮的终端 UI 显示进度
- **下载重试**：内置下载失败重试机制
- **Homebrew 自动安装**：在 macOS 上自动安装 Homebrew（如需）
- **Node.js 自动升级**：自动检测并升级到所需版本
- **临时文件清理**：脚本退出时自动清理临时文件

## 使用示例

### 标准安装
```bash
bash src/scripts/install-openclaw.sh
```

### 无交互模式（适用于 CI/CD）
```bash
OPENCLAW_NO_PROMPT=1 bash src/scripts/install-openclaw.sh
```

### 跳过入门流程
```bash
OPENCLAW_NO_ONBOARD=1 bash src/scripts/install-openclaw.sh
```

### 启用详细输出
```bash
OPENCLAW_VERBOSE=1 bash src/scripts/install-openclaw.sh
```

### 安装特定版本
```bash
OPENCLAW_VERSION=1.0.0 bash src/scripts/install-openclaw.sh
```

## 下一步

安装完成后，你可以：

```bash
# 运行 OpenClaw
openclaw

# 查看帮助
openclaw --help

# 查看版本
openclaw --version
```

## 故障排除

### 问题：npm 未找到

**解决方案**：确保 Node.js 已正确安装
```bash
node --version
npm --version
```

### 问题：权限被拒绝

**解决方案**：确保脚本有执行权限
```bash
chmod +x src/scripts/install-openclaw.sh
```

### 问题：在 macOS 上安装失败

**解决方案**：检查 Homebrew 是否已安装
```bash
brew --version
```
如果未安装，脚本会自动安装。

### 问题：Node.js 版本过低

**解决方案**：升级 Node.js 到 v20 或更高
```bash
# macOS
brew upgrade node

# Linux
sudo apt update && sudo apt upgrade nodejs
```

## 日志和调试

如果安装失败，启用详细模式查看更多信息：

```bash
OPENCLAW_VERBOSE=1 bash src/scripts/install-openclaw.sh
```

## 安全性

该脚本：
- ✅ 使用 HTTPS 协议进行所有下载
- ✅ 验证下载文件的 SHA256 校验和
- ✅ 不存储任何敏感信息
- ✅ 临时文件会自动清理
- ✅ 支持离线安装（使用本地脚本）

## 许可证

OpenClaw 是专有软件。请查看官方网站了解更多信息。

## 参考资源

- 官方网站：https://openclaw.ai
- 文档：https://docs.openclaw.ai
- FAQ：https://docs.openclaw.ai/start/faq
