# Ubuntu 行動版 OpenClaw 快速安裝指令

## 🚀 最簡單的方式 - 複製並在終端粘貼

### 方式 1：一行命令（推薦）

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### 方式 2：分步安裝

```bash
# 1. 更新系統包
sudo apt-get update

# 2. 安裝依賴
sudo apt-get install -y curl wget git build-essential python3 make g++ cmake

# 3. 安裝 Node.js (方法A - NodeSource)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 或方法B - 使用 snap
# sudo snap install node --classic

# 4. 驗證安裝
node --version
npm --version

# 5. 安裝 OpenClaw
npm install -g openclaw

# 6. 驗證 OpenClaw
openclaw --version
```

### 方式 3：無交互式安裝

```bash
curl -fsSL https://openclaw.ai/install.sh | OPENCLAW_NO_PROMPT=1 bash
```

---

## 📋 逐步詳細說明

### 第 1 步：更新系統
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 第 2 步：安裝基本工具
```bash
sudo apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    python3 \
    make \
    g++ \
    cmake
```

### 第 3 步：安裝 Node.js

**推薦方式 - NodeSource 倉庫（Node 20 LTS）：**

```bash
# 下載設置腳本
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# 安裝 Node.js
sudo apt-get install -y nodejs

# 驗證
node -v
npm -v
```

**備選方式 - 使用 Snap：**

```bash
sudo snap install node --classic
node -v
npm -v
```

**備選方式 - 系統倉庫：**

```bash
sudo apt-get install -y nodejs npm

# 可能版本較舊，如需新版本，使用上面的 NodeSource 方式
```

### 第 4 步：安裝 OpenClaw

```bash
# 全局安裝 OpenClaw
npm install -g openclaw

# 驗證安裝
openclaw --version

# 查看幫助
openclaw --help

# 運行 OpenClaw
openclaw
```

---

## ✅ 驗證安裝

運行以下命令驗證：

```bash
# 檢查所有工具
echo "=== Node.js ===" && node --version
echo "=== npm ===" && npm --version
echo "=== Git ===" && git --version
echo "=== OpenClaw ===" && openclaw --version
```

---

## 🐛 常見問題

### Q1：sudo: npm 找不到命令

**A：** npm 是全局安裝的，不需要 sudo。直接使用：

```bash
npm install -g openclaw
```

### Q2：權限被拒絕 (EACCES)

**A：** 配置 npm 以使用本地目錄：

```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Q3：找不到 apt-get

**A：** 可能你的 Ubuntu 版本使用了不同的包管理器。檢查：

```bash
# 對於基於 Fedora/CentOS 的系統
which dnf || which yum

# 對於基於 Alpine 的系統
which apk
```

### Q4：Node.js 版本過低

**A：** 升級到最新版本：

```bash
# 移除舊版本
sudo apt-get remove nodejs npm -y

# 重新安裝最新版本
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Q5：網絡連接問題

**A：** 配置 npm 使用鏡像：

```bash
# 使用淘寶鏡像
npm config set registry https://registry.npmmirror.com

# 或使用阿里鏡像
npm config set registry https://mirrors.aliyun.com/npm/

# 恢復官方鏡像
npm config set registry https://registry.npmjs.org/
```

---

## 📱 Ubuntu 行動版特定建議

### 省電設置
```bash
# 設置為省電模式
export NODE_ENV=production
openclaw --optimize-battery
```

### 低端設備優化
```bash
# 禁用某些高級功能
export NODE_ENV=production
openclaw --minimal-mode
```

### 網絡優化
```bash
# 設置更長的超時時間
npm config set fetch-timeout 120000
```

---

## 🎯 完成後

```bash
# 啟動 OpenClaw
openclaw

# 首次運行會進行設置
# 按照提示完成配置
```

---

## 📞 獲得幫助

- 官方網站：https://openclaw.ai
- 文檔：https://docs.openclaw.ai
- FAQ：https://docs.openclaw.ai/start/faq
- GitHub：https://github.com/openclaw/openclaw

---

## 🔗 快捷參考

```bash
# 列出全局包
npm list -g --depth=0

# 更新 OpenClaw
npm update -g openclaw

# 卸載 OpenClaw
npm uninstall -g openclaw

# 清理 npm 緩存
npm cache clean --force

# 檢查 npm 配置
npm config list -l
```

---

祝安裝順利！🎉

如有問題，請參考官方文檔或在 GitHub 提出問題。
