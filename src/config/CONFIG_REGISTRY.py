"""
Configuration Registry - 配置文件對齐索引

此文件記錄所有配置文件的位置、目的和依賴關係
"""

CONFIG_REGISTRY = {
    # 系統配置 (15個突破協同理論系統)
    'systems': {
        'main_system': {
            'path': 'systems/main_system/',
            'files': [
                'main_system_config.yaml',
                'cosmic_engine.yaml'
            ],
            'description': '主系統配置',
            'features': [
                'enhanced_compression',
                'experience_learning',
                'immune_system',
                'intelligent_agents',
                'offline_processing',
                'profit_optimization',
                'quantum_analysis'
            ]
        },
        'quantum_analysis': {
            'path': 'systems/quantum_analysis/',
            'files': [],
            'description': '量子分析系統配置',
            'dependencies': ['main_system']
        },
        'immune_system': {
            'path': 'systems/immune_system/',
            'files': [],
            'description': '免疫系統配置',
            'dependencies': ['main_system']
        },
        'intelligent_agents': {
            'path': 'systems/intelligent_agents/',
            'files': [],
            'description': '智能代理系統配置',
            'dependencies': ['main_system']
        },
        'bio_evolution': {
            'path': 'systems/bio_evolution/',
            'files': [],
            'description': '生物進化系統配置',
            'dependencies': ['main_system']
        },
        'enhanced_compression': {
            'path': 'systems/enhanced_compression/',
            'files': [
                'compression_optimizer.yaml',
                'compression_control.yaml'
            ],
            'description': '增強壓縮系統配置',
            'dependencies': ['main_system']
        },
        'experience_learning': {
            'path': 'systems/experience_learning/',
            'files': [],
            'description': '經驗學習系統配置',
            'dependencies': ['main_system']
        },
        'profit_optimization': {
            'path': 'systems/profit_optimization/',
            'files': [],
            'description': '利潤優化系統配置',
            'dependencies': ['main_system', 'trading']
        },
        'offline_processing': {
            'path': 'systems/offline_processing/',
            'files': [],
            'description': '離線處理系統配置',
            'dependencies': ['main_system']
        },
        'energy_management': {
            'path': 'systems/energy_management/',
            'files': [],
            'description': '能量管理系統配置',
            'dependencies': ['main_system', 'enhanced_compression']
        },
        'performance': {
            'path': 'systems/performance/',
            'files': ['performance_config.yaml'],
            'description': '性能管理系統配置',
            'dependencies': ['main_system']
        },
        'optimization': {
            'path': 'systems/optimization/',
            'files': ['optimization_config.yaml'],
            'description': '優化系統配置',
            'dependencies': ['main_system']
        },
        'quantum_coherence': {
            'path': 'systems/quantum_coherence/',
            'files': [],
            'description': '量子相幹性系統配置',
            'dependencies': ['quantum_analysis']
        },
        'io_management': {
            'path': 'systems/io_management/',
            'files': [],
            'description': '輸入輸出管理系統配置',
            'dependencies': ['main_system']
        },
        'monitoring': {
            'path': 'systems/monitoring/',
            'files': [],
            'description': '監控系統配置',
            'dependencies': ['main_system']
        }
    },
    
    # 交易所配置
    'exchanges': {
        'binance': {
            'path': 'exchanges/binance/',
            'files': [],
            'description': '幣安交易所配置',
            'api_type': 'unified'
        },
        'okx': {
            'path': 'exchanges/okx/',
            'files': [],
            'description': '歐易交易所配置',
            'api_type': 'unified'
        },
        'bybit': {
            'path': 'exchanges/bybit/',
            'files': [],
            'description': 'Bybit交易所配置',
            'api_type': 'unified'
        },
        'bitget': {
            'path': 'exchanges/bitget/',
            'files': [],
            'description': 'Bitget交易所配置',
            'api_type': 'unified'
        },
        'common': {
            'path': 'exchanges/common/',
            'files': ['exchange_config.py'],
            'description': '統一交易所配置和客戶端',
            'supported_exchanges': ['binance', 'okx', 'bybit', 'bitget']
        }
    },
    
    # 基礎設施配置
    'infrastructure': {
        'deployment': {
            'path': 'infrastructure/deployment/',
            'files': ['deployment.yaml'],
            'description': '部署配置',
            'includes': ['environments', 'containers', 'scaling', 'monitoring']
        },
        'database': {
            'path': 'infrastructure/database/',
            'files': [],
            'description': '數據庫配置',
            'supported_types': ['sqlite', 'postgresql', 'redis']
        },
        'caching': {
            'path': 'infrastructure/caching/',
            'files': [],
            'description': '緩存配置',
            'cache_types': ['redis', 'memcached']
        },
        'networking': {
            'path': 'infrastructure/networking/',
            'files': ['network_config.yaml'],
            'description': '網絡配置',
            'includes': ['firewall', 'routing', 'load_balancing']
        },
        'logging': {
            'path': 'infrastructure/logging/',
            'files': [],
            'description': '日誌配置',
            'includes': ['structured_logging', 'log_rotation', 'log_levels']
        },
        'backup': {
            'path': 'infrastructure/backup/',
            'files': ['backup_config.yaml'],
            'description': '備份配置',
            'backup_types': ['database', 'logs', 'config']
        }
    },
    
    # 監控和安全
    'monitoring': {
        'path': 'monitoring/',
        'files': ['monitoring_config.yaml'],
        'description': '監控系統配置',
        'metrics': [
            'cpu_usage',
            'memory_usage',
            'disk_usage',
            'network_io',
            'error_rate',
            'response_time',
            'quantum_coherence'
        ]
    },
    
    'security': {
        'path': 'security/',
        'files': [
            'security_config.yaml',
            'privacy_config.yaml'
        ],
        'description': '安全和隱私配置',
        'features': [
            'authentication',
            'authorization',
            'encryption',
            'audit',
            'compliance'
        ]
    },
    
    # 交易配置
    'trading': {
        'strategies': {
            'path': 'trading/strategies/',
            'files': [],
            'description': '交易策略配置'
        },
        'risk_management': {
            'path': 'trading/risk_management/',
            'files': [],
            'description': '風險管理配置'
        },
        'backtest': {
            'path': 'trading/backtest/',
            'files': [],
            'description': '回測配置'
        },
        'portfolio': {
            'path': 'trading/portfolio/',
            'files': [],
            'description': '投資組合配置'
        }
    },
    
    # API密鑰和模板
    'api_keys': {
        'path': 'api_keys/',
        'description': 'API密鑰管理',
        'subdirs': ['binance', 'llm']
    },
    
    'templates': {
        'path': 'templates/',
        'files': ['default_prompt_template.py'],
        'description': '提示詞模板'
    },
    
    'loaders': {
        'path': 'loaders/',
        'files': ['config_loader.py'],
        'description': '配置加載器'
    },
    
    'schemas': {
        'path': 'schemas/',
        'description': '配置模式驗證'
    },
    
    'plugins': {
        'path': 'plugins/',
        'files': ['plugins_config.json'],
        'description': '插件配置'
    }
}

# 層級結構圖
HIERARCHY_MAP = """
src/config/
├── systems/                          # 15個突破協同理論系統
│   ├── main_system/                  # 1. 主系統
│   ├── quantum_analysis/             # 2. 量子分析
│   ├── immune_system/                # 3. 免疫系統
│   ├── intelligent_agents/           # 4. 智能代理
│   ├── bio_evolution/                # 5. 生物進化
│   ├── enhanced_compression/         # 6. 增強壓縮
│   ├── experience_learning/          # 7. 經驗學習
│   ├── profit_optimization/          # 8. 利潤優化
│   ├── offline_processing/           # 9. 離線處理
│   ├── energy_management/            # 10. 能量管理
│   ├── performance/                  # 11. 性能管理
│   ├── optimization/                 # 12. 優化
│   ├── quantum_coherence/            # 13. 量子相幹性
│   ├── io_management/                # 14. 輸入輸出管理
│   └── monitoring/                   # 15. 監控
│
├── exchanges/                        # 交易所配置
│   ├── binance/                      # 幣安
│   ├── okx/                          # 歐易
│   ├── bybit/                        # Bybit
│   ├── bitget/                       # Bitget
│   └── common/                       # 統一配置
│
├── infrastructure/                   # 基礎設施
│   ├── deployment/                   # 部署
│   ├── database/                     # 數據庫
│   ├── caching/                      # 緩存
│   ├── networking/                   # 網絡
│   ├── logging/                      # 日誌
│   └── backup/                       # 備份
│
├── trading/                          # 交易配置
│   ├── strategies/                   # 策略
│   ├── risk_management/              # 風險管理
│   ├── backtest/                     # 回測
│   └── portfolio/                    # 投資組合
│
├── monitoring/                       # 監控配置
├── security/                         # 安全配置
├── api_keys/                         # API密鑰
├── templates/                        # 提示詞模板
├── loaders/                          # 配置加載器
├── schemas/                          # 配置模式
└── plugins/                          # 插件配置
"""

if __name__ == '__main__':
    import json
    print("Configuration Registry")
    print("=" * 80)
    print(json.dumps(CONFIG_REGISTRY, indent=2, ensure_ascii=False))
    print("\n" + HIERARCHY_MAP)
