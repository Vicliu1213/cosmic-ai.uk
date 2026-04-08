# 檔名命名標準指南

## 📋 概述

為了保持代碼的整齊性和可維護性，我們採用統一的命名規範。所有檔案名稱都遵循前綴 + 描述的格式。

## 🎯 命名規範

### 通用規則

1. **小寫字母**: 所有檔案名都使用小寫
2. **下劃線分隔**: 使用下劃線 `_` 分隔單詞，不使用連字符 `-` 或駝峰命名
3. **前綴格式**: `prefix_description.py` 或 `prefix_description.md`
4. **清晰描述**: 描述應該清晰明確，通常為 2-4 個單詞

### 前綴分類

#### 1. `activation_` - 激活相關
用於與系統激活功能相關的檔案。

```
activation_display.py          # 激活狀態展示
activation_main_menu.py        # 激活主菜單
activation_status_cli.py       # 激活狀態 CLI
```

#### 2. `init_` - 初始化相關
用於系統初始化和設置檔案。

```
init_exponential_synergy.py    # 初始化指數協同系統
init_immortal_system.py        # 初始化永恆系統
init_quantum_field_theory.py   # 初始化量子場論
init_system.py                 # 初始化系統
```

#### 3. `config_` - 配置相關
用於配置、驗證和環境設置檔案。

```
config_deployment.py           # 部署配置
config_environment.py          # 環境配置
config_environment_validator.py # 環境驗證
config_init_validator.py       # 初始化驗證
config_validator.py            # 配置驗證
```

#### 4. `start_` - 啟動相關
用於系統啟動和運行相關的檔案。

```
start_deployment.py            # 啟動部署
start_direct.py                # 直接啟動
start_infinity_synergy.py      # 啟動無限協同
start_with_recap.py            # 帶回顧的啟動
```

#### 5. `install_` - 安裝相關
用於安裝和配置程序檔案。

```
install_config_auto.py         # 自動配置安裝
install_openclaw.py            # OpenClaw 安裝
```

#### 6. `test_` - 測試相關
用於所有測試檔案。

```
test_api_connectivity.py       # API 連接測試
test_https.py                  # HTTPS 測試
test_imports_and_execution.py  # 導入和執行測試
test_integration.py            # 集成測試
test_system_check.py           # 系統檢查測試
```

#### 7. `tool_` - 工具相關
用於各種工具和實用程序檔案。

```
tool_code_quality_checker.py   # 代碼質量檢查器
tool_comprehensive_analyzer.py # 綜合分析器
tool_cosmic_optimizer.py       # 宇宙優化器
tool_memory_cli.py             # 記憶體 CLI 工具
tool_project_analyzer.py       # 項目分析器
tool_recap_cli.py              # 回顧 CLI 工具
tool_setup_ssl.py              # SSL 設置工具
tool_setup_vertex_ai.py        # Vertex AI 設置工具
tool_task_panel.py             # 任務面板工具
tool_task_panel_launcher.py    # 任務面板啟動器
```

#### 8. `report_` - 報告相關（文檔）
用於所有報告和分析文檔檔案。

```
report_backtest_analysis.md              # 回測分析報告
report_backtest_conclusions.md           # 回測結論報告
report_optimization.md                   # 優化報告
report_quantum_classical_hybrid.md       # 量子-經典混合報告
report_quantum_enhanced.md               # 量子增強報告
```

#### 9. `example_` - 示例相關
用於示例代碼和演示檔案。

```
example_singularity.py         # 奇點示例
skill_converter_examples.py    # 技能轉換器示例
```

## 📁 目錄結構

### scripts/ - 執行腳本
```
scripts/
├── activation_*.py          # 激活相關腳本
├── init_*.py               # 初始化腳本
├── config_*.py             # 配置相關腳本
├── start_*.py              # 啟動腳本
├── install_*.py            # 安裝腳本
├── test_*.py               # 測試腳本
└── tool_*.py               # 工具腳本
```

### reports/ - 報告文檔
```
reports/
├── report_*.md             # 報告文檔
├── backtest/
│   └── report_*.md        # 回測相關報告
├── backtesting/
│   └── report_*.md        # 回測分析報告
├── benchmarking/          # 基準測試報告
└── daily/                 # 日報告
```

### examples/ - 示例代碼
```
examples/
├── example_*.py           # 示例代碼
└── *_examples.py          # 示例集合
```

## 🔄 命名轉換示例

### Before (不統一)
```
deploy.py
direct_launch.py
comprehensive_analyzer.py
FINAL_BACKTEST_CONCLUSIONS.md
openclaw-install.py
```

### After (統一)
```
start_deployment.py
start_direct.py
tool_comprehensive_analyzer.py
report_backtest_conclusions.md
install_openclaw.py
```

## ✅ 檢查清單

命名新檔案時，請確保：

- [ ] 使用小寫字母
- [ ] 使用下劃線分隔單詞
- [ ] 選擇正確的前綴
- [ ] 描述清晰且簡潔
- [ ] 遵循現有的命名模式
- [ ] 總長度不超過 50 個字符

## 📊 統計

### Scripts 目錄 (35 個檔案)
| 前綴 | 數量 | 用途 |
|------|------|------|
| activation_ | 3 | 激活相關 |
| init_ | 4 | 初始化 |
| config_ | 5 | 配置相關 |
| start_ | 4 | 啟動相關 |
| install_ | 2 | 安裝相關 |
| test_ | 5 | 測試相關 |
| tool_ | 10 | 工具相關 |
| __init__.py | 1 | 模塊初始化 |

### Reports 目錄 (5 個檔案)
| 前綴 | 數量 | 用途 |
|------|------|------|
| report_ | 5 | 報告文檔 |

### Examples 目錄 (1 個檔案)
| 前綴 | 數量 | 用途 |
|------|------|------|
| *_examples | 1 | 示例代碼 |

## 🔗 相關文檔

- [Python 命名慣例 (PEP 8)](https://pep8.org/)
- [Google Python 風格指南](https://google.github.io/styleguide/pyguide.html)

---

**版本**: 1.0
**生效日期**: 2026-04-07
**狀態**: ✅ 已實施
