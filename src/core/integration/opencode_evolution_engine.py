#!/usr/bin/env python3
"""
OpenCode 自進化配置引擎
配置自動學習、評估和優化系統
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict, field
import statistics
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """性能指標"""
    task_type: str  # 'code_generation', 'analysis', 'refactor', 'debug'
    agent_used: str  # 'build', 'plan', 'general', 'explore'
    model_used: str  # 'claude-haiku-4', etc
    duration_seconds: float
    success: bool
    quality_score: float  # 0-100
    tokens_used: int
    timestamp: str
    feedback: str = ""


@dataclass
class ConfigurationVariant:
    """配置變體"""
    name: str
    config: Dict[str, Any]
    average_score: float = 0.0
    trial_count: int = 0
    success_rate: float = 0.0
    best_for_tasks: List[str] = field(default_factory=list)


class EvolutionEngine:
    """OpenCode 配置進化引擎"""

    def __init__(self, config_dir: str = "~/.config/opencode"):
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.config_dir / "evolution_metrics.jsonl"
        self.variants_file = self.config_dir / "config_variants.json"
        self.history_file = self.config_dir / "evolution_history.json"
        
        self.metrics: List[PerformanceMetric] = []
        self.variants: Dict[str, ConfigurationVariant] = {}
        
        self._load_existing_data()

    def _load_existing_data(self):
        """載入現有的進化數據"""
        if self.metrics_file.exists():
            with open(self.metrics_file) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.metrics.append(PerformanceMetric(**data))
        
        if self.variants_file.exists():
            with open(self.variants_file) as f:
                data = json.load(f)
                self.variants = {
                    name: ConfigurationVariant(**variant)
                    for name, variant in data.items()
                }

    def record_metric(self, metric: PerformanceMetric) -> None:
        """記錄性能指標"""
        self.metrics.append(metric)
        
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(asdict(metric)) + '\n')
        
        logger.info(f"記錄指標: {metric.task_type} - {metric.agent_used} "
                   f"(品質: {metric.quality_score:.1f}, 成功: {metric.success})")

    def analyze_agent_performance(self, agent: str) -> Dict[str, Any]:
        """分析特定代理的性能"""
        agent_metrics = [m for m in self.metrics if m.agent_used == agent]
        
        if not agent_metrics:
            return {"error": "沒有此代理的數據"}
        
        quality_scores = [m.quality_score for m in agent_metrics if m.success]
        durations = [m.duration_seconds for m in agent_metrics]
        
        return {
            "agent": agent,
            "total_trials": len(agent_metrics),
            "success_rate": sum(1 for m in agent_metrics if m.success) / len(agent_metrics),
            "avg_quality": statistics.mean(quality_scores) if quality_scores else 0,
            "max_quality": max(quality_scores) if quality_scores else 0,
            "avg_duration": statistics.mean(durations),
            "best_for_tasks": self._identify_best_tasks(agent_metrics)
        }

    def analyze_task_performance(self, task_type: str) -> Dict[str, Any]:
        """分析特定任務類型的性能"""
        task_metrics = [m for m in self.metrics if m.task_type == task_type]
        
        if not task_metrics:
            return {"error": "沒有此任務的數據"}
        
        by_agent = {}
        for metric in task_metrics:
            if metric.agent_used not in by_agent:
                by_agent[metric.agent_used] = []
            by_agent[metric.agent_used].append(metric)
        
        agent_scores = {}
        for agent, metrics in by_agent.items():
            successful = [m.quality_score for m in metrics if m.success]
            agent_scores[agent] = {
                "avg_quality": statistics.mean(successful) if successful else 0,
                "success_rate": sum(1 for m in metrics if m.success) / len(metrics),
                "trials": len(metrics)
            }
        
        best_agent = max(agent_scores.items(), 
                        key=lambda x: x[1]["avg_quality"])[0]
        
        return {
            "task_type": task_type,
            "agents_performance": agent_scores,
            "recommended_agent": best_agent,
            "total_trials": len(task_metrics)
        }

    def recommend_configuration(self, task_type: str) -> Dict[str, Any]:
        """為任務推薦最佳配置"""
        task_analysis = self.analyze_task_performance(task_type)
        
        if "error" in task_analysis:
            return self._get_default_recommendation(task_type)
        
        best_agent = task_analysis.get("recommended_agent", "build")
        
        return {
            "recommended_agent": best_agent,
            "reasoning": f"基於 {task_analysis['total_trials']} 次試驗",
            "performance": task_analysis["agents_performance"],
            "confidence": len(self.metrics) / 50  # 樣本量越大信心越高
        }

    def suggest_config_adjustment(self) -> List[Dict[str, Any]]:
        """根據歷史數據建議配置調整"""
        suggestions = []
        
        # 分析所有代理
        for agent in ['build', 'plan', 'general', 'explore']:
            perf = self.analyze_agent_performance(agent)
            
            if "error" in perf:
                continue
            
            # 如果成功率低於 70%，建議調整
            if perf["success_rate"] < 0.7:
                suggestions.append({
                    "type": "low_success_rate",
                    "agent": agent,
                    "success_rate": perf["success_rate"],
                    "suggestion": f"考慮為 {agent} 增加 step 限制或調整溫度"
                })
            
            # 如果平均時間超過 30 秒，建議優化
            if perf.get("avg_duration", 0) > 30:
                suggestions.append({
                    "type": "slow_performance",
                    "agent": agent,
                    "duration": perf["avg_duration"],
                    "suggestion": f"考慮為 {agent} 使用更快的模型或減少 step 數"
                })
        
        return suggestions

    def generate_evolution_report(self) -> str:
        """生成進化報告"""
        report = []
        report.append("=" * 60)
        report.append("OpenCode 進化引擎報告")
        report.append(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        report.append(f"\n📊 總體統計:")
        report.append(f"  • 總試驗次數: {len(self.metrics)}")
        
        successful = sum(1 for m in self.metrics if m.success)
        report.append(f"  • 成功次數: {successful} ({successful/len(self.metrics)*100:.1f}%)")
        
        avg_quality = statistics.mean([m.quality_score for m in self.metrics])
        report.append(f"  • 平均品質得分: {avg_quality:.1f}/100")
        
        report.append(f"\n🤖 代理性能分析:")
        for agent in ['build', 'plan', 'general', 'explore']:
            perf = self.analyze_agent_performance(agent)
            if "error" not in perf:
                report.append(f"\n  {agent}:")
                report.append(f"    • 成功率: {perf['success_rate']*100:.1f}%")
                report.append(f"    • 平均品質: {perf['avg_quality']:.1f}")
                report.append(f"    • 最佳任務: {', '.join(perf['best_for_tasks'][:3])}")
        
        report.append(f"\n💡 配置建議:")
        suggestions = self.suggest_config_adjustment()
        if suggestions:
            for sugg in suggestions[:5]:
                report.append(f"  • {sugg['suggestion']}")
        else:
            report.append("  ✓ 當前配置表現良好，無需調整")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)

    def _identify_best_tasks(self, metrics: List[PerformanceMetric]) -> List[str]:
        """識別代理最適合的任務"""
        task_counts = {}
        for m in metrics:
            if m.success and m.quality_score > 80:
                task_counts[m.task_type] = task_counts.get(m.task_type, 0) + 1
        
        return sorted(task_counts.keys(), key=lambda x: task_counts[x], reverse=True)

    def _get_default_recommendation(self, task_type: str) -> Dict[str, Any]:
        """獲得默認推薦"""
        defaults = {
            "code_generation": "build",
            "analysis": "plan",
            "refactor": "build",
            "debug": "explore",
        }
        
        return {
            "recommended_agent": defaults.get(task_type, "build"),
            "reasoning": "基於預設規則（無歷史數據）",
            "confidence": 0.5
        }

    def export_best_config(self) -> Dict[str, Any]:
        """導出最佳配置"""
        if not self.metrics:
            return self._get_default_opencode_config()
        
        # 分析最有效的配置組合
        best_metrics = sorted(
            self.metrics,
            key=lambda m: m.quality_score,
            reverse=True
        )[:10]
        
        agents_stats = {}
        for agent in ['build', 'plan', 'general', 'explore']:
            perf = self.analyze_agent_performance(agent)
            if "error" not in perf:
                agents_stats[agent] = perf
        
        return {
            "generated_at": datetime.now().isoformat(),
            "based_on_trials": len(self.metrics),
            "agent_recommendations": agents_stats,
            "notes": "根據實際性能數據生成的最佳配置"
        }

    @staticmethod
    def _get_default_opencode_config() -> Dict[str, Any]:
        """默認 OpenCode 配置"""
        return {
            "model": "anthropic/claude-haiku-4-20250514",
            "theme": "one-dark",
            "agent": {
                "build": {"temperature": 0.3, "steps": 10},
                "plan": {"temperature": 0.1, "steps": 5},
                "general": {"temperature": 0.5, "steps": 15},
                "explore": {"temperature": 0.1, "steps": 8}
            }
        }


def main():
    """主程序"""
    engine = EvolutionEngine()
    
    # 示例：記錄一些測試指標
    sample_metrics = [
        PerformanceMetric(
            task_type="code_generation",
            agent_used="build",
            model_used="claude-haiku-4",
            duration_seconds=15.5,
            success=True,
            quality_score=92.0,
            tokens_used=1250,
            timestamp=datetime.now().isoformat()
        ),
        PerformanceMetric(
            task_type="analysis",
            agent_used="plan",
            model_used="claude-haiku-4",
            duration_seconds=8.2,
            success=True,
            quality_score=85.0,
            tokens_used=950,
            timestamp=datetime.now().isoformat()
        ),
    ]
    
    for metric in sample_metrics:
        engine.record_metric(metric)
    
    # 生成報告
    print(engine.generate_evolution_report())
    
    # 導出最佳配置
    print("\n最佳配置:")
    print(json.dumps(engine.export_best_config(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
