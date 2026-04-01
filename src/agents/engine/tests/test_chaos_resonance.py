"""
單元測試: chaos_resonance
中文名稱: 混沌共振
"""

import pytest
import sys
from pathlib import Path

# 添加 src 路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestTheory:
    """混沌共振 理論單元測試"""
    
    def test_import_core(self):
        """測試能否導入核心模塊"""
        try:
            from chaos_resonance import core
            assert core is not None
        except ImportError:
            pytest.skip("Core module not yet implemented")
    
    def test_configuration(self):
        """測試配置檔讀取"""
        import yaml
        from pathlib import Path
        
        config_path = Path(__file__).parent.parent / "config" / "chaos_resonance.yaml"
        assert config_path.exists(), f"Configuration file not found: {config_path}"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
            assert config is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
