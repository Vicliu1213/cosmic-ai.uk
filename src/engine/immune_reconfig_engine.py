#!/usr/bin/env python3
"""
免疫重構引擎
基於量子優勢的自我修復與進化系統
"""

import numpy as np
import yaml
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import logging

@dataclass
class ImmuneCell:
    """免疫細胞單元"""
    id: str
    type: str  # T-cell, B-cell, NK-cell
    strength: float
    memory: Dict[str, Any]
    activation_threshold: float
    last_activation: Optional[datetime] = None

@dataclass
class AntigenPattern:
    """抗原模式 - 異常檢測模式"""
    pattern_id: str
    signature: np.ndarray
    threat_level: float
    category: str  # anomaly, error, inefficiency

class ImmuneReconfigEngine:
    """免疫重構引擎主類"""
    
    def __init__(self, config_path: str = "engine/immune_config.yaml"):
        self.config = self._load_config(config_path)
        self.immune_cells: Dict[str, ImmuneCell] = {}
        self.antigen_patterns: Dict[str, AntigenPattern] = {}
        self.system_state = "normal"
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """載入免疫引擎配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            'immune_system': {
                'cell_types': {
                    'T-cell': {'count': 10, 'base_strength': 0.7},
                    'B-cell': {'count': 8, 'base_strength': 0.6},
                    'NK-cell': {'count': 5, 'base_strength': 0.8}
                },
                'response_threshold': 0.8,
                'memory_decay': 0.95,
                'adaptation_rate': 0.1
            },
            'quantum_enhancement': {
                'coherence_threshold': 0.9,
                'entanglement_depth': 4,
                'superposition_states': 3
            }
        }
        
    def initialize_immune_system(self) -> None:
        """初始化免疫系統"""
        cell_config = self.config['immune_system']['cell_types']
        
        for cell_type, config in cell_config.items():
            for i in range(config['count']):
                cell_id = f"{cell_type}_{i}"
                cell = ImmuneCell(
                    id=cell_id,
                    type=cell_type,
                    strength=config['base_strength'] * np.random.uniform(0.8, 1.2),
                    memory={},
                    activation_threshold=self.config['immune_system']['response_threshold']
                )
                self.immune_cells[cell_id] = cell
                
        self.logger.info(f"Initialized {len(self.immune_cells)} immune cells")
        
    def detect_anomaly(self, system_metrics: Dict[str, Any]) -> List[AntigenPattern]:
        """檢測系統異常模式"""
        antigens = []
        
        # 性能異常檢測
        performance = system_metrics.get('performance', {})
        if performance.get('cpu_usage', 0) > 0.9:
            antigens.append(AntigenPattern(
                pattern_id="high_cpu",
                signature=np.array([0.9, 0, 0]),
                threat_level=0.8,
                category="anomaly"
            ))
            
        # 錯誤率異常
        error_rate = system_metrics.get('error_rate', 0)
        if error_rate > 0.05:
            antigens.append(AntigenPattern(
                pattern_id="high_error_rate",
                signature=np.array([0, error_rate, 0]),
                threat_level=min(error_rate * 10, 1.0),
                category="error"
            ))
            
        # 效率異常
        efficiency = system_metrics.get('efficiency', 1.0)
        if efficiency < 0.7:
            antigens.append(AntigenPattern(
                pattern_id="low_efficiency",
                signature=np.array([0, 0, 1.0 - efficiency]),
                threat_level=1.0 - efficiency,
                category="inefficiency"
            ))
            
        return antigens
        
    def activate_immune_response(self, antigens: List[AntigenPattern]) -> Dict[str, Any]:
        """激活免疫應答"""
        response_actions = []
        
        for antigen in antigens:
            # 計算細胞激活程度
            activated_cells = []
            for cell in self.immune_cells.values():
                activation_score = self._calculate_cell_activation(cell, antigen)
                if activation_score > cell.activation_threshold:
                    activated_cells.append({
                        'cell_id': cell.id,
                        'type': cell.type,
                        'activation': activation_score
                    })
                    
            if activated_cells:
                response = self._generate_response(antigen, activated_cells)
                response_actions.append(response)
                
        return {
            'response_actions': response_actions,
            'total_threat_level': sum(a.threat_level for a in antigens),
            'response_strength': len(activated_cells) / len(self.immune_cells)
        }
        
    def _calculate_cell_activation(self, cell: ImmuneCell, antigen: AntigenPattern) -> float:
        """計算免疫細胞激活度"""
        # 量子增強的相似性計算
        quantum_factor = self.config['quantum_enhancement']['coherence_threshold']
        
        # 基於記憶的識別
        memory_activation = 0.0
        if antigen.pattern_id in cell.memory:
            memory_activation = cell.memory[antigen.pattern_id].get('strength', 0)
            
        # 基於類型的專一性
        type_specificity = {
            'T-cell': ['error'],
            'B-cell': ['anomaly'], 
            'NK-cell': ['inefficiency']
        }
        
        specificity_bonus = 1.0
        if antigen.category in type_specificity.get(cell.type, []):
            specificity_bonus = 1.5
            
        activation = (cell.strength * specificity_bonus * quantum_factor + 
                    memory_activation * (1 - quantum_factor))
                    
        return min(activation, 1.0)
        
    def _generate_response(self, antigen: AntigenPattern, activated_cells: List[Dict]) -> Dict[str, Any]:
        """生成應答策略"""
        strategies = {
            'high_cpu': 'scale_resources',
            'high_error_rate': 'error_recovery',
            'low_efficiency': 'optimize_algorithm'
        }
        
        strategy = strategies.get(antigen.pattern_id, 'general_recovery')
        
        return {
            'antigen': antigen.pattern_id,
            'threat_level': antigen.threat_level,
            'strategy': strategy,
            'activated_cells': len(activated_cells),
            'recommended_actions': self._get_action_plan(strategy, antigen.threat_level)
        }
        
    def _get_action_plan(self, strategy: str, threat_level: float) -> List[str]:
        """獲取具體執行計劃"""
        action_plans = {
            'scale_resources': [
                'increase_computation_power',
                'activate_additional_cores',
                'optimize_memory_allocation'
            ],
            'error_recovery': [
                'rollback_to_stable_state',
                'clear_corrupted_cache',
                'reinitialize_failed_modules'
            ],
            'optimize_algorithm': [
                'reconfigure_parameters',
                'apply_quantum_enhancements',
                'enable_adaptive_optimization'
            ]
        }
        
        base_actions = action_plans.get(strategy, ['system_restart'])
        
        # 根據威脅等級調整
        if threat_level > 0.8:
            base_actions.append('emergency_quarantine')
            
        return base_actions
        
    def adapt_and_evolve(self, response_results: Dict[str, Any]) -> None:
        """適應與進化"""
        success_rate = response_results.get('success_rate', 0.5)
        
        for cell in self.immune_cells.values():
            # 記憶學習
            if cell.last_activation:
                for antigen_id, result in response_results.items():
                    if antigen_id in cell.memory:
                        # 記憶衰減
                        cell.memory[antigen_id]['strength'] *= (
                            self.config['immune_system']['memory_decay']
                        )
                        
                    # 新記憶形成
                    if result > 0.7:  # 成功應答
                        cell.memory[antigen_id] = {
                            'strength': result,
                            'timestamp': datetime.now()
                        }
                        
            # 適應性調整
            adaptation_rate = self.config['immune_system']['adaptation_rate']
            if success_rate > 0.8:
                cell.strength = min(1.0, cell.strength * (1 + adaptation_rate))
            elif success_rate < 0.3:
                cell.strength = max(0.1, cell.strength * (1 - adaptation_rate))
                
    def get_system_status(self) -> Dict[str, Any]:
        """獲取免疫系統狀態"""
        cell_types = {}
        for cell in self.immune_cells.values():
            if cell.type not in cell_types:
                cell_types[cell.type] = {'count': 0, 'avg_strength': 0}
            cell_types[cell.type]['count'] += 1
            cell_types[cell.type]['avg_strength'] += cell.strength
            
        for cell_type in cell_types:
            cell_types[cell_type]['avg_strength'] /= cell_types[cell_type]['count']
            
        return {
            'system_state': self.system_state,
            'total_cells': len(self.immune_cells),
            'cell_distribution': cell_types,
            'memory_patterns': len(self.antigen_patterns),
            'quantum_coherence': self.config['quantum_enhancement']['coherence_threshold']
        }