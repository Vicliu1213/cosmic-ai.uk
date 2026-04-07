# Ubuntu 移動版 OpenClaw 快速安裝指南

## 📱 針對 Ubuntu 移動設備優化

本指南專為 Ubuntu Touch 和其他 Ubuntu 移動設備設計。

---

## 🚀 快速開始

### 方式 1：一鍵安裝（推薦）

```bash
bash src/scripts/install-openclaw-ubuntu.sh
```

### 方式 2：使用 curl 遠程安裝

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### 方式 3：手動步驟

```bash
# 1. 更新系統包
sudo apt-get update

# 2. 安裝依賴
sudo apt-get install -y curl nodejs npm git

# 3. 安裝 OpenClaw
npm install -g openclaw

# 4. 驗證安裝
openclaw --version
```

---

## ✅ 系統要求

| 項目 | 需求 | 狀態 |
|------|------|------|
| 操作系統 | Ubuntu 20.04+ | ✓ 支持 |
| 架構 | ARM64 / x86_64 | ✓ 支持 |
| Node.js | v20+ | ✓ 自動安裝 |
| npm | v9+ | ✓ 自動安裝 |
| 存儲空間 | ~500MB | 最小要求 |

---

## 🔧 詳細安裝步驟

### 第 1 步：檢查系統

```bash
# 查看 Ubuntu 版本
lsb_release -a

# 查看系統架構
uname -m

# 查看 CPU 信息
cat /proc/cpuinfo
```

### 第 2 步：安裝必需依賴

如果你還沒有安裝基本工具：

```bash
# 更新包列表
sudo apt-get update

# 安裝必需的工具
sudo apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    python3 \
    make
```

### 第 3 步：安裝 Node.js

#### 方法 A：使用 NodeSource 倉庫（推薦）

```bash
# 添加 NodeSource 仓库
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# 安裝 Node.js
sudo apt-get install -y nodejs
```

#### 方法 B：使用 snap

```bash
# 安裝 Node.js snap
sudo snap install node --classic
```

#### 方法 C：使用發行版倉庫

```bash
# 直接從 Ubuntu 倉庫安裝
sudo apt-get install -y nodejs npm
```

### 第 4 步：驗證安裝

```bash
# 檢查 Node.js 版本
node --version

# 檢查 npm 版本
npm --version
```

### 第 5 步：安裝 OpenClaw

```bash
# 全局安裝 OpenClaw
npm install -g openclaw

# 驗證安裝
openclaw --version
```

---

## 🎯 運行 OpenClaw

安裝完成後，你可以通過以下方式使用 OpenClaw：

```bash
# 啟動 OpenClaw
openclaw

# 查看幫助信息
openclaw --help

# 查看詳細信息
openclaw info
```

---

## 🐛 故障排除

### 問題 1：sudo: npm 找不到

**症狀**：
```
sudo: npm: command not found
```

**解決方案**：
```bash
# npm 已安裝到當前用戶，使用以下命令：
npm install -g openclaw

# 如果需要全局安裝，配置 npm：
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
```

### 問題 2：權限被拒絕

**症狀**：
```
Error: EACCES: permission denied
```

**解決方案**：
```bash
# 方法 1：使用本地安裝
npm install openclaw

# 方法 2：更改 npm 所有權
sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) /usr/local/lib/node_modules
```

### 問題 3：Node.js 版本過低

**症狀**：
```
OpenClaw requires Node.js 20+
```

**解決方案**：
```bash
# 升級 Node.js
sudo apt-get update
sudo apt-get upgrade nodejs

# 或重新安裝最新版本
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 問題 4：網絡連接問題

**症狀**：
```
Cannot reach registry.npmjs.org
```

**解決方案**：
```bash
# 檢查網絡連接
ping -c 4 registry.npmjs.org

# 配置 npm 鏡像（使用阿里鏡像）
npm config set registry https://registry.npmmirror.com

# 恢復官方鏡像
npm config set registry https://registry.npmjs.org/
```

### 問題 5：磁盤空間不足

**症狀**：
```
ENOSPC: no space left on device
```

**解決方案**：
```bash
# 檢查磁盤使用情況
df -h

# 清理 npm 緩存
npm cache clean --force

# 移除舊版本
npm prune
```

---

## 📊 移動設備特定考慮

### 電池優化
```bash
# 在后臺運行時優化性能
openclaw --optimize-battery
```

### 網絡優化
```bash
# 使用較低的並發連接
npm config set fetch-timeout 60000
npm config set fetch-retry-mintimeout 10000
```

### 存儲優化
```bash
# 清理不必要的包
npm prune --production

# 清理緩存
npm cache clean --force
```

---

## 🔐 安全建議

1. **定期更新**
   ```bash
   npm update -g openclaw
   ```

2. **檢查依賴安全性**
   ```bash
   npm audit
   ```

3. **使用安全的鏡像**
   ```bash
   npm config set registry https://registry.npmjs.org/
   ```

---

## 📱 移動設備優化提示

### 對於低端設備
```bash
# 禁用某些高級功能以節省資源
export NODE_ENV=production
openclaw --minimal-mode
```

### 對於高端設備
```bash
# 啟用所有功能以獲得最佳性能
export NODE_ENV=development
openclaw --full-features
```

---

## 📞 獲得幫助

### 官方資源
- 網站：https://openclaw.ai
- 文檔：https://docs.openclaw.ai
- 常見問題：https://docs.openclaw.ai/start/faq
- GitHub：https://github.com/openclaw/openclaw

### 本地幫助
```bash
# 顯示完整幫助信息
openclaw --help

# 顯示版本信息
openclaw --version

# 顯示系統信息
openclaw info
```

---

## 🎉 下一步

安裝完成後：

1. ✅ 閱讀官方文檔
2. ✅ 配置你的設置
3. ✅ 開始使用 OpenClaw
4. ✅ 加入社區論壇

---

## 🚨 常見命令參考

```bash
# 安裝
npm install -g openclaw

# 更新
npm update -g openclaw

# 卸載
npm uninstall -g openclaw

# 查看已安裝的全局包
npm list -g --depth=0

# 檢查 openclaw 路徑
which openclaw

# 驗證安裝
openclaw --version
```

---

祝你使用愉快！🎊
