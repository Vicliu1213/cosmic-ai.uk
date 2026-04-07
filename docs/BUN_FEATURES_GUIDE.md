# Bun 功能完整指南 (v1.3.11)

## 📋 目錄
1. [核心功能概覽](#核心功能概覽)
2. [運行代碼 (bun run)](#運行代碼-bun-run)
3. [包管理 (bun install)](#包管理-bun-install)
4. [測試 (bun test)](#測試-bun-test)
5. [打包 (bun build)](#打包-bun-build)
6. [執行包 (bunx)](#執行包-bunx)
7. [其他命令](#其他命令)
8. [實用標誌](#實用標誌)
9. [性能提示](#性能提示)

---

## 核心功能概覽

Bun 是一個全合一的 JavaScript/TypeScript 工具包，包括：
- ⚡ **運行時**: 比 Node.js 快 4 倍的執行速度
- 📦 **包管理**: 比 npm 快 30 倍的依賴安裝
- 🧪 **測試**: Jest 兼容的測試運行器
- 📚 **打包**: 原生 JS/TS/JSX 打包器

---

## 運行代碼 (bun run)

### 基本用法

```bash
# 運行 TypeScript/JavaScript 文件（直接支持）
bun run script.ts
bun run script.jsx
bun run script.js

# 運行 package.json 中定義的腳本
bun run start
bun run test
bun run build

# 直接評估代碼
bun -e "console.log('Hello from Bun')"
bun -p "1 + 2"  # 打印結果
```

### 常用標誌

| 標誌 | 說明 | 示例 |
|------|------|------|
| `--watch` | 文件改變時自動重啟 | `bun run --watch server.ts` |
| `--hot` | 啟用熱重載 | `bun run --hot app.ts` |
| `--inspect` | 啟用調試器 | `bun run --inspect script.ts` |
| `-i` | 自動安裝缺失依賴 | `bun run -i script.ts` |
| `--no-install` | 禁用自動安裝 | `bun run --no-install app.ts` |
| `--env-file` | 加載 .env 文件 | `bun run --env-file=.env.local app.ts` |

### 調試選項

```bash
# 啟用調試器（需要 IDE 連接）
bun run --inspect script.ts
bun run --inspect-wait script.ts    # 等待調試器連接再運行
bun run --inspect-brk script.ts     # 在第一行設置斷點

# 性能分析
bun run --cpu-prof script.ts         # 生成 CPU 性能數據
bun run --heap-prof script.ts        # 生成堆快照
```

### 實際例子

```bash
# 用插件系統運行插件加載器
bun run -i /workspaces/cosmic-ai.uk/src/plugins/plugin_loader.py

# 監視模式開發服務器
bun run --watch --hot src/server.ts

# 評估並打印結果
bun -p "Math.sqrt(16)"  # 輸出: 4
```

---

## 包管理 (bun install)

### 基本安裝

```bash
# 安裝所有依賴
bun install

# 或簡寫
bun i

# 安裝特定包
bun install express
bun install @types/node --dev
bun install zod@^3.20.0

# 全局安裝
bun install -g typescript
```

### 添加/移除依賴

```bash
# 添加包
bun add express                  # 生產環境
bun add -d @types/node         # 開發環境
bun add --optional sharp       # 可選依賴
bun add --peer react           # 對等依賴

# 移除包
bun remove express
bun rm express

# 更新包
bun update express              # 更新單個
bun update                      # 更新所有
```

### 重要標誌

| 標誌 | 說明 |
|------|------|
| `-p, --production` | 跳過 devDependencies |
| `-d, --dev` | 添加到 devDependencies |
| `-E, --exact` | 精確版本（不用範圍） |
| `--frozen-lockfile` | 禁止修改鎖文件 |
| `-f, --force` | 強制重新安裝所有 |
| `--dry-run` | 模擬安裝，不實際改變 |
| `--no-cache` | 忽略緩存 |
| `--audit` | 檢查已安裝包的漏洞 |
| `--outdated` | 顯示過時的包 |

### 工作區支持

```bash
# 在所有工作區包中運行
bun install --workspaces

# 為特定工作區過濾
bun install --filter=@myapp/core
```

### 檢查命令

```bash
# 查看包信息
bun info tailwindcss

# 查看為什麼安裝了包
bun why elysia

# 檢查漏洞
bun audit

# 檢查過時的包
bun outdated

# 查看本地鏈接的包
bun link [<package>]
bun unlink [<package>]
```

---

## 測試 (bun test)

### 基本使用

```bash
# 運行所有測試
bun test

# 運行特定文件的測試
bun test src/tests

# 運行匹配模式的測試文件
bun test foo bar  # 文件名包含 "foo" 或 "bar"
```

### 運行特定測試

```bash
# 運行名稱匹配的測試
bun test --test-name-pattern "add function"

# 只運行 test.only() 標記的測試
bun test --only

# 包括 test.todo() 標記的測試
bun test --todo

# 只顯示失敗的測試
bun test --only-failures
```

### 重要標誌

| 標誌 | 說明 | 示例 |
|------|------|------|
| `--timeout` | 測試超時（毫秒） | `bun test --timeout=10000` |
| `--retry` | 失敗重試次數 | `bun test --retry=3` |
| `--rerun-each` | 重複運行每個測試 | `bun test --rerun-each=5` |
| `--concurrent` | 並發運行所有測試 | `bun test --concurrent` |
| `--randomize` | 隨機順序運行 | `bun test --randomize` |
| `--seed` | 設置隨機種子 | `bun test --randomize --seed=12345` |
| `--bail` | N 個失敗後退出 | `bun test --bail=5` |
| `--max-concurrency` | 最大並發數 | `bun test --max-concurrency=10` |

### 代碼覆蓋率

```bash
# 生成覆蓋率報告
bun test --coverage

# 指定報告格式
bun test --coverage --coverage-reporter=text,lcov

# 指定覆蓋目錄
bun test --coverage --coverage-dir=./reports
```

### 測試報告

```bash
# 不同的報告格式
bun test --reporter=dots              # 點狀報告
bun test --reporter=junit --reporter-outfile=test-results.xml

# 隱藏通過的測試，只看失敗
bun test --only-failures
```

### 例子

```bash
# 開發時監視測試
bun test --watch

# 高度並發運行
bun test --concurrent --max-concurrency=20

# 完整的 CI 設置
bun test --coverage --reporter=junit --reporter-outfile=test-results.xml
```

---

## 打包 (bun build)

### 基本打包

```bash
# 打包單個文件
bun build ./src/index.ts

# 打包多個入口點
bun build ./index.jsx ./lib/worker.ts

# 指定輸出文件
bun build --outfile=bundle.js ./src/index.ts

# 指定輸出目錄
bun build --outdir=dist ./src/index.ts ./src/worker.ts
```

### 打包目標

```bash
# 為瀏覽器打包
bun build --target=browser ./src/index.ts

# 為 Bun 運行時打包
bun build --target=bun --outfile=server.js ./server.ts

# 為 Node.js 打包
bun build --target=node ./src/index.ts
```

### 最小化和優化

```bash
# 啟用所有最小化
bun build --minify ./src/index.ts

# 分別最小化
bun build --minify-syntax ./src/index.ts
bun build --minify-whitespace ./src/index.ts
bun build --minify-identifiers ./src/index.ts

# 保留名稱（用於調試）
bun build --minify --keep-names ./src/index.ts

# 生產模式
bun build --production ./src/index.ts
```

### 進階選項

| 選項 | 說明 |
|------|------|
| `--compile` | 生成獨立可執行文件 |
| `--watch` | 監視文件改變 |
| `--splitting` | 啟用代碼分割 |
| `--sourcemap` | 生成源圖（linked/inline/external/none） |
| `--no-bundle` | 只轉譯，不打包 |
| `--format=esm` | ESM 格式輸出 |
| `--format=cjs` | CommonJS 格式輸出 |
| `--format=iife` | IIFE 格式輸出 |
| `--banner` | 添加文件頭 |
| `--footer` | 添加文件尾 |
| `--external` | 排除模塊（如 -e react） |

### 創建可執行文件

```bash
# 生成獨立可執行文件
bun build --compile --outfile=my-app ./cli.ts

# 包含 .env 文件
bun build --compile --compile-autoload-dotenv ./app.ts

# 跨平台編譯（指定執行文件）
bun build --compile --compile-executable-path=/path/to/bun ./app.ts
```

### Windows 特定選項

```bash
bun build --compile \
  --windows-icon=icon.ico \
  --windows-title="My App" \
  --windows-publisher="My Company" \
  --windows-version="1.0.0.0" \
  --windows-description="My application" \
  --windows-copyright="© 2024"
```

### 使用示例

```bash
# 開發模式監視
bun build --watch --outdir=dist ./src/index.ts

# 生產打包
bun build --production --minify --splitting --outdir=dist ./src/index.ts

# 為 Bun 服務器優化
bun build --target=bun --production --outfile=dist/server.js ./src/server.ts

# React + TypeScript 項目
bun build --react-fast-refresh --target=browser --outfile=app.js ./src/App.tsx
```

---

## 執行包 (bunx)

### 基本使用

```bash
# 執行包的 CLI 命令
bunx prisma migrate
bunx prettier ./src/index.ts
bunx vite dev

# 指定包版本
bunx eslint@8.0.0 ./src

# 當包名不同於命令名
bunx -p @angular/cli ng new my-app

# 強制使用 Bun 運行
bunx --bun vite dev
```

### 常用標誌

| 標誌 | 說明 |
|------|------|
| `--bun` | 強制使用 Bun 而非 Node.js |
| `-p, --package` | 包名不同於命令名時指定 |
| `--no-install` | 跳過安裝（若未安裝則失敗） |
| `--verbose` | 詳細輸出 |
| `--silent` | 抑制輸出 |

### 常見使用

```bash
# 代碼檢查和格式化
bunx eslint ./src
bunx prettier --write ./src
bunx stylelint ./styles

# 數據庫工具
bunx prisma studio
bunx prisma migrate dev

# 構建工具
bunx vite build
bunx next build

# 開發服務器
bunx --bun vite dev
bunx --bun next dev
```

---

## 其他命令

### 項目初始化

```bash
# 創建新 Bun 項目
bun init

# 使用模板創建（如 Next.js）
bun create next-app my-app
bun create vite-app my-app
```

### REPL 環境

```bash
# 啟動交互式 REPL
bun repl

# 在 REPL 中執行 TypeScript 代碼
import { readFileSync } from 'fs'
const content = readFileSync('./file.txt', 'utf-8')
console.log(content)
```

### 執行 Shell 腳本

```bash
# 直接執行 shell 腳本
bun exec ./script.sh

# 或在 package.json 中使用
bun run my-script  # 執行定義的腳本
```

### 升級 Bun

```bash
# 升級到最新版本
bun upgrade

# 查看版本
bun --version
bun --revision  # 包含提交 hash
```

### 反饋和信息

```bash
# 提供反饋給 Bun 團隊
bun feedback ./file1 ./file2

# 查看包信息
bun info express

# 查看為什麼安裝了包
bun why lodash

# 發布包到 npm
bun publish

# 為包打補丁
bun patch lodash
```

---

## 實用標誌

### 全局標誌

| 標誌 | 說明 |
|------|------|
| `-h, --help` | 顯示幫助信息 |
| `-v, --version` | 顯示版本 |
| `--verbose` | 詳細輸出 |
| `--quiet` | 簡化輸出 |
| `--cwd=<path>` | 改變工作目錄 |
| `--config=<path>` | 指定配置文件路徑 |

### 調試和性能

| 標誌 | 用途 |
|------|------|
| `--inspect` | 啟用調試器 |
| `--inspect-wait` | 等待調試器連接 |
| `--inspect-brk` | 第一行設置斷點 |
| `--cpu-prof` | CPU 性能分析 |
| `--heap-prof` | 堆快照生成 |
| `--cpu-prof-md` | Markdown 格式的 CPU 分析 |
| `--heap-prof-md` | Markdown 格式的堆分析 |

### 環境控制

| 標誌 | 說明 |
|------|------|
| `--env-file=<path>` | 加載 .env 文件 |
| `--no-env-file` | 禁用自動加載 .env |
| `--prefer-offline` | 優先使用緩存 |
| `--prefer-latest` | 總是檢查最新版本 |

### 資源優化

| 標誌 | 說明 |
|------|------|
| `--smol` | 減少內存使用，更頻繁的垃圾回收 |
| `--no-addons` | 禁用原生模塊 |
| `--expose-gc` | 暴露 gc() 方法 |

---

## 性能提示

### 1. 快速開發設置

```bash
# 使用 --hot 進行實時重載
bun run --hot --watch src/server.ts

# 自動安裝依賴（開發時）
bun run -i src/app.ts
```

### 2. 優化生產打包

```bash
# 完整優化
bun build \
  --production \
  --minify \
  --splitting \
  --sourcemap=external \
  --target=browser \
  --outdir=dist \
  ./src/index.ts
```

### 3. 快速測試

```bash
# 並發運行最大化
bun test --concurrent --max-concurrency=20

# 隨機順序檢測間歇性故障
bun test --randomize --retry=3
```

### 4. 包管理優化

```bash
# 冷啟動加速
bun install

# 檢查漏洞
bun audit

# 清理過時包
bun remove unused-package
```

### 5. 調試和分析

```bash
# CPU 性能分析
bun run --cpu-prof server.ts
# 查看結果在 CPU.0001.cpuprofile

# 堆分析
bun run --heap-prof server.ts
# 查看結果在 .heapsnapshot 文件
```

---

## 配置文件

### bunfig.toml

在項目根目錄創建 `bunfig.toml` 自定義 Bun 配置：

```toml
# 包管理器設置
[install]
production = false
exact = false

# 構建設置
[build]
target = "browser"
format = "esm"
minify = "all"

# 運行時設置
[runtime]
alwaysFreeze = true
```

---

## 常用工作流

### 開發工作流

```bash
# 1. 創建項目
bun create vite-app my-app
cd my-app

# 2. 安裝依賴
bun install

# 3. 開發（監視模式）
bun run --watch --hot dev

# 4. 測試（監視模式）
bun test --watch
```

### CI/CD 工作流

```bash
# 1. 安裝（生產環境）
bun install --production

# 2. 運行測試
bun test --coverage --reporter=junit --reporter-outfile=test-results.xml

# 3. 構建
bun build --production --outdir=dist ./src/index.ts

# 4. 檢查漏洞
bun audit
```

### 部署工作流

```bash
# 1. 創建可執行文件
bun build --compile --outfile=app ./src/server.ts

# 2. 分發 `app` 可執行文件
# 無需 Node.js，可直接運行

# 3. 使用 systemd 或 docker 運行
./app
```

---

## 快速參考卡

```bash
# 運行代碼
bun run script.ts                    # 運行 TypeScript
bun run --watch server.ts           # 監視模式
bun run --hot app.ts                # 熱重載

# 包管理
bun install                          # 安裝依賴
bun add express                      # 添加包
bun remove express                   # 移除包
bun audit                            # 檢查漏洞

# 測試
bun test                             # 運行所有測試
bun test --watch                     # 監視模式
bun test --coverage                  # 覆蓋率

# 打包
bun build ./src/index.ts            # 打包
bun build --production ./src/index.ts # 優化生產
bun build --compile ./app.ts        # 創建可執行文件

# 執行命令
bunx prisma migrate                  # 執行 npm 包 CLI
bunx vite build                      # 運行構建工具

# 交互
bun repl                             # 啟動 REPL
bun --version                        # 版本信息
bun --help                           # 幫助文本
```

---

**最後更新**: 2024 年 4 月 6 日  
**Bun 版本**: 1.3.11
