#!/usr/bin/env python3
"""
分層記憶管理工具 - Tiered Memory Management Tool
Comic AI 記憶系統分層管理實用工具

提供:
- 層級容量監控
- 自動遷移管理
- 性能分析
- 最佳實踐驗證
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# 添加核心模塊路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from memory_manager import init_memory_manager
from memory_cache_optimization import AdvancedMemoryCache


class TierName(Enum):
    """層級名稱"""
    L1 = "L1_MEMORY"
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"
    L2 = "L2_DISK"
    L3 = "L3_COMPRESSED"


@dataclass
class TierMetrics:
    """層級指標"""
    name: TierName
    capacity_limit: float  # MB 或條目數
    current_usage: float   # 當前使用
    entries: int           # 條目數
    hit_rate: float        # 命中率 (%)
    utilization: float     # 利用率 (%)
    status: str            # 狀態 (HEALTHY/WARNING/CRITICAL/FULL)
    compression_ratio: float = 1.0


class TierMonitor:
    """層級監控器"""
    
    def __init__(self, manager: 'MemoryManager'):
        self.manager = manager
        self.cache = manager.cache
        self.history = []  # 保存歷史數據
    
    def collect_metrics(self) -> Dict[TierName, TierMetrics]:
        """收集所有層級的性能指標"""
        stats = self.manager.get_cache_stats()
        
        metrics = {}
        
        # L1 指標
        l1_stats = stats['l1']
        metrics[TierName.L1] = TierMetrics(
            name=TierName.L1,
            capacity_limit=l1_stats['max_size_mb'],
            current_usage=l1_stats['current_size_mb'],
            entries=l1_stats['entries'],
            hit_rate=self._calculate_l1_hit_rate(stats),
            utilization=l1_stats['utilization_percent'],
            status=self._determine_status(l1_stats['utilization_percent'])
        )
        
        # 短期記憶指標
        st_entries = len(self.cache.short_term.entries)
        metrics[TierName.SHORT_TERM] = TierMetrics(
            name=TierName.SHORT_TERM,
            capacity_limit=1000,
            current_usage=st_entries,
            entries=st_entries,
            hit_rate=0.0,  # 待計算
            utilization=(st_entries / 1000) * 100,
            status=self._determine_status((st_entries / 1000) * 100)
        )
        
        # 長期記憶指標
        lt_stats = self.cache.long_term.stats()
        metrics[TierName.LONG_TERM] = TierMetrics(
            name=TierName.LONG_TERM,
            capacity_limit=5000,  # 估計容量
            current_usage=lt_stats['total_size_mb'],
            entries=lt_stats['entries'],
            hit_rate=0.0,  # 待計算
            utilization=(lt_stats['total_size_mb'] / 5000) * 100 if lt_stats['total_size_mb'] > 0 else 0,
            status=self._determine_status((lt_stats['total_size_mb'] / 5000) * 100)
        )
        
        # L2 指標
        l2_stats = stats['l2']
        metrics[TierName.L2] = TierMetrics(
            name=TierName.L2,
            capacity_limit=10000,
            current_usage=l2_stats['total_size_mb'],
            entries=l2_stats['entries'],
            hit_rate=0.0,
            utilization=(l2_stats['total_size_mb'] / 10000) * 100,
            status=self._determine_status((l2_stats['total_size_mb'] / 10000) * 100)
        )
        
        # L3 指標
        l3_stats = stats['l3']
        metrics[TierName.L3] = TierMetrics(
            name=TierName.L3,
            capacity_limit=50000,
            current_usage=l3_stats['total_size_mb'],
            entries=l3_stats['entries'],
            hit_rate=0.0,
            utilization=(l3_stats['total_size_mb'] / 50000) * 100,
            status=self._determine_status((l3_stats['total_size_mb'] / 50000) * 100),
            compression_ratio=l3_stats.get('compression_ratio', 1.0)
        )
        
        return metrics
    
    def _calculate_l1_hit_rate(self, stats: Dict) -> float:
        """計算 L1 命中率"""
        total = stats['overall']['total_hits'] + stats['overall']['total_misses']
        if total == 0:
            return 0.0
        return (stats['overall']['total_hits'] / total) * 100
    
    def _determine_status(self, utilization: float) -> str:
        """根據利用率決定狀態"""
        if utilization < 50:
            return "HEALTHY"
        elif utilization < 75:
            return "WARNING"
        elif utilization < 90:
            return "CRITICAL"
        else:
            return "FULL"
    
    def print_report(self, metrics: Dict[TierName, TierMetrics]):
        """打印層級報告"""
        print("\n📊 層級性能報告")
        print("=" * 80)
        
        for tier_name, metric in metrics.items():
            status_icon = {
                "HEALTHY": "✅",
                "WARNING": "⚠️ ",
                "CRITICAL": "🔴",
                "FULL": "❌"
            }.get(metric.status, "❓")
            
            print(f"\n{status_icon} {tier_name.value}")
            print(f"  容量: {metric.current_usage:.2f} / {metric.capacity_limit:.2f}")
            print(f"  利用率: {metric.utilization:.1f}%")
            print(f"  條目: {metric.entries}")
            print(f"  命中率: {metric.hit_rate:.1f}%")
            
            if metric.compression_ratio > 1.0:
                print(f"  壓縮比: {metric.compression_ratio:.2f}x")
        
        print("\n" + "=" * 80)
    
    def save_history(self, filepath: str = ".memory/tier_metrics.json"):
        """保存指標歷史"""
        metrics = self.collect_metrics()
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                tier.value: {
                    "utilization": m.utilization,
                    "status": m.status,
                    "entries": m.entries
                }
                for tier, m in metrics.items()
            }
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # 讀取現有歷史
        history = []
        if Path(filepath).exists():
            try:
                history = json.loads(Path(filepath).read_text())
            except:
                history = []
        
        # 添加新記錄（保持最近 100 條）
        history.append(history_entry)
        history = history[-100:]
        
        Path(filepath).write_text(json.dumps(history, indent=2))


class TierHealthAnalyzer:
    """層級健康分析器"""
    
    def __init__(self, monitor: TierMonitor):
        self.monitor = monitor
    
    def analyze(self) -> Dict[str, Any]:
        """分析層級健康狀況"""
        metrics = self.monitor.collect_metrics()
        
        issues = []
        recommendations = []
        
        # 檢查 L1
        l1_metric = metrics[TierName.L1]
        if l1_metric.utilization > 85:
            issues.append(f"⚠️ L1 利用率過高 ({l1_metric.utilization:.1f}%)")
            recommendations.append("建議: 增加 L1 容量或啟用更頻繁的驅逐")
        
        # 檢查短期記憶
        st_metric = metrics[TierName.SHORT_TERM]
        if st_metric.utilization > 90:
            issues.append(f"🔴 短期記憶快滿 ({st_metric.utilization:.1f}%)")
            recommendations.append("建議: 執行清理和遷移 (memory_cli.py migrate)")
        
        # 檢查長期記憶
        lt_metric = metrics[TierName.LONG_TERM]
        if lt_metric.entries > 10000:
            issues.append(f"⚠️ 長期記憶條目過多 ({lt_metric.entries})")
            recommendations.append("建議: 清理低重要性條目或存檔至外部")
        
        # 檢查整體命中率
        overall_hit_rate = l1_metric.hit_rate
        if overall_hit_rate < 80:
            issues.append(f"⚠️ 命中率偏低 ({overall_hit_rate:.1f}%)")
            recommendations.append("建議: 增加 L1 大小或優化訪問模式")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "healthy": len(issues) == 0,
            "issue_count": len(issues),
            "issues": issues,
            "recommendations": recommendations,
            "metrics_summary": {
                "l1_utilization": l1_metric.utilization,
                "st_utilization": st_metric.utilization,
                "lt_size_mb": lt_metric.current_usage,
                "overall_hit_rate": overall_hit_rate
            }
        }
    
    def print_analysis(self):
        """打印分析結果"""
        analysis = self.analyze()
        
        print("\n🔍 層級健康分析")
        print("=" * 80)
        
        if analysis['healthy']:
            print("✅ 系統狀態良好")
        else:
            print(f"⚠️ 發現 {analysis['issue_count']} 個問題:")
            for issue in analysis['issues']:
                print(f"  • {issue}")
            
            print("\n💡 建議:")
            for rec in analysis['recommendations']:
                print(f"  • {rec}")
        
        print("\n📈 指標摘要:")
        summary = analysis['metrics_summary']
        print(f"  L1 利用率: {summary['l1_utilization']:.1f}%")
        print(f"  短期利用率: {summary['st_utilization']:.1f}%")
        print(f"  長期大小: {summary['lt_size_mb']:.2f} MB")
        print(f"  命中率: {summary['overall_hit_rate']:.1f}%")
        
        print("\n" + "=" * 80)


class TierOptimizer:
    """層級優化器"""
    
    def __init__(self, manager: 'MemoryManager', monitor: TierMonitor):
        self.manager = manager
        self.monitor = monitor
    
    def auto_optimize(self):
        """自動優化層級"""
        metrics = self.monitor.collect_metrics()
        
        actions = []
        
        # 1. 檢查 L1 是否過滿
        if metrics[TierName.L1].utilization > 85:
            self.manager.cache.l1.clear()  # 強制清空冷數據
            actions.append("✓ 清空 L1 冷數據")
        
        # 2. 檢查短期記憶
        if metrics[TierName.SHORT_TERM].utilization > 80:
            cleanup_stats = self.manager.cleanup_short_term_memory()
            actions.append(
                f"✓ 短期清理: 遷移 {cleanup_stats['migrated_count']}, "
                f"刪除 {cleanup_stats['deleted_count']}"
            )
        
        # 3. 檢查長期記憶大小
        lt_stats = self.manager.cache.long_term.stats()
        if lt_stats['total_size_mb'] > 4000:
            # 提示需要存檔
            actions.append("⚠️ 長期記憶大小超過 4GB，建議進行存檔")
        
        return actions
    
    def suggest_tier_size(self):
        """建議層級大小"""
        metrics = self.monitor.collect_metrics()
        
        suggestions = {}
        
        # L1 大小建議
        l1_metric = metrics[TierName.L1]
        if l1_metric.utilization > 80:
            suggestions['L1'] = f"建議增加至 {l1_metric.capacity_limit * 1.5:.0f} MB"
        else:
            suggestions['L1'] = f"當前大小適當 ({l1_metric.capacity_limit:.0f} MB)"
        
        # 短期容量建議
        st_metric = metrics[TierName.SHORT_TERM]
        if st_metric.utilization > 90:
            suggestions['SHORT_TERM'] = f"建議增加至 2000 條"
        else:
            suggestions['SHORT_TERM'] = f"當前容量適當 (1000 條)"
        
        return suggestions


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="分層記憶管理工具")
    parser.add_argument(
        "command",
        choices=["monitor", "analyze", "optimize", "suggest"],
        help="執行命令"
    )
    parser.add_argument("--save-history", action="store_true", help="保存指標歷史")
    
    args = parser.parse_args()
    
    # 初始化管理器
    print("🔄 初始化記憶系統...")
    manager = init_memory_manager()
    monitor = TierMonitor(manager)
    
    if args.command == "monitor":
        # 監控命令
        metrics = monitor.collect_metrics()
        monitor.print_report(metrics)
        
        if args.save_history:
            monitor.save_history()
            print("✅ 指標已保存")
    
    elif args.command == "analyze":
        # 分析命令
        analyzer = TierHealthAnalyzer(monitor)
        analyzer.print_analysis()
    
    elif args.command == "optimize":
        # 優化命令
        optimizer = TierOptimizer(manager, monitor)
        actions = optimizer.auto_optimize()
        
        print("\n⚡ 優化操作:")
        for action in actions:
            print(f"  {action}")
    
    elif args.command == "suggest":
        # 建議命令
        optimizer = TierOptimizer(manager, monitor)
        suggestions = optimizer.suggest_tier_size()
        
        print("\n💡 層級大小建議:")
        for tier, suggestion in suggestions.items():
            print(f"  {tier}: {suggestion}")


if __name__ == "__main__":
    main()
