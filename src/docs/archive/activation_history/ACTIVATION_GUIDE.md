# Comic AI 系統激活指南

## 快速激活

### 1. 激活虛擬環境

```bash
cd /root/comic_ai
source venv/bin/activate
```

### 2. 驗證系統狀態

```bash
# 檢查所有核心模塊
python3 << 'VERIFY'
import numpy, pandas, scipy, matplotlib, yaml, qiskit, ray, semantic_kernel
print("✅ 所有模塊已加載")
VERIFY

# 運行測試
pytest src/tests/ -v
```

### 3. 運行主要應用

#### CLI 應用

```bash
python3 src/cli/cli.py
```

#### 量子交易演算法

```bash
python3 quantum_grover_trading_algorithm.py
```

#### 多智能體系統演示

```bash
python3 demo_singularity_system.py
```

## 系統組件狀態

| 組件 | 狀態 | 版本 |
|------|------|------|
| Python | ✅ | 3.12.3 |
| NumPy | ✅ | 1.26.4 |
| Pandas | ✅ | 3.0.1 |
| Qiskit | ✅ | 2.3.0 |
| Ray | ✅ | 2.52.1 |
| Semantic Kernel | ✅ | 1.39.4 |

## 測試結果摘要

- 通過: 172/218 (78.9%)
- 失敗: 46/218 (主要是未實現功能)

## 常見命令

```bash
# 激活環境
source venv/bin/activate

# 安裝依賴（如果需要更新）
pip install -r requirements.txt --upgrade

# 運行所有測試
pytest src/tests/ -v

# 運行特定測試
pytest src/tests/test_api.py -v

# 運行代碼質量檢查
flake8 . --count --select=E9,F63,F7,F82 --show-source

# 退出虛擬環境
deactivate
```

## 故障排除

### 如果出現 "externally-managed-environment" 錯誤

虛擬環境已設置好，使用：

```bash
source venv/bin/activate
```

### 如果模塊導入失敗

重新安裝依賴：

```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade --force-reinstall
```

### 如果測試失敗

查看詳細錯誤：

```bash
pytest src/tests/ -vv --tb=long
```

## 系統架構

```
Comic AI
├── src/
│   ├── core/          # 核心交易和量子系統
│   ├── cli/           # 命令行界面
│   ├── tests/         # 測試套件
│   └── utils/         # 工具函數
├── engine/            # 量子和機器學習引擎
├── optimizer/         # 優化算法
├── dashboard/         # Web 儀表板
└── config/            # 配置文件
```

## 激活狀態

✅ **系統已成功激活**

最後激活: 2026-02-20
下次維護: 檢查失敗測試並完成未實現功能
