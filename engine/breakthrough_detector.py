#!/usr/bin/env python3
"""
技術突破檢測系統
基於現實技術的性能評估和突破檢測
"""

import numpy as np
import scipy.stats as stats
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

class BreakthroughType(Enum):
    """突破類型枚舉"""
    ALGORITHMIC = "algorithmic"
    PERFORMANCE = "performance" 
    EFFICIENCY = "efficiency"
    SCALABILITY = "scalability"
    NOVELTY = "novelty"

class SignificanceLevel(Enum):
    """顯著性等級"""
    INSIGNIFICANT = "insignificant"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    BREAKTHROUGH = "breakthrough"

@dataclass
class PerformanceMetric:
    """性能指標"""
    name: str
    value: float
    baseline: float
    unit: str
    improvement_ratio: float
    statistical_significance: float
    confidence_interval: Tuple[float, float]

@dataclass
class BreakthroughCandidate:
    """突破候選"""
    breakthrough_type: BreakthroughType
    metrics: List[PerformanceMetric]
    significance: SignificanceLevel
    confidence_score: float
    novelty_score: float
    reproducibility: float
    timestamp: datetime
    description: str

class StatisticalValidator:
    """統計驗證器"""
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
        self.min_sample_size = 5
        
    def calculate_improvement_significance(self, 
                                     baseline_values: List[float],
                                     improved_values: List[float]) -> Tuple[float, float]:
        """計算改進的統計顯著性"""
        if len(baseline_values) < self.min_sample_size or len(improved_values) < self.min_sample_size:
            return 0.0, 0.0
            
        # t檢驗
        baseline_mean = np.mean(baseline_values)
        improved_mean = np.mean(improved_values)
        
        baseline_std = np.std(baseline_values, ddof=1)
        improved_std = np.std(improved_values, ddof=1)
        
        # 合併標準誤差
        n1, n2 = len(baseline_values), len(improved_values)
        pooled_se = np.sqrt((baseline_std**2/n1) + (improved_std**2/n2))
        
        # t統計量
        if pooled_se > 0:
            t_stat = (improved_mean - baseline_mean) / pooled_se
        else:
            t_stat = 0
            
        # p值
        df = n1 + n2 - 2
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))
        
        # 改進比率
        if baseline_mean != 0:
            improvement_ratio = (baseline_mean - improved_mean) / abs(baseline_mean)
        else:
            improvement_ratio = 0.0
            
        return improvement_ratio, p_value
        
    def calculate_confidence_interval(self, 
                                  values: List[float]) -> Tuple[float, float]:
        """計算置信區間"""
        if len(values) < 2:
            return 0.0, 0.0
            
        mean = np.mean(values)
        std_err = stats.sem(values)
        
        # t分位數
        alpha = 1 - self.confidence_level
        t_critical = stats.t.ppf(1 - alpha/2, len(values) - 1)
        
        margin = t_critical * std_err
        return mean - margin, mean + margin

class BreakthroughDetector:
    """技術突破檢測器"""
    
    def __init__(self, config_path: str = "config/breakthrough_config.yaml"):
        self.config = self._load_config(config_path)
        self.validator = StatisticalValidator()
        self.historical_performance = {}
        self.detected_breakthroughs = []
        self.performance_benchmarks = {}
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """載入檢測配置"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            'thresholds': {
                'minor_improvement': 0.1,      # 10%
                'moderate_improvement': 0.25,   # 25%
                'major_improvement': 0.5,        # 50%
                'breakthrough_improvement': 1.0   # 100%
            },
            'validation': {
                'statistical_significance': 0.05,
                'min_reproducibility': 0.8,
                'min_novelty_score': 0.6,
                'validation_runs': 5
            },
            'metrics': {
                'performance_metrics': [
                    'convergence_speed',
                    'solution_quality', 
                    'computational_efficiency',
                    'memory_usage',
                    'scalability_factor'
                ],
                'weight_factors': {
                    'convergence_speed': 0.25,
                    'solution_quality': 0.35,
                    'computational_efficiency': 0.2,
                    'memory_usage': 0.1,
                    'scalability_factor': 0.1
                }
            }
        }
        
    def analyze_performance_improvement(self, 
                                   method_name: str,
                                   baseline_metrics: Dict[str, List[float]],
                                   new_metrics: Dict[str, List[float]],
                                   problem_context: str = "") -> Optional[BreakthroughCandidate]:
        """分析性能改進"""
        performance_metrics = []
        
        for metric_name in self.config['metrics']['performance_metrics']:
            if metric_name in baseline_metrics and metric_name in new_metrics:
                baseline_vals = baseline_metrics[metric_name]
                new_vals = new_metrics[metric_name]
                
                # 計算統計顯著性
                improvement_ratio, p_value = self.validator.calculate_improvement_significance(
                    baseline_vals, new_vals
                )
                
                # 計算置信區間
                ci_low, ci_high = self.validator.calculate_confidence_interval(new_vals)
                
                # 創建性能指標
                baseline_mean = np.mean(baseline_vals)
                new_mean = np.mean(new_vals)
                
                metric = PerformanceMetric(
                    name=metric_name,
                    value=new_mean,
                    baseline=baseline_mean,
                    unit=self._get_metric_unit(metric_name),
                    improvement_ratio=improvement_ratio,
                    statistical_significance=p_value,
                    confidence_interval=(ci_low, ci_high)
                )
                
                performance_metrics.append(metric)
                
        if not performance_metrics:
            return None
            
        # 計算整體顯著性
        overall_significance = self._calculate_overall_significance(performance_metrics)
        significance_level = self._determine_significance_level(overall_significance)
        
        # 計算新穎性分數
        novelty_score = self._calculate_novelty_score(method_name, problem_context)
        
        # 計算可重現性
        reproducibility = self._calculate_reproducibility(new_metrics)
        
        # 計算置信分數
        confidence_score = self._calculate_confidence_score(
            performance_metrics, significance_level, novelty_score, reproducibility
        )
        
        # 生成描述
        description = self._generate_description(
            method_name, performance_metrics, significance_level
        )
        
        breakthrough = BreakthroughCandidate(
            breakthrough_type=self._determine_breakthrough_type(performance_metrics),
            metrics=performance_metrics,
            significance=significance_level,
            confidence_score=confidence_score,
            novelty_score=novelty_score,
            reproducibility=reproducibility,
            timestamp=datetime.now(),
            description=description
        )
        
        # 更新歷史記錄
        self.historical_performance[method_name] = {
            'metrics': new_metrics,
            'timestamp': breakthrough.timestamp,
            'significance': significance_level
        }
        
        return breakthrough
        
    def _get_metric_unit(self, metric_name: str) -> str:
        """獲取指標單位"""
        units = {
            'convergence_speed': 'iterations/second',
            'solution_quality': 'objective_value',
            'computational_efficiency': 'operations/second',
            'memory_usage': 'MB',
            'scalability_factor': 'factor'
        }
        return units.get(metric_name, 'unit')
        
    def _calculate_overall_significance(self, metrics: List[PerformanceMetric]) -> float:
        """計算整體顯著性"""
        weights = self.config['metrics']['weight_factors']
        
        weighted_significance = 0.0
        total_weight = 0.0
        
        for metric in metrics:
            weight = weights.get(metric.name, 0.1)
            significance = 1.0 - metric.statistical_significance  # 轉換為顯著性分數
            
            weighted_significance += weight * significance
            total_weight += weight
            
        return weighted_significance / total_weight if total_weight > 0 else 0.0
        
    def _determine_significance_level(self, overall_significance: float) -> SignificanceLevel:
        """確定顯著性等級"""
        thresholds = self.config['thresholds']
        
        if overall_significance < thresholds['minor_improvement']:
            return SignificanceLevel.INSIGNIFICANT
        elif overall_significance < thresholds['moderate_improvement']:
            return SignificanceLevel.MINOR
        elif overall_significance < thresholds['major_improvement']:
            return SignificanceLevel.MODERATE
        elif overall_significance < thresholds['breakthrough_improvement']:
            return SignificanceLevel.MAJOR
        else:
            return SignificanceLevel.BREAKTHROUGH
            
    def _determine_breakthrough_type(self, metrics: List[PerformanceMetric]) -> BreakthroughType:
        """確定突破類型"""
        # 基於主要改進確定類型
        best_metric = max(metrics, key=lambda m: m.improvement_ratio)
        
        type_mapping = {
            'convergence_speed': BreakthroughType.PERFORMANCE,
            'solution_quality': BreakthroughType.ALGORITHMIC,
            'computational_efficiency': BreakthroughType.EFFICIENCY,
            'memory_usage': BreakthroughType.EFFICIENCY,
            'scalability_factor': BreakthroughType.SCALABILITY
        }
        
        return type_mapping.get(best_metric.name, BreakthroughType.ALGORITHMIC)
        
    def _calculate_novelty_score(self, method_name: str, context: str) -> float:
        """計算新穎性分數"""
        # 基於方法名和上下文估算新穎性
        novelty_keywords = {
            'quantum': 0.8,
            'hybrid': 0.6,
            'enhanced': 0.4,
            'adaptive': 0.5,
            'neural': 0.7,
            'evolutionary': 0.6
        }
        
        # 檢查關鍵詞
        max_score = 0.0
        for keyword, score in novelty_keywords.items():
            if keyword in method_name.lower():
                max_score = max(max_score, score)
                
        # 上下文新穎性
        context_bonus = 0.1 if 'novel' in context.lower() or 'innovative' in context.lower() else 0.0
        
        return min(max_score + context_bonus, 1.0)
        
    def _calculate_reproducibility(self, metrics: Dict[str, List[float]]) -> float:
        """計算可重現性"""
        if not metrics:
            return 0.0
            
        reproducibility_scores = []
        
        for metric_name, values in metrics.items():
            if len(values) < 2:
                continue
                
            # 計算變異係數
            mean_val = np.mean(values)
            if mean_val != 0:
                cv = np.std(values) / abs(mean_val)
                # 低變異係數表示高可重現性
                reproducibility = max(0, 1 - cv)
                reproducibility_scores.append(reproducibility)
                
        return np.mean(reproducibility_scores) if reproducibility_scores else 0.0
        
    def _calculate_confidence_score(self, 
                                  metrics: List[PerformanceMetric],
                                  significance: SignificanceLevel,
                                  novelty: float,
                                  reproducibility: float) -> float:
        """計算綜合置信分數"""
        # 權重配置
        weights = {
            'significance': 0.4,
            'statistical_validity': 0.3,
            'novelty': 0.2,
            'reproducibility': 0.1
        }
        
        # 顯著性分數
        significance_scores = {
            SignificanceLevel.INSIGNIFICANT: 0.0,
            SignificanceLevel.MINOR: 0.25,
            SignificanceLevel.MODERATE: 0.5,
            SignificanceLevel.MAJOR: 0.75,
            SignificanceLevel.BREAKTHROUGH: 1.0
        }
        
        sig_score = significance_scores[significance]
        
        # 統計有效性（基於p值）
        avg_significance = np.mean([1.0 - m.statistical_significance for m in metrics])
        
        # 綜合分數
        confidence = (
            weights['significance'] * sig_score +
            weights['statistical_validity'] * avg_significance +
            weights['novelty'] * novelty +
            weights['reproducibility'] * reproducibility
        )
        
        return min(confidence, 1.0)
        
    def _generate_description(self, 
                           method_name: str,
                           metrics: List[PerformanceMetric],
                           significance: SignificanceLevel) -> str:
        """生成突破描述"""
        if not metrics:
            return f"{method_name}: Insufficient data for evaluation"
            
        # 主要改進指標
        best_metric = max(metrics, key=lambda m: m.improvement_ratio)
        worst_metric = min(metrics, key=lambda m: m.improvement_ratio)
        
        descriptions = {
            SignificanceLevel.INSIGNIFICANT: 
                f"{method_name} shows minimal improvement with no significant breakthrough.",
            SignificanceLevel.MINOR:
                f"{method_name} achieves minor improvement, primarily in {best_metric.name} ({best_metric.improvement_ratio:.1%}).",
            SignificanceLevel.MODERATE:
                f"{method_name} demonstrates moderate improvement with notable gains in {best_metric.name} ({best_metric.improvement_ratio:.1%}).",
            SignificanceLevel.MAJOR:
                f"{method_name} represents a major advancement with significant improvements across multiple metrics, especially {best_metric.name} ({best_metric.improvement_ratio:.1%}).",
            SignificanceLevel.BREAKTHROUGH:
                f"{method_name} constitutes a technological breakthrough with dramatic improvements in {best_metric.name} ({best_metric.improvement_ratio:.1%}) and overall system performance."
        }
        
        return descriptions.get(significance, f"{method_name}: Evaluation completed.")
        
    def validate_breakthrough(self, candidate: BreakthroughCandidate) -> Dict[str, Any]:
        """驗證突破候選"""
        validation_config = self.config['validation']
        
        # 統計顯著性檢查
        stat_significant = all(
            m.statistical_significance < validation_config['statistical_significance']
            for m in candidate.metrics
        )
        
        # 可重現性檢查
        reproducible = candidate.reproducibility >= validation_config['min_reproducibility']
        
        # 新穎性檢查
        novel = candidate.novelty_score >= validation_config['min_novelty_score']
        
        # 綜合驗證
        is_valid = (
            stat_significant and 
            reproducible and 
            novel and
            candidate.confidence_score >= 0.7
        )
        
        return {
            'is_valid_breakthrough': is_valid,
            'statistical_significance': stat_significant,
            'reproducibility': reproducible,
            'novelty': novel,
            'overall_confidence': candidate.confidence_score,
            'validation_timestamp': datetime.now().isoformat(),
            'recommendation': self._get_validation_recommendation(is_valid, candidate)
        }
        
    def _get_validation_recommendation(self, is_valid: bool, candidate: BreakthroughCandidate) -> str:
        """獲取驗證建議"""
        if is_valid:
            if candidate.significance == SignificanceLevel.BREAKTHROUGH:
                return "Validated breakthrough: Recommend immediate publication and patent filing."
            elif candidate.significance == SignificanceLevel.MAJOR:
                return "Validated major improvement: Recommend further optimization and deployment."
            else:
                return "Validated improvement: Consider implementation for specific use cases."
        else:
            if candidate.reproducibility < 0.8:
                return "Insufficient reproducibility: Require additional validation runs."
            elif candidate.novelty_score < 0.6:
                return "Low novelty: Consider integration with existing methods."
            else:
                return "Insufficient statistical significance: Increase sample size or refine methodology."
                
    def get_breakthrough_summary(self, days: int = 30) -> Dict[str, Any]:
        """獲取突破總結"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_breakthroughs = [
            bt for bt in self.detected_breakthroughs
            if bt.timestamp > cutoff_date
        ]
        
        if not recent_breakthroughs:
            return {
                'period_days': days,
                'total_breakthroughs': 0,
                'breakthrough_rate': 0,
                'summary': 'No breakthroughs detected in the specified period.'
            }
            
        # 統計分析
        breakthrough_types = {}
        significance_levels = {}
        
        for bt in recent_breakthroughs:
            # 按類型統計
            bt_type = bt.breakthrough_type.value
            breakthrough_types[bt_type] = breakthrough_types.get(bt_type, 0) + 1
            
            # 按顯著性統計
            sig_level = bt.significance.value
            significance_levels[sig_level] = significance_levels.get(sig_level, 0) + 1
            
        breakthrough_rate = len(recent_breakthroughs) / days
        
        return {
            'period_days': days,
            'total_breakthroughs': len(recent_breakthroughs),
            'breakthrough_rate': breakthrough_rate,
            'breakthrough_types': breakthrough_types,
            'significance_levels': significance_levels,
            'most_significant': max(recent_breakthroughs, key=lambda bt: bt.confidence_score) if recent_breakthroughs else None,
            'breakthrough_trend': 'increasing' if len(recent_breakthroughs) > len(self.detected_breakthroughs) // 2 else 'stable'
        }