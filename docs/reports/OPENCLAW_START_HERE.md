# OpenClaw 安裝 - 完整說明

你好！我已經為你的 Ubuntu 行動版準備好了完整的 OpenClaw 安裝套件。

## 🎯 立即開始

### 最簡單的方式（推薦）

在你的 Ubuntu 行動版終端複製並粘貼這行命令：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**就這樣！** 安裝器會自動下載所有必需的軟件並安裝 OpenClaw。

---

## 📁 本專案中提供的文件

### 根目錄
1. **OPENCLAW_QUICK_INSTALL.md** ← 👈 **你應該先看這個**
   - 複製粘貼安裝命令
   - 逐步詳細說明
   - 常見問題解答

2. **OPENCLAW_INSTALL.md**
   - 快速參考
   - 基本使用說明

3. **openclaw-install.sh**
   - 自定義 Bash 安裝腳本
   - 下載官方安裝器並運行

4. **openclaw-install.py**
   - Python 版本的安裝器
   - 支持完整的依賴檢查和自動安裝

### src/scripts 目錄

#### 安裝腳本
1. **install-openclaw.sh**
   - 通用安裝腳本
   - 支持所有 Bash 環境

2. **install-openclaw-ubuntu.sh**
   - Ubuntu 移動版優化版本
   - 自動檢測和安裝依賴

3. **verify-openclaw-install.sh**
   - 驗證安裝是否成功
   - 檢查所有依賴

#### 文檔和配置
1. **OPENCLAW_INSTALL_README.md**
   - 詳細的安裝指南
   - 高級選項說明

2. **OPENCLAW_UBUNTU_MOBILE_GUIDE.md**
   - Ubuntu 行動版專用指南
   - 移動設備優化建議
   - 電池/網絡優化

3. **.openclaw-install.conf**
   - 安裝配置文件
   - 可自定義的選項

---

## 🚀 使用方式

### 方式 1：最簡單（推薦）

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### 方式 2：本地腳本（需要 Bash）

```bash
# 在項目根目錄
bash openclaw-install.sh

# 或使用 Ubuntu 優化版
bash src/scripts/install-openclaw-ubuntu.sh
```

### 方式 3：Python 版本

```bash
python3 openclaw-install.py
```

### 方式 4：手動逐步安裝

詳見 `OPENCLAW_QUICK_INSTALL.md` 中的「分步安裝」部分

---

## ✅ 驗證安裝

安裝完成後運行：

```bash
# 檢查版本
openclaw --version

# 運行 OpenClaw
openclaw

# 查看幫助
openclaw --help
```

或使用本項目提供的驗證腳本：

```bash
bash src/scripts/verify-openclaw-install.sh
```

---

## 📋 安裝流程

```
1. 更新系統包
   ↓
2. 安裝依賴 (curl, git, build-essential 等)
   ↓
3. 安裝 Node.js (v20+)
   ↓
4. 安裝 npm (v9+)
   ↓
5. 通過 npm 全局安裝 OpenClaw
   ↓
6. 驗證安裝
   ↓
7. 運行 openclaw
```

---

## 🐛 如果遇到問題

### 常見錯誤和解決方案

**錯誤 1: "curl: command not found"**
```bash
sudo apt-get install -y curl
```

**錯誤 2: "npm: command not found"**
- Node.js 未正確安裝
- 重新運行 NodeSource 設置：
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**錯誤 3: "Permission denied"**
```bash
# 配置 npm 使用本地目錄
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
```

**錯誤 4: "Network error"**
```bash
# 使用鏡像
npm config set registry https://registry.npmmirror.com
```

詳細的故障排除指南見：`OPENCLAW_QUICK_INSTALL.md`

---

## 📚 更多文檔

| 文件 | 用途 |
|------|------|
| OPENCLAW_QUICK_INSTALL.md | 👈 快速安裝命令和詳細步驟 |
| OPENCLAW_INSTALL.md | 簡介和快速參考 |
| src/scripts/OPENCLAW_INSTALL_README.md | 詳細的功能說明 |
| src/scripts/OPENCLAW_UBUNTU_MOBILE_GUIDE.md | Ubuntu 行動版專用 |

---

## 🎯 下一步

### 步驟 1：安裝 OpenClaw

複製這行命令到你的終端：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### 步驟 2：驗證安裝

```bash
openclaw --version
```

### 步驟 3：啟動 OpenClaw

```bash
openclaw
```

### 步驟 4：享受

根據提示完成初始配置並開始使用 OpenClaw！

---

## 💡 提示

- **首次安裝可能需要時間**：根據網絡速度，安裝可能需要 5-10 分鐘
- **需要管理員權限**：安裝某些系統包時需要 sudo 密碼
- **無交互模式**：可以使用 `--no-prompt` 選項跳過提示
- **離線模式**：安裝後，OpenClaw 可以在有限的離線環境下運行

---

## 🔗 官方資源

- 網站：https://openclaw.ai
- 文檔：https://docs.openclaw.ai
- FAQ：https://docs.openclaw.ai/start/faq
- GitHub：https://github.com/openclaw/openclaw

---

## ✨ 這個項目為你準備了什麼

✅ **3 個安裝腳本**（Bash、Ubuntu 優化版、Python 版本）
✅ **4 個詳細文檔**（快速安裝、詳細指南、Ubuntu 指南、配置說明）
✅ **完整的驗證工具**（檢查安裝狀態的腳本）
✅ **故障排除指南**（常見問題和解決方案）
✅ **針對 Ubuntu 行動版的優化**（特別考慮移動設備）

---

## 🎉 祝你安裝順利！

如有任何問題，請參考 `OPENCLAW_QUICK_INSTALL.md` 或官方文檔。

**立即開始：**

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

---

最後更新：2026-04-05
