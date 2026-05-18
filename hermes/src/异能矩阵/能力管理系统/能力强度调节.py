"""
能力强度调节 - 我是调音师，精细控制异能强度
"""
from typing import Dict
import logging
from .. import AbilityConfig

logger = logging.getLogger(__name__)

class AbilityIntensityAdjuster:
    """
    视角：我是精准的控制器
    职责：在安全范围内动态调整异能强度
    """
    def __init__(self):
        self.intensity_overrides: Dict[str, float] = {}
        logger.info("🎚️ 能力强度调节器已就绪")

    def set_intensity(self, ability_id: str, intensity: float):
        intensity = max(0.1, min(1.0, intensity))
        self.intensity_overrides[ability_id] = intensity
        logger.info(f"🔧 {ability_id} 强度设置为: {intensity:.2f}")

    def get_intensity(self, ability: AbilityConfig) -> float:
        return self.intensity_overrides.get(ability.ability_id, 1.0)

    def scale_to_energy(self, ability: AbilityConfig, available_energy: float) -> float:
        """根据可用能量自动缩放强度"""
        ratio = available_energy / ability.base_energy_cost
        optimal = min(1.0, ratio * 0.9)
        self.set_intensity(ability.ability_id, optimal)
        logger.info(f"📐 {ability.name} 自动强度: {optimal:.2f} (能量比率: {ratio:.2f})")
        return optimal

    def reset(self, ability_id: str):
        if ability_id in self.intensity_overrides:
            del self.intensity_overrides[ability_id]
