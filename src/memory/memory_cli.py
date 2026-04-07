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

# Add core directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

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

    def analyze_command(self, args) -> int:
        """Analyze memory patterns and provide insights"""
        print("\n🔍 Analyzing Memory System Patterns...")
        print("=" * 70)

        try:
            if not self.manager:
                self.manager = init_memory_manager()

            # Get cache statistics
            stats = self.manager.get_cache_stats()
            
            # Get learning stats if available
            if hasattr(self.manager.cache, 'get_learning_stats'):
                learning_stats = self.manager.cache.get_learning_stats()
                
                print("\n[ACCESS PATTERNS]")
                print(f"  Total Unique Keys: {learning_stats['total_access_patterns']}")
                print(f"  Hot Keys (Most Accessed): {learning_stats['hot_keys_count']}")
                
                if learning_stats['hot_keys']:
                    print("\n  Top 10 Most Accessed Keys:")
                    for i, (key, count) in enumerate(learning_stats['hot_keys'][:10], 1):
                        print(f"    {i}. {key}: {count} accesses")

            # Performance insights
            print("\n[PERFORMANCE INSIGHTS]")
            hit_rate = stats['overall']['hit_rate_percent']
            print(f"  Cache Hit Rate: {hit_rate:.2f}%")
            
            if hit_rate > 90:
                print("  ✅ Excellent cache performance")
            elif hit_rate > 70:
                print("  ⚠️  Good cache performance, room for improvement")
            else:
                print("  ⚠️  Poor cache hit rate, consider increasing L1 size")

            # Compression insights
            print("\n[COMPRESSION INSIGHTS]")
            comp_ratio = stats['overall']['compression_ratio']
            print(f"  Average Compression Ratio: {comp_ratio:.2f}x")
            print(f"  Total Compressions: {stats['overall']['total_compressions']}")

            # AI Optimization
            print("\n[AI OPTIMIZATION]")
            if hasattr(self.manager, 'ai_optimize'):
                ai_result = self.manager.ai_optimize()
                print(f"  Status: {ai_result.get('status', 'active')}")
                if 'recommendations' in ai_result:
                    for rec in ai_result['recommendations']:
                        print(f"  💡 {rec['type']}: {rec['reason']}")

            print("\n" + "=" * 70)
            return 0

        except Exception as e:
            print(f"❌ Error in analysis: {e}")
            return 1

    def short_term_command(self, args) -> int:
        """Manage short-term memory"""
        if not self.manager:
            self.manager = init_memory_manager()

        try:
            if args.action == "list":
                print("\n📋 Short-Term Memory Entries")
                print("=" * 70)
                
                if hasattr(self.manager.cache, 'short_term'):
                    st = self.manager.cache.short_term
                    if st.entries:
                        for key, (value, created_at) in st.entries.items():
                            access_count = st.access_count.get(key, 0)
                            age = time.time() - created_at
                            ttl_remaining = max(0, st.ttl_seconds - age)
                            print(f"  {key}")
                            print(f"    - Age: {age:.1f}s")
                            print(f"    - TTL Remaining: {ttl_remaining:.1f}s")
                            print(f"    - Access Count: {access_count}")
                    else:
                        print("  (empty)")
                else:
                    print("❌ Short-term memory not available")
                    return 1

            elif args.action == "clear":
                print("🗑️  Clearing short-term memory...")
                if hasattr(self.manager.cache, 'short_term'):
                    self.manager.cache.short_term.clear()
                    print("✅ Short-term memory cleared!")
                else:
                    print("❌ Short-term memory not available")
                    return 1

            elif args.action == "stats":
                print("\n📊 Short-Term Memory Statistics")
                print("=" * 70)
                if hasattr(self.manager.cache, 'short_term'):
                    stats = self.manager.cache.short_term.stats()
                    print(f"  Total Entries: {stats['entries']}")
                    print(f"  Max Entries: {stats['max_entries']}")
                    print(f"  TTL (seconds): {stats['ttl_seconds']}")
                    print(f"  Utilization: {stats['utilization_percent']:.1f}%")
                else:
                    print("❌ Short-term memory not available")
                    return 1

            print("\n" + "=" * 70)
            return 0

        except Exception as e:
            print(f"❌ Error in short-term memory command: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def long_term_command(self, args) -> int:
        """Manage long-term memory"""
        if not self.manager:
            self.manager = init_memory_manager()

        try:
            if args.action == "list":
                print("\n📋 Long-Term Memory Entries")
                print("=" * 70)
                
                if hasattr(self.manager.cache, 'long_term'):
                    lt = self.manager.cache.long_term
                    
                    # Apply filters
                    metadata = lt.metadata
                    
                    if args.tag or args.min_importance:
                        filtered = {}
                        for key, meta in metadata.items():
                            # Check importance filter
                            if args.min_importance and meta.get('importance', 0) < args.min_importance:
                                continue
                            # Check tag filter
                            if args.tag and args.tag not in meta.get('tags', []):
                                continue
                            filtered[key] = meta
                        metadata = filtered
                        
                        if args.tag:
                            print(f"  Entries with tag '{args.tag}':")
                        if args.min_importance:
                            print(f"  Entries with importance >= {args.min_importance}:")
                    
                    if metadata:
                        for key, meta in metadata.items():
                            importance = meta.get('importance', 0.0)
                            tags = meta.get('tags', [])
                            access_count = meta.get('access_count', 0)
                            size_bytes = meta.get('size_bytes', 0)
                            print(f"  {key}")
                            print(f"    - Importance: {importance:.2f}")
                            print(f"    - Tags: {', '.join(tags) if tags else 'none'}")
                            print(f"    - Access Count: {access_count}")
                            print(f"    - Size: {size_bytes} bytes")
                    else:
                        print("  (no matching entries)")
                else:
                    print("❌ Long-term memory not available")
                    return 1

            elif args.action == "search":
                if not args.query:
                    print("❌ --query required for search action")
                    return 1
                
                print(f"\n🔍 Searching long-term memory for: '{args.query}'")
                print("=" * 70)
                
                if hasattr(self.manager.cache, 'long_term'):
                    lt = self.manager.cache.long_term
                    # Simple search by key substring
                    results = {k: v for k, v in lt.metadata.items() if args.query.lower() in k.lower()}
                    
                    if results:
                        for key, meta in results.items():
                            importance = meta.get('importance', 0.0)
                            print(f"  {key} (importance: {importance:.2f})")
                    else:
                        print("  (no results)")
                else:
                    print("❌ Long-term memory not available")
                    return 1

            elif args.action == "stats":
                print("\n📊 Long-Term Memory Statistics")
                print("=" * 70)
                
                if hasattr(self.manager.cache, 'long_term'):
                    stats = self.manager.cache.long_term.stats()
                    print(f"  Total Entries: {stats['entries']}")
                    print(f"  Total Size: {stats['total_size_mb']:.2f} MB")
                    
                    importance_dist = stats.get('importance_distribution', {})
                    if importance_dist:
                        print(f"\n  Importance Distribution:")
                        print(f"    - Critical (>0.8): {importance_dist.get('critical', 0)}")
                        print(f"    - High (0.5-0.8): {importance_dist.get('high', 0)}")
                        print(f"    - Medium (0.2-0.5): {importance_dist.get('medium', 0)}")
                        print(f"    - Low (<0.2): {importance_dist.get('low', 0)}")
                else:
                    print("❌ Long-term memory not available")
                    return 1

            print("\n" + "=" * 70)
            return 0

        except Exception as e:
            print(f"❌ Error in long-term memory command: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def migrate_command(self, args) -> int:
        """Migrate entries from short-term to long-term memory"""
        if not self.manager:
            self.manager = init_memory_manager()

        try:
            print("\n🔄 Running cleanup and migration from short-term to long-term...")
            
            if hasattr(self.manager, 'cleanup_short_term_memory'):
                stats = self.manager.cleanup_short_term_memory()
                print(f"✅ Migration completed!")
                print(f"  Expired entries: {stats.get('expired_count', 0)}")
                print(f"  Migrated to long-term: {stats.get('migrated_count', 0)}")
                print(f"  Deleted entries: {stats.get('deleted_count', 0)}")
            else:
                print("❌ Cleanup method not available")
                return 1

            return 0

        except Exception as e:
            print(f"❌ Error in migration: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def summary_command(self, args) -> int:
        """Show comprehensive memory summary"""
        if not self.manager:
            self.manager = init_memory_manager()

        try:
            print("\n📊 Memory System Summary")
            print("=" * 70)
            
            if hasattr(self.manager, 'memory_summary'):
                summary = self.manager.memory_summary()
                
                # Format short-term memory
                st = summary.get('short_term', {})
                print("\n[SHORT-TERM MEMORY]")
                print(f"  Entries: {st.get('entries', 0)}/{st.get('max_entries', 0)}")
                print(f"  Utilization: {st.get('utilization_percent', 0):.1f}%")
                print(f"  Expired: {st.get('expired_entries', 0)}")
                print(f"  TTL: {st.get('ttl_seconds', 0)}s")
                
                # Format long-term memory
                lt = summary.get('long_term', {})
                print("\n[LONG-TERM MEMORY]")
                print(f"  Entries: {lt.get('entries', 0)}")
                print(f"  Total Size: {lt.get('total_size_mb', 0):.2f} MB")
                importance_dist = lt.get('importance_distribution', {})
                if importance_dist:
                    print(f"  Importance Distribution:")
                    print(f"    - Critical (>0.8): {importance_dist.get('critical', 0)}")
                    print(f"    - High (0.5-0.8): {importance_dist.get('high', 0)}")
                    print(f"    - Medium (0.2-0.5): {importance_dist.get('medium', 0)}")
                    print(f"    - Low (<0.2): {importance_dist.get('low', 0)}")
                
                # Format cache statistics
                cache = summary.get('cache', {})
                overall = cache.get('overall', {})
                print("\n[CACHE PERFORMANCE]")
                print(f"  Total Hits: {overall.get('total_hits', 0)}")
                print(f"  Total Misses: {overall.get('total_misses', 0)}")
                print(f"  Hit Rate: {overall.get('hit_rate_percent', 0):.2f}%")
                print(f"  Memory Used: {overall.get('current_memory_mb', 0):.2f} MB")
                print(f"  Compression Ratio: {overall.get('compression_ratio', 1.0):.2f}x")
                
                # Format AI metrics
                ai = summary.get('ai_metrics', {})
                print("\n[AI METRICS]")
                print(f"  Learning Enabled: {ai.get('learning_enabled', False)}")
                print(f"  Adaptive L1 Size: {ai.get('adaptive_l1_size', 0)} MB")
                print(f"  Compression Threshold: {ai.get('optimal_compression_threshold', 0):.1f}%")
                print(f"  Hit Rate Target: {ai.get('cache_hit_target', 0):.2%}")
                print(f"  Optimization Count: {ai.get('optimization_count', 0)}")
                
                print("\n" + "=" * 70)
            else:
                print("❌ Summary method not available")
                return 1

            return 0

        except Exception as e:
            print(f"❌ Error in summary: {e}")
            import traceback
            traceback.print_exc()
            return 1

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

        # Analyze command
        analyze_parser = subparsers.add_parser("analyze", help="Analyze memory patterns and insights")

        # Activate command
        activate_parser = subparsers.add_parser("activate", help="Activate memory system")
        activate_parser.add_argument("--memory-file", default="memory.md", help="Memory file path")
        activate_parser.add_argument("--l1-size", type=int, default=100, help="L1 cache size in MB")
        activate_parser.add_argument("--update-md", action="store_true", help="Update memory.md")

        # Short-term memory command
        short_term_parser = subparsers.add_parser("short-term", help="Manage short-term memory")
        short_term_parser.add_argument(
            "--action",
            choices=["list", "clear", "stats"],
            default="list",
            help="Short-term memory action"
        )

        # Long-term memory command
        long_term_parser = subparsers.add_parser("long-term", help="Manage long-term memory")
        long_term_parser.add_argument(
            "--action",
            choices=["list", "search", "stats"],
            default="list",
            help="Long-term memory action"
        )
        long_term_parser.add_argument("--tag", help="Filter by tag")
        long_term_parser.add_argument("--min-importance", type=float, help="Filter by minimum importance")
        long_term_parser.add_argument("--query", help="Search query")

        # Migrate command
        migrate_parser = subparsers.add_parser("migrate", help="Migrate short-term to long-term memory")

        # Summary command
        summary_parser = subparsers.add_parser("summary", help="Show comprehensive memory summary")

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
        elif args.command == "analyze":
            return self.analyze_command(args)
        elif args.command == "activate":
            return self.activate_command(args)
        elif args.command == "short-term":
            return self.short_term_command(args)
        elif args.command == "long-term":
            return self.long_term_command(args)
        elif args.command == "migrate":
            return self.migrate_command(args)
        elif args.command == "summary":
            return self.summary_command(args)

        return 1


if __name__ == "__main__":
    cli = MemorySystemCLI()
    sys.exit(cli.run())
