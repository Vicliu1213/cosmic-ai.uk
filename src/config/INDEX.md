# 配置文件完整索引 - Configuration Complete Index

## 📋 目錄概覽

此目錄包含 Cosmic AI 系統的所有配置文件，組織為層級化結構，便於管理和維護。

**遷移完成日期**: 2026-04-06  
**遷移狀態**: ✓ 完成  
**文件總數**: 93 個  
**目錄總數**: 64 個

---

## 🏗️ 目錄結構

### 1. 系統配置 (`systems/`)

15個突破協同理論系統的配置文件。

| 系統 | 目錄 | 配置文件 | 說明 |
|------|------|--------|------|
| 1 | `main_system/` | `main_system_config.yaml`, `cosmic_engine.yaml` | 主系統配置，定義系統特性和運行時參數 |
| 2 | `enhanced_compression/` | `compression_optimizer.yaml`, `compression_control.yaml` | 增強壓縮系統，包含能量管理和量子優化 |
| 3 | `performance/` | `performance_config.yaml` | 性能管理配置 |
| 4 | `optimization/` | `optimization_config.yaml` | 優化系統配置 |
| 5 | `quantum_analysis/` | - | 量子分析系統（待補充） |
| 6 | `immune_system/` | - | 免疫系統（待補充） |
| 7 | `intelligent_agents/` | - | 智能代理系統（待補充） |
| 8 | `bio_evolution/` | - | 生物進化系統（待補充） |
| 9 | `experience_learning/` | - | 經驗學習系統（待補充） |
| 10 | `profit_optimization/` | - | 利潤優化系統（待補充） |
| 11 | `offline_processing/` | - | 離線處理系統（待補充） |
| 12 | `energy_management/` | - | 能量管理系統（待補充） |
| 13 | `quantum_coherence/` | - | 量子相幹性系統（待補充） |
| 14 | `io_management/` | - | 輸入輸出管理系統（待補充） |
| 15 | `monitoring/` | - | 監控系統（待補充） |

### 2. 交易所配置 (`exchanges/`)

支持多個主流交易所的統一配置接口。

```
exchanges/
├── common/              # 統一交易所配置和客戶端
│   └── exchange_config.py        # 支持: Binance, OKX, Bybit, Bitget
├── binance/             # 幣安特定配置（待補充）
├── okx/                 # 歐易特定配置（待補充）
├── bybit/               # Bybit特定配置（待補充）
└── bitget/              # Bitget特定配置（待補充）
```

### 3. 基礎設施配置 (`infrastructure/`)

系統部署、數據庫、網絡等基礎設施配置。

```
infrastructure/
├── deployment/          # 部署配置 (deployment.yaml)
│                       # 包含環境配置、容器、擴展、監控
├── backup/             # 備份配置 (backup_config.yaml)
├── networking/         # 網絡配置 (network_config.yaml)
├── database/           # 數據庫配置（待補充）
├── caching/            # 緩存配置（待補充）
└── logging/            # 日誌配置（待補充）
```

### 4. 交易配置 (`trading/`)

交易策略、風險管理、回測等配置。

```
trading/
├── strategies/         # 交易策略配置（待補充）
├── risk_management/    # 風險管理配置（待補充）
├── backtest/          # 回測配置（待補充）
└── portfolio/         # 投資組合配置（待補充）
```

### 5. 環境配置 (`environments/`)

開發、預發佈、生產環境的配置。

```
environments/
├── development/        # 開發環境 (config.json)
├── staging/           # 預發佈環境 (config.json)
└── production/        # 生產環境 (config.json)
```

### 6. 配置示例 (`examples/`)

各種配置示例和遷移指南。

```
examples/
├── complete/          # 完整配置示例 (config.yaml)
├── custom/            # 自定義配置示例 (config.yaml)
├── migration/         # 遷移指南 (MIGRATION_GUIDE.md)
└── README.md
```

### 7. 提示詞模板 (`templates/`)

AI 提示詞模板和配置模板。

```
templates/
├── default_prompt_template.py
├── enterprise/        # 企業級模板 (config.json)
├── minimal/          # 最小化模板 (config.json)
├── quick-start/      # 快速開始模板 (config.json)
├── README.md
└── __init__.py
```

### 8. 配置驗證模式 (`schemas/`)

配置文件格式驗證的 JSON Schema。

```
schemas/
├── api/               # API 模式 (api_schema.json)
├── engine/            # 引擎模式 (engine_schema.json)
├── system/            # 系統模式 (system_schema.json)
├── trading/           # 交易模式 (trading_schema.json)
├── README.md
└── __init__.py
```

### 9. 備份目錄 (`backups/`)

配置文件備份的存儲位置。

```
backups/
├── daily/             # 日備份
├── weekly/            # 週備份
├── monthly/           # 月備份
└── README.md
```

### 10. API 密鑰 (`api_keys/`)

API 密鑰和認證信息管理。

```
api_keys/
├── binance.py         # Binance API 配置
├── llm.py            # LLM API 配置
└── __init__.py
```

### 11. 配置加載器 (`loaders/`)

配置文件加載和管理的代碼。

```
loaders/
├── config_loader.py   # 配置加載器實現
└── __init__.py
```

### 12. 監控配置 (`monitoring/`)

監控和告警配置。

```
monitoring/
└── monitoring_config.yaml
```

### 13. 安全配置 (`security/`)

安全、認證、加密和隱私配置。

```
security/
├── security_config.yaml      # 安全配置
├── privacy_config.yaml       # 隱私配置
└── __init__.py
```

### 14. 插件配置 (`plugins/`)

系統插件的配置文件。

```
plugins/
└── plugins_config.json
```

### 15. 根級配置文件

```
├── docker-compose.yml              # Docker 容器編排
├── environment.yml                 # Conda 環境配置
├── comic-ai-daemon.service         # Systemd 服務配置
├── .pre-commit-config.yaml         # Git 預提交鉤子
│
├── CONFIG_REGISTRY.py              # 配置註冊表
├── CONFIG_MAPPING.txt              # 配置映射表
├── CONFIG_INDEX.md                 # 配置索引
├── CONFIG_README.md                # 配置說明
├── DATA_ALIGNMENT.md               # 數據對齐文檔
├── MIGRATION_REPORT.txt            # 初始遷移報告
├── ROOT_CONFIG_MIGRATION_REPORT.txt # 根目錄遷移報告
└── INDEX.md                        # 本文件
```

---

## 📖 文檔指南

### 快速導航

- **[MIGRATION_REPORT.txt](MIGRATION_REPORT.txt)** - /.config/ 遷移報告
- **[ROOT_CONFIG_MIGRATION_REPORT.txt](ROOT_CONFIG_MIGRATION_REPORT.txt)** - /config/ 遷移報告
- **[CONFIG_MAPPING.txt](CONFIG_MAPPING.txt)** - 配置文件對應映射表
- **[CONFIG_REGISTRY.py](CONFIG_REGISTRY.py)** - 配置註冊表和層級結構
- **[DATA_ALIGNMENT.md](DATA_ALIGNMENT.md)** - 數據對齐文檔

### 具體位置指南

| 需要 | 位置 |
|------|------|
| 系統基礎配置 | `systems/main_system/` |
| 交易所配置 | `exchanges/common/` |
| 部署配置 | `infrastructure/deployment/` |
| 備份設置 | `infrastructure/backup/` |
| 監控告警 | `monitoring/` |
| 安全策略 | `security/` |
| 環境切換 | `environments/` |
| 配置示例 | `examples/` |
| 驗證規則 | `schemas/` |

---

## 🔄 配置加載優先級

系統加載配置時，優先級如下（從高到低）：

1. **環境變量** (最高優先級)
   ```bash
   export CONFIG_MAIN_SYSTEM_DEBUG=true
   ```

2. **命令行參數**
   ```bash
   --config=/src/config/systems/main_system/
   ```

3. **用戶配置文件**
   ```
   /src/config/*.yaml
   ```

4. **系統特定配置**
   ```
   /src/config/systems/<system>/config.yaml
   ```

5. **默認配置**
   ```
   /src/config/default.yaml
   ```

6. **硬編碼默認值** (最低優先級)

---

## 🔧 配置加載流程

```
系統啟動
   ↓
ConfigLoader.load_config()
   ├── 讀取 /src/config/systems/main_system/main_system_config.yaml
   ├── 讀取 /src/config/systems/*/config.yaml
   ├── 讀取 /src/config/infrastructure/*/config.yaml
   └── 讀取 /src/config/trading/*/config.yaml
   ↓
ConfigLoader.override_from_env()
   ├── 檢查環境變量
   └── 覆蓋相應配置
   ↓
Config 單例初始化
   ├── APIKeysConfig
   ├── BinanceConfig
   ├── LLMConfig
   ├── TradingConfig
   ├── RiskConfig
   ├── BacktestConfig
   ├── RedisConfig
   └── LoggingConfig
   ↓
應用使用配置
   └── get_config() 獲取全局配置實例
```

---

## 📝 文件格式說明

### YAML (.yaml/.yml)
- 人類可讀的配置格式
- 層級結構使用縮進表示
- 支持註釋
- **11 個**配置文件使用此格式

### JSON (.json)
- 輕量級數據格式
- 結構化格式
- **8 個**配置文件使用此格式

### Python (.py)
- 可執行的配置模塊
- 支持複雜邏輯和類定義
- **3 個**配置文件使用此格式

### Markdown (.md)
- 文檔和說明文件
- **9 個**文檔文件

---

## 🚀 使用示例

### 基本導入

```python
from src.config import get_config

# 獲取全局配置
config = get_config()

# 訪問配置
api_key = config.get('binance.api_key')
deployment_env = config.get('deployment.environment', 'development')
```

### 加載特定系統配置

```python
from src.config.systems.main_system import main_system_config
from src.config.systems.enhanced_compression import compression_optimizer

# 加載主系統配置
main_config = main_system_config.load()

# 加載壓縮優化配置
compression_config = compression_optimizer.load()
```

### 使用環境配置

```python
import json

# 獲取當前環境配置
with open('src/config/environments/production/config.json') as f:
    env_config = json.load(f)
    
# 或者使用環境變量
import os
current_env = os.getenv('ENVIRONMENT', 'development')
config_path = f'src/config/environments/{current_env}/config.json'
```

---

## ✅ 驗證清單

遷移後的驗證項目：

- [x] 所有目錄已創建
- [x] 所有文件已遷移
- [x] 沒有文件丟失
- [x] 目錄結構完整
- [x] 文檔已更新
- [ ] 代碼路徑已更新（待執行）
- [ ] 配置加載測試已通過（待執行）
- [ ] 環境變量配置已驗證（待執行）
- [ ] CI/CD 配置已更新（待執行）

---

## 🔗 相關文件

- 主配置模塊: `/src/config/__init__.py`
- 配置加載器: `/src/config/loaders/config_loader.py`
- 配置模式: `/src/config/schemas/`

---

## 📞 支持

如有問題，請參考：

1. `CONFIG_REGISTRY.py` - 完整的配置層級結構
2. `CONFIG_MAPPING.txt` - 文件對應映射
3. `MIGRATION_REPORT.txt` - 詳細遷移日誌
4. 各子目錄的 `README.md` 文件

---

**最後更新**: 2026-04-06  
**版本**: 1.0.0  
**狀態**: ✓ 完成
