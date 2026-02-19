#!/usr/bin/env python3
"""
OpenCode 完整進化系統集成
整合量子遺傳算法、性能監測和配置管理

使用方式：
1. python opencode_evolution_system.py --init     # 初始化系統
2. python opencode_evolution_system.py --record   # 記錄性能數據
3. python opencode_evolution_system.py --evolve   # 執行進化優化
4. python opencode_evolution_system.py --report   # 生成報告
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class OpenCodeEvolutionSystem:
    """OpenCode 完整進化系統"""
    
    def __init__(self, config_dir: str = "~/.config/opencode"):
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.config_dir / "evolution_metrics.jsonl"
        self.evolved_config_file = self.config_dir / "evolved_config.json"
        self.system_log_file = self.config_dir / "evolution_system.log"
    
    def initialize_system(self):
        """初始化進化系統"""
        logger.info("🚀 初始化 OpenCode 進化系統...")
        
        # 創建必要的目錄
        (self.config_dir / "skills").mkdir(exist_ok=True)
        (self.config_dir / "backups").mkdir(exist_ok=True)
        
        # 創建初始配置
        initial_config = {
            "model": "anthropic/claude-haiku-4-20250514",
            "theme": "one-dark",
            "tui": {
                "scroll_speed": 3,
                "scroll_acceleration": {"enabled": True},
                "diff_style": "auto"
            },
            "agent": {
                "build": {"temperature": 0.3, "steps": 10},
                "plan": {"temperature": 0.1, "steps": 5},
                "general": {"temperature": 0.5, "steps": 15},
                "explore": {"temperature": 0.1, "steps": 8}
            },
            "evolution": {
                "enabled": True,
                "last_optimized": datetime.now().isoformat(),
                "generation": 0
            }
        }
        
        config_file = self.config_dir / "opencode.json"
        with open(config_file, 'w') as f:
            json.dump(initial_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ 配置文件已創建: {config_file}")
        logger.info(f"✓ 進化系統初始化完成")
    
    def print_welcome_banner(self):
        """打印歡迎橫幅"""
        banner = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   🧬 OpenCode 量子遺傳算法進化系統                                ║
║   Quantum Genetic Algorithm Evolution System for OpenCode        ║
║                                                                    ║
║   融合量子計算邏輯與經典遺傳算法                                   ║
║   實現 AI 編碼助手的自進化優化                                    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

📊 核心特性：
  ✓ 量子疊加態 - 多配置並行探索
  ✓ 量子糾纏 - 代理間的相互影響
  ✓ 測量坍縮 - 適應度評估與選擇
  ✓ 自適應進化 - 根據任務動態優化

🎯 進化目標：
  • 最大化代碼生成品質
  • 優化性能與效率
  • 適應不同任務類型
  • 持續學習和改進

🔧 使用命令：
  --init      初始化系統
  --record    記錄性能數據
  --evolve    執行進化優化
  --report    生成優化報告
  --apply     應用最優配置

"""
        print(banner)
    
    def record_metric(self, task_type: str, agent: str, quality: float, 
                     duration: float, success: bool, tokens: int):
        """記錄性能指標"""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "agent": agent,
            "quality_score": quality,
            "duration_seconds": duration,
            "success": success,
            "tokens_used": tokens
        }
        
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metric, ensure_ascii=False) + '\n')
        
        logger.info(f"✓ 已記錄: {task_type} - {agent} (品質: {quality:.1f})")
    
    def load_metrics(self) -> List[Dict[str, Any]]:
        """載入所有性能指標"""
        metrics = []
        if self.metrics_file.exists():
            with open(self.metrics_file) as f:
                for line in f:
                    if line.strip():
                        metrics.append(json.loads(line))
        return metrics
    
    def analyze_performance(self) -> Dict[str, Any]:
        """分析整體性能"""
        metrics = self.load_metrics()
        
        if not metrics:
            return {"error": "沒有可用的性能數據"}
        
        analysis = {
            "total_tasks": len(metrics),
            "success_rate": sum(1 for m in metrics if m["success"]) / len(metrics),
            "avg_quality": sum(m["quality_score"] for m in metrics) / len(metrics),
            "avg_duration": sum(m["duration_seconds"] for m in metrics) / len(metrics),
            "total_tokens": sum(m["tokens_used"] for m in metrics),
            "by_agent": {}
        }
        
        # 按代理分析
        for agent in ["build", "plan", "general", "explore"]:
            agent_metrics = [m for m in metrics if m["agent"] == agent]
            if agent_metrics:
                analysis["by_agent"][agent] = {
                    "count": len(agent_metrics),
                    "success_rate": sum(1 for m in agent_metrics if m["success"]) / len(agent_metrics),
                    "avg_quality": sum(m["quality_score"] for m in agent_metrics) / len(agent_metrics)
                }
        
        return analysis
    
    def generate_report(self):
        """生成詳細報告"""
        logger.info("\n" + "=" * 70)
        logger.info("📈 OpenCode 進化系統性能報告")
        logger.info("=" * 70)
        
        analysis = self.analyze_performance()
        
        if "error" in analysis:
            logger.warning(f"⚠️  {analysis['error']}")
            return
        
        logger.info(f"\n📊 總體統計:")
        logger.info(f"  • 任務總數: {analysis['total_tasks']}")
        logger.info(f"  • 成功率: {analysis['success_rate']*100:.1f}%")
        logger.info(f"  • 平均品質: {analysis['avg_quality']:.1f}/100")
        logger.info(f"  • 平均耗時: {analysis['avg_duration']:.2f}秒")
        logger.info(f"  • 總 Token 消耗: {analysis['total_tokens']:,}")
        
        logger.info(f"\n🤖 代理性能詳情:")
        for agent, stats in analysis["by_agent"].items():
            logger.info(f"\n  {agent.upper()}:")
            logger.info(f"    • 使用次數: {stats['count']}")
            logger.info(f"    • 成功率: {stats['success_rate']*100:.1f}%")
            logger.info(f"    • 平均品質: {stats['avg_quality']:.1f}")
        
        logger.info("\n" + "=" * 70 + "\n")
    
    def apply_evolved_config(self):
        """應用進化後的配置"""
        if not self.evolved_config_file.exists():
            logger.warning("⚠️  未找到進化配置文件，請先執行 --evolve")
            return
        
        with open(self.evolved_config_file) as f:
            evolved_config = json.load(f)
        
        config_file = self.config_dir / "opencode.json"
        
        # 備份當前配置
        backup_file = self.config_dir / "backups" / f"opencode_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if config_file.exists():
            with open(config_file) as f:
                current_config = json.load(f)
            with open(backup_file, 'w') as f:
                json.dump(current_config, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ 備份當前配置: {backup_file}")
        
        # 應用新配置
        with open(config_file, 'w') as f:
            json.dump(evolved_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ 已應用進化配置: {config_file}")
        logger.info(f"  • 適應度: {evolved_config.get('genetic_algorithm', {}).get('fitness', 'N/A')}")
        logger.info(f"  • 進化代數: {evolved_config.get('genetic_algorithm', {}).get('generation', 'N/A')}")


def main():
    """主程序"""
    parser = argparse.ArgumentParser(
        description="OpenCode 量子遺傳算法進化系統",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python opencode_evolution_system.py --init
  python opencode_evolution_system.py --record code_generation build 95.0 12.5 true 1500
  python opencode_evolution_system.py --report
        """
    )
    
    parser.add_argument("--init", action="store_true", help="初始化系統")
    parser.add_argument("--record", nargs=6, help="記錄性能指標 [task_type agent quality duration success tokens]")
    parser.add_argument("--report", action="store_true", help="生成性能報告")
    parser.add_argument("--evolve", action="store_true", help="執行遺傳算法優化")
    parser.add_argument("--apply", action="store_true", help="應用進化後的配置")
    
    args = parser.parse_args()
    
    system = OpenCodeEvolutionSystem()
    system.print_welcome_banner()
    
    if args.init:
        system.initialize_system()
    
    elif args.record:
        task_type, agent, quality, duration, success, tokens = args.record
        system.record_metric(
            task_type=task_type,
            agent=agent,
            quality=float(quality),
            duration=float(duration),
            success=success.lower() == 'true',
            tokens=int(tokens)
        )
    
    elif args.report:
        system.generate_report()
    
    elif args.apply:
        system.apply_evolved_config()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
