# OpenClaw 安裝 - 根目錄

## 快速開始

根目錄已有 OpenClaw 安裝腳本。只需運行：

```bash
bash openclaw-install.sh
```

## 説明

- **openclaw-install.sh** - 下載官方安裝器並運行
- **src/scripts/install-openclaw.sh** - 自訂安裝腳本
- **src/scripts/install-openclaw-ubuntu.sh** - Ubuntu 移動版優化
- **src/scripts/verify-openclaw-install.sh** - 驗證安裝

## 使用選項

```bash
# 基本安裝
bash openclaw-install.sh

# 不要求用戶輸入
bash openclaw-install.sh --no-prompt

# 跳過入門
bash openclaw-install.sh --no-onboard

# 詳細輸出
bash openclaw-install.sh --verbose
```

## 系統需求

- macOS 或 Linux
- Node.js v22+
- npm v9+
- curl 或 wget

## 驗證安裝

```bash
# 檢查是否安裝成功
bash src/scripts/verify-openclaw-install.sh

# 或直接運行
openclaw --version
```

## 下一步

```bash
openclaw
```

---

祝安裝順利！🎉
