"""
Configuration Schemas Module
配置数据验证模式 - 用于验证和类型检查配置数据
"""

from typing import Dict, Any

# API 相关 schemas
API_KEYS_SCHEMAS = {
    'binance': {
        'type': 'object',
        'properties': {
            'api_key': {'type': 'string'},
            'api_secret': {'type': 'string'},
        },
        'required': ['api_key', 'api_secret']
    },
    
    'deepseek': {
        'type': 'object',
        'properties': {
            'api_key': {'type': 'string'},
        },
        'required': ['api_key']
    },
    
    'llm': {
        'type': 'object',
        'properties': {
            'provider': {
                'type': 'string',
                'enum': ['openai', 'deepseek', 'claude', 'qwen', 'gemini', 'kimi', 'minimax', 'glm']
            },
            'model': {'type': 'string'},
            'api_keys': {'type': 'object'},
            'base_url': {'type': 'string'},
        },
        'required': ['provider', 'model']
    }
}

# 基础设施相关 schemas
INFRASTRUCTURE_SCHEMAS = {
    'redis': {
        'type': 'object',
        'properties': {
            'host': {'type': 'string'},
            'port': {'type': 'integer'},
            'db': {'type': 'integer'},
            'password': {'type': 'string'},
        },
        'required': ['host', 'port']
    },
    
    'logging': {
        'type': 'object',
        'properties': {
            'level': {
                'type': 'string',
                'enum': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            },
            'format': {'type': 'string'},
            'file': {'type': 'string'},
        }
    }
}

# 交易相关 schemas
TRADING_SCHEMAS = {
    'trading': {
        'type': 'object',
        'properties': {
            'pair': {'type': 'string'},
            'timeframe': {'type': 'string'},
            'leverage': {'type': 'number'},
            'position_size': {'type': 'number'},
        }
    },
    
    'risk': {
        'type': 'object',
        'properties': {
            'max_drawdown_pct': {'type': 'number'},
            'max_position_size': {'type': 'number'},
            'stop_loss_pct': {'type': 'number'},
            'take_profit_pct': {'type': 'number'},
            'max_consecutive_losses': {'type': 'integer'},
        }
    },
    
    'backtest': {
        'type': 'object',
        'properties': {
            'enabled': {'type': 'boolean'},
            'start_date': {'type': 'string'},
            'end_date': {'type': 'string'},
            'initial_capital': {'type': 'number'},
            'commission': {'type': 'number'},
        }
    }
}

# 完整配置 schema
FULL_CONFIG_SCHEMA = {
    'type': 'object',
    'properties': {
        **{k: v for k, v in API_KEYS_SCHEMAS.items()},
        **{k: v for k, v in INFRASTRUCTURE_SCHEMAS.items()},
        **{k: v for k, v in TRADING_SCHEMAS.items()},
    },
    'required': ['binance', 'redis', 'llm']
}


__all__ = [
    'API_KEYS_SCHEMAS',
    'INFRASTRUCTURE_SCHEMAS',
    'TRADING_SCHEMAS',
    'FULL_CONFIG_SCHEMA',
]
