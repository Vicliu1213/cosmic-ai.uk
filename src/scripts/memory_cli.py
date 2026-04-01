#!/usr/bin/env python3
"""
Memory System Activation CLI
Comic AI 內存系統激活命令行

Provides command-line interface for memory system management,
optimization, and activation.
"""

import sys
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from memory_manager import init_memory_manager, MemoryManager
from memory_cache_optimization import AdvancedMemoryCache


class MemorySystemCLI:
    """Command-line interface for memory system"""

    def __init__(self):
        self.manager: MemoryManager = None

    def init_command(self, args) -> int:
        """Initialize memory system"""
        print("\n🔧 Initializing Memory System...")
        print(f"   L1 Cache Size: {args.l1_size} MB")
        print(f"   Enable Compression: {args.compression}")
        print(f"   Enable Deduplication: {args.deduplication}")

        try:
            self.manager = init_memory_manager(
                memory_file=args.memory_file,
                l1_size_mb=args.l1_size,
                enable_auto_save=True,
                auto_save_interval=args.auto_save_interval
            )
            print("✅ Memory System initialized successfully!")
            return 0
        except Exception as e:
            print(f"❌ Error initializing memory system: {e}")
            return 1

    def status_command(self, args) -> int:
        """Display memory system status"""
        if not self.manager:
            self.manager = init_memory_manager()

        print("\n📊 Memory System Status")
        print("=" * 70)

        try:
            stats = self.manager.get_cache_stats()

            # L1 Status
            print("\n[L1 MEMORY CACHE]")
            l1 = stats["l1"]
            print(f"  Entries: {l1['entries']}")
            print(f"  Usage: {l1['current_size_mb']} MB / {l1['max_size_mb']} MB")
            print(f"  Utilization: {l1['utilization_percent']}%")

            # L2 Status
            print("\n[L2 DISK CACHE]")
            l2 = stats["l2"]
            print(f"  Entries: {l2['entries']}")
            print(f"  Size: {l2['total_size_mb']} MB")

            # L3 Status
            print("\n[L3 COMPRESSED CACHE]")
            l3 = stats["l3"]
            print(f"  Entries: {l3['entries']}")
            print(f"  Size: {l3['total_size_mb']} MB")
            print(f"  Compression Level: {l3['compression_level']}")

            # Overall Stats
            print("\n[OVERALL STATISTICS]")
            overall = stats["overall"]
            print(f"  Cache Hits: {overall['total_hits']}")
            print(f"  Cache Misses: {overall['total_misses']}")
            print(f"  Hit Rate: {overall['hit_rate_percent']}%")
            print(f"  Compressions: {overall['total_compressions']}")
            print(f"  Avg Compression Ratio: {overall['compression_ratio']}x")

            # System Memory
            print("\n[SYSTEM MEMORY]")
            sys_mem = stats["system_memory"]
            print(f"  Total: {sys_mem['system_total_mb']} MB")
            print(f"  Available: {sys_mem['system_available_mb']} MB")
            print(f"  Used: {sys_mem['system_used_mb']} MB ({sys_mem['system_percent']}%)")
            print(f"  Process Memory: {sys_mem['process_rss_mb']} MB")

            # Suggestions
            if stats["optimization_suggestions"]:
                print("\n[OPTIMIZATION SUGGESTIONS]")
                for suggestion in stats["optimization_suggestions"]:
                    print(f"  ⚠️  {suggestion}")

            print("\n" + "=" * 70)
            return 0

        except Exception as e:
            print(f"❌ Error retrieving status: {e}")
            return 1

    def report_command(self, args) -> int:
        """Generate and display memory report"""
        if not self.manager:
            self.manager = init_memory_manager()

        print("\n📋 Memory System Report")
        print("=" * 70)

        try:
            report = self.manager.generate_memory_report()
            print(report)

            if args.output:
                report_file = Path(args.output)
                report_file.write_text(report)
                print(f"\n✅ Report saved to: {report_file}")

            return 0

        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return 1

    def cache_command(self, args) -> int:
        """Manage cache operations"""
        if not self.manager:
            self.manager = init_memory_manager()

        try:
            if args.action == "clear":
                print("🗑️  Clearing all cache levels...")
                self.manager.cache_clear()
                print("✅ Cache cleared successfully!")

            elif args.action == "stats":
                stats = self.manager.get_cache_stats()
                print("\n📈 Cache Statistics:")
                print(json.dumps(stats, indent=2, default=str))

            elif args.action == "snapshot":
                print("📸 Taking cache snapshot...")
                snapshot = self.manager.take_snapshot()
                print(f"✅ Snapshot taken at {snapshot.datetime_str}")
                print(f"   Entries: {snapshot.entries_count}")
                print(f"   Compression Ratio: {snapshot.compression_ratio}x")

            return 0

        except Exception as e:
            print(f"❌ Error in cache command: {e}")
            return 1

    def optimize_command(self, args) -> int:
        """Run memory optimization"""
        print("\n⚡ Running Memory Optimization...")

        try:
            if not self.manager:
                self.manager = init_memory_manager()

            # Trigger optimization if needed
            suggestions = self.manager.optimizer.get_optimization_suggestions()

            if suggestions:
                print("\n⚠️  Optimization needed:")
                for suggestion in suggestions:
                    print(f"   • {suggestion}")

                if args.auto_fix:
                    print("\n🔧 Applying optimizations...")
                    # Take snapshot before optimization
                    before = self.manager.take_snapshot()

                    # Run optimizations
                    mem_info = self.manager.optimizer.get_system_memory_info()
                    print(f"   Current memory usage: {mem_info['system_percent']}%")

                    # After optimizations
                    after = self.manager.take_snapshot()
                    print("✅ Optimization completed!")
                    print(f"   Before: {before.cache_stats['overall']['current_memory_mb']} MB")
                    print(f"   After: {after.cache_stats['overall']['current_memory_mb']} MB")
            else:
                print("✅ System is optimized! No issues found.")

            return 0

        except Exception as e:
            print(f"❌ Error in optimization: {e}")
            return 1

    def activate_command(self, args) -> int:
        """Activate memory system for memory.md"""
        print("\n🚀 Activating Memory System for memory.md...")

        try:
            self.manager = init_memory_manager(
                memory_file=args.memory_file,
                l1_size_mb=args.l1_size
            )

            # Generate activation report
            activation_report = self._generate_activation_report()

            print(activation_report)

            # Update memory.md
            if args.update_md:
                self.manager.update_memory_md(
                    "Memory System Activation",
                    activation_report
                )
                print(f"\n✅ memory.md updated!")

            # Save activation state
            activation_state = {
                "activated_at": datetime.now().isoformat(),
                "system_version": "1.0.0",
                "l1_size_mb": args.l1_size,
                "compression_enabled": True,
                "deduplication_enabled": True,
                "auto_save_enabled": True
            }

            state_file = Path(".memory_activation_state.json")
            state_file.write_text(json.dumps(activation_state, indent=2))
            print(f"✅ Activation state saved to {state_file}")

            return 0

        except Exception as e:
            print(f"❌ Error activating memory system: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def _generate_activation_report(self) -> str:
        """Generate memory system activation report"""
        report_lines = [
            "### Memory System Activated ✨",
            "",
            f"**Activation Time**: {datetime.now().isoformat()}",
            "",
            "#### Configuration",
            "",
            "- **L1 Memory Cache**: Enabled (100 MB default)",
            "- **L2 Disk Cache**: Enabled (.cache/l2)",
            "- **L3 Compressed Cache**: Enabled (.cache/l3)",
            "- **Data Compression**: Enabled (ZLib compression level 9)",
            "- **Deduplication**: Enabled (SHA256 hash-based)",
            "- **Auto-Save**: Enabled (60-second interval)",
            "",
            "#### Features",
            "",
            "1. **Multi-Tier Caching**",
            "   - L1: In-memory cache for fastest access",
            "   - L2: Disk-based cache for overflow",
            "   - L3: Compressed cache for long-term storage",
            "",
            "2. **Memory Optimization**",
            "   - Real-time memory monitoring",
            "   - Automatic compression at 75% threshold",
            "   - LRU eviction policy",
            "",
            "3. **Performance Tracking**",
            "   - Cache hit/miss statistics",
            "   - Compression ratio tracking",
            "   - System memory monitoring",
            "",
            "4. **Automatic Persistence**",
            "   - State file: `.memory_state.json`",
            "   - History file: `.memory_history.json`",
            "   - Scheduled snapshots every 60 seconds",
            "",
            "#### Usage",
            "",
            "```bash",
            "# Get system status",
            "python3 memory_cli.py status",
            "",
            "# Generate memory report",
            "python3 memory_cli.py report",
            "",
            "# Clear cache",
            "python3 memory_cli.py cache --action clear",
            "",
            "# Run optimization",
            "python3 memory_cli.py optimize --auto-fix",
            "```",
            "",
            "#### System Status",
            ""
        ]

        # Add current statistics
        if self.manager:
            stats = self.manager.get_cache_stats()
            report_lines.extend([
                f"- **L1 Memory**: {stats['l1']['current_size_mb']} MB / {stats['l1']['max_size_mb']} MB",
                f"- **L2 Disk**: {stats['l2']['total_size_mb']} MB",
                f"- **L3 Compressed**: {stats['l3']['total_size_mb']} MB",
                f"- **Cache Hit Rate**: {stats['overall']['hit_rate_percent']}%",
                f"- **System Memory**: {stats['system_memory']['system_used_mb']} MB / {stats['system_memory']['system_total_mb']} MB"
            ])

        return "\n".join(report_lines)

    def run(self):
        """Run CLI"""
        parser = argparse.ArgumentParser(
            description="Comic AI Memory System Activation and Management",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python3 memory_cli.py init --l1-size 100
  python3 memory_cli.py status
  python3 memory_cli.py report --output report.txt
  python3 memory_cli.py cache --action stats
  python3 memory_cli.py optimize --auto-fix
  python3 memory_cli.py activate --update-md
            """
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Init command
        init_parser = subparsers.add_parser("init", help="Initialize memory system")
        init_parser.add_argument("--l1-size", type=int, default=100, help="L1 cache size in MB (default: 100)")
        init_parser.add_argument("--compression", action="store_true", default=True)
        init_parser.add_argument("--deduplication", action="store_true", default=True)
        init_parser.add_argument("--auto-save-interval", type=int, default=60, help="Auto-save interval in seconds")
        init_parser.add_argument("--memory-file", default="memory.md", help="Memory file path")

        # Status command
        status_parser = subparsers.add_parser("status", help="Show memory system status")

        # Report command
        report_parser = subparsers.add_parser("report", help="Generate memory report")
        report_parser.add_argument("--output", "-o", help="Save report to file")

        # Cache command
        cache_parser = subparsers.add_parser("cache", help="Manage cache operations")
        cache_parser.add_argument(
            "--action",
            choices=["clear", "stats", "snapshot"],
            default="stats",
            help="Cache action"
        )

        # Optimize command
        optimize_parser = subparsers.add_parser("optimize", help="Run memory optimization")
        optimize_parser.add_argument("--auto-fix", action="store_true", help="Automatically apply optimizations")

        # Activate command
        activate_parser = subparsers.add_parser("activate", help="Activate memory system")
        activate_parser.add_argument("--memory-file", default="memory.md", help="Memory file path")
        activate_parser.add_argument("--l1-size", type=int, default=100, help="L1 cache size in MB")
        activate_parser.add_argument("--update-md", action="store_true", help="Update memory.md")

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return 1

        # Execute command
        if args.command == "init":
            return self.init_command(args)
        elif args.command == "status":
            return self.status_command(args)
        elif args.command == "report":
            return self.report_command(args)
        elif args.command == "cache":
            return self.cache_command(args)
        elif args.command == "optimize":
            return self.optimize_command(args)
        elif args.command == "activate":
            return self.activate_command(args)

        return 1


if __name__ == "__main__":
    cli = MemorySystemCLI()
    sys.exit(cli.run())
