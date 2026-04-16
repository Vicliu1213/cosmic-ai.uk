"""
生產級配置加載器
支持多環境配置、配置分離、環境變量注入、熱加載
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ConfigLoader:
    """生產級配置加載器"""

    def __init__(self, config_dir: str = "config", env: str = None):
        self.config_dir = Path(config_dir)
        self.env = env or os.getenv("APP_ENV", "development")
        self._config = None
        self._watchers = []

        # 加載 .env 文件
        load_dotenv()

    def load(self, validate: bool = True) -> Dict[str, Any]:
        """加載完整配置"""
        if self._config is not None:
            return self._config

        logger.info(f"加載配置: 環境={self.env}, 目錄={self.config_dir}")

        # 1. 加載默認配置
        config = self._load_yaml("default.yaml")
        if not config:
            raise FileNotFoundError("default.yaml 不存在")

        # 2. 加載環境特定配置
        env_config = self._load_yaml(f"{self.env}.yaml")
        if env_config:
            config = self._deep_merge(config, env_config)
            logger.info(f"已加載環境配置: {self.env}.yaml")

        # 3. 加載引擎獨立配置
        engines_dir = self.config_dir / "engines"
        if engines_dir.exists():
            for engine_file in engines_dir.glob("*.yaml"):
                engine_name = engine_file.stem
                engine_config = self._load_yaml(f"engines/{engine_file.name}")
                if engine_config:
                    config = self._deep_merge(config, {
                        "algorithms": {
                            "engines": {
                                "params": {
                                    engine_name: engine_config
                                }
                            }
                        }
                    })
                    logger.debug(f"已加載引擎配置: {engine_name}")

        # 4. 加載驗證器配置
        validation_dir = self.config_dir / "validation"
        if validation_dir.exists():
            for val_file in validation_dir.glob("*.yaml"):
                val_name = val_file.stem
                val_config = self._load_yaml(f"validation/{val_file.name}")
                if val_config:
                    config = self._deep_merge(config, {
                        "validation": {
                            val_name: val_config
                        }
                    })

        # 5. 加載敏感信息
        secrets = self._load_yaml("secrets.yaml")
        if secrets:
            config = self._deep_merge(config, secrets)
            logger.info("已加載敏感配置")

        # 6. 環境變量覆蓋
        config = self._apply_env_overrides(config)

        # 7. 配置校驗
        if validate:
            self._validate_config(config)

        self._config = config
        return config

    def _load_yaml(self, filename: str) -> Optional[Dict]:
        """加載 YAML 文件"""
        filepath = self.config_dir / filename
        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"加載配置失敗 {filename}: {e}")
            return None

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """深度合併配置"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _apply_env_overrides(self, config: Dict) -> Dict:
        """應用環境變量覆蓋"""
        # 支持格式: APP_ALGORITHMS_ENGINES_INITIAL_0=trend
        prefix = "APP_"
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue

            # 解析路徑
            path = key[len(prefix):].lower().split('_')
            target = config
            for p in path[:-1]:
                if p not in target:
                    target[p] = {}
                target = target[p]

            # 轉換類型
            last_key = path[-1]
            if value.lower() in ('true', 'false'):
                target[last_key] = value.lower() == 'true'
            elif value.isdigit():
                target[last_key] = int(value)
            elif value.replace('.', '', 1).isdigit():
                target[last_key] = float(value)
            else:
                target[last_key] = value

        return config

    def _validate_config(self, config: Dict):
        """校驗必需配置項"""
        required_keys = [
            "global.name",
            "global.version",
            "runtime.api.port",
            "algorithms.engines.initial"
        ]

        for key_path in required_keys:
            keys = key_path.split('.')
            value = config
            for k in keys:
                if not isinstance(value, dict) or k not in value:
                    raise ValueError(f"缺少必需配置: {key_path}")
                value = value[k]

    def reload(self):
        """熱重載配置"""
        self._config = None
        return self.load()

    def get(self, path: str, default: Any = None) -> Any:
        """獲取指定路徑的配置值"""
        config = self.load()
        keys = path.split('.')
        value = config
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value[key]
        return value


# 全局單例
_config_loader = None

def get_config(env: str = None, reload: bool = False) -> Dict:
    """獲取配置（單例）"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(env=env)
    if reload:
        return _config_loader.reload()
    return _config_loader.load()


def get_config_value(path: str, default: Any = None) -> Any:
    """獲取單個配置值"""
    return get_config().get(path, default)
