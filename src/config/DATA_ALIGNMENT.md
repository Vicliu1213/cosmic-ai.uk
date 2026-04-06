"""
DATA ALIGNMENT DOCUMENTATION
數據對齐文檔 - 配置文件遷移和重組

生成日期：2026-04-06
狀態：已對齐並鋪展

===========================================
遷移總結
===========================================

源位置: /.config/
目標位置: /src/config/

遷移文件數: 17
創建新目錄: 45+
組織結構: 層級化分類 (15個系統 + 交易所 + 基礎設施)

===========================================
遷移詳情
===========================================

【1】系統配置 (15個突破協同理論系統)
────────────────────────────────────────

✓ main_system/
  - main_system_config.yaml (來自: /.config/main_system_config.yaml)
  - cosmic_engine.yaml (來自: /.config/cosmic_engine_yaml)
  特性: 定義系統基礎配置、特性開關、運行時參數

✓ enhanced_compression/
  - compression_optimizer.yaml (來自: /.config/compression_optimizer.yaml)
  - compression_control.yaml (來自: /.config/compression.control.yaml)
  特性: 壓縮策略、能量優化、量子協調

✓ performance/
  - performance_config.yaml (來自: /.config/performance_config.yaml)
  特性: 性能監控、緩存策略、優化目標

✓ optimization/
  - optimization_config.yaml (來自: /.config/optimization_config.yaml)
  特性: 系統優化參數、資源分配

✓ quantum_analysis/
  目錄已創建，待補充配置

✓ immune_system/
  目錄已創建，待補充配置

✓ intelligent_agents/
  目錄已創建，待補充配置

✓ bio_evolution/
  目錄已創建，待補充配置

✓ experience_learning/
  目錄已創建，待補充配置

✓ profit_optimization/
  目錄已創建，待補充配置

✓ offline_processing/
  目錄已創建，待補充配置

✓ energy_management/
  目錄已創建，待補充配置

✓ quantum_coherence/
  目錄已創建，待補充配置

✓ io_management/
  目錄已創建，待補充配置

【2】交易所配置
────────────────────────────────────────

✓ exchanges/common/
  - exchange_config.py (來自: /.config/exchange.py)
  支持交易所: Binance, OKX, Bybit, Bitget
  功能: 統一API接口、多交易所管理

✓ exchanges/binance/
  目錄已創建，待補充配置

✓ exchanges/okx/
  目錄已創建，待補充配置

✓ exchanges/bybit/
  目錄已創建，待補充配置

✓ exchanges/bitget/
  目錄已創建，待補充配置

【3】基礎設施配置
────────────────────────────────────────

✓ infrastructure/deployment/
  - deployment.yaml (來自: /.config/deployment.yaml)
  包含: 環境配置、容器配置、擴展策略、監控告警

✓ infrastructure/backup/
  - backup_config.yaml (來自: /.config/backup_config.yaml)
  包含: 備份策略、保留期、多目標備份

✓ infrastructure/networking/
  - network_config.yaml (來自: /.config/network_config.yaml)
  包含: 網絡配置、防火牆、負載均衡

✓ infrastructure/database/
  目錄已創建，待補充配置

✓ infrastructure/caching/
  目錄已創建，待補充配置

✓ infrastructure/logging/
  目錄已創建，待補充配置

【4】監控和安全
────────────────────────────────────────

✓ monitoring/
  - monitoring_config.yaml (來自: /.config/monitoring_config.yaml)
  指標: CPU、內存、磁盤、網絡、錯誤率、響應時間、量子相幹性

✓ security/
  - security_config.yaml (來自: /.config/security_config.yaml)
  - privacy_config.yaml (來自: /.config/privacy_config.yaml)
  特性: 認證、授權、加密、審計

【5】交易配置
────────────────────────────────────────

✓ trading/strategies/
  目錄已創建，待補充配置

✓ trading/risk_management/
  目錄已創建，待補充配置

✓ trading/backtest/
  目錄已創建，待補充配置

✓ trading/portfolio/
  目錄已創建，待補充配置

【6】其他配置
────────────────────────────────────────

✓ api_keys/
  既有結構保持，包含: binance, llm

✓ templates/
  既有文件: default_prompt_template.py

✓ loaders/
  既有文件: config_loader.py

✓ schemas/
  既有文件: 配置驗證模式

✓ plugins/
  - plugins_config.json (來自: /.config/plugins_config.json)
  插件管理配置

===========================================
待補充的配置文件
===========================================

以下文件在源目錄中但未被分類（需要確認用途）:

1. /.config/config.yaml (空文件)
2. /.config/default.yaml (空文件)
3. /.config/norgk.yml (1行配置)

建議:
- config.yaml → 可作為根配置模板保留在 /src/config/
- default.yaml → 可作為默認值模板保留在 /src/config/
- norgk.yml → 需要確認用途，建議檢查引用

===========================================
依賴關係圖
===========================================

main_system
├── quantum_analysis
├── immune_system
├── intelligent_agents
├── bio_evolution
├── enhanced_compression → energy_management
├── experience_learning
├── profit_optimization → trading
├── offline_processing
├── performance
├── optimization
├── quantum_coherence → quantum_analysis
├── io_management
└── monitoring

exchanges/common (統一接口)
├── exchanges/binance
├── exchanges/okx
├── exchanges/bybit
└── exchanges/bitget

infrastructure
├── deployment
├── database
├── caching
├── networking
├── logging
└── backup

===========================================
數據類型和配置格式
===========================================

YAML 配置文件 (.yaml/.yml):
- main_system_config.yaml
- compression_optimizer.yaml
- compression.control.yaml
- deployment.yaml
- backup_config.yaml
- network_config.yaml
- monitoring_config.yaml
- security_config.yaml
- privacy_config.yaml
- performance_config.yaml
- optimization_config.yaml

Python 模塊 (.py):
- exchange_config.py (UnifiedExchangeClient, MultiExchangeManager)

JSON 配置文件 (.json):
- plugins_config.json

===========================================
後續操作
===========================================

待做項目:

1. ✓ 創建層級目錄結構
2. ✓ 遷移現有配置文件
3. ✓ 創建系統 __init__.py 和索引文件
4. □ 為空目錄補充配置文件
5. □ 更新 src/config/__init__.py 以引用新結構
6. □ 更新所有導入路徑
7. □ 創建配置模式驗證規則
8. □ 測試新配置加載器
9. □ 更新文檔和說明
10. □ 清理舊的 /.config/ 目錄

===========================================
配置加載優先級
===========================================

1. 環境變量 (最高優先級)
2. 用戶配置 (src/config/*.yaml)
3. 系統特定配置 (src/config/systems/*/config.yaml)
4. 默認配置 (src/config/default.yaml)
5. 硬編碼默認值 (最低優先級)

===========================================
驗證檢查清單
===========================================

□ 所有YAML文件格式有效
□ 所有Python模塊可導入
□ JSON文件格式有效
□ 所有必需的目錄都已創建
□ 所有配置文件都已復制
□ 沒有文件丟失或損壞
□ 配置關鍵詞一致
□ 所有依賴項已解決
□ 文檔已更新
□ 測試通過

===========================================

更新時間: 2026-04-06 19:54:00
狀態: 已完成數據對齐和初始鋪展
"""

__version__ = "1.0.0"
__author__ = "OpenCode Configuration Alignment"
__status__ = "ALIGNED"

if __name__ == '__main__':
    print(__doc__)
