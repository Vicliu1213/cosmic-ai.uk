#!/usr/bin/env python3
"""
日誌面板 (Logging Dashboard)
日志面板查看工具 - 實時查看日誌和報告
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
import json

def print_header(title: str):
    """打印標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def view_recent_logs(category: str = "trading", lines: int = 20):
    """查看最近的日誌"""
    print_header(f"📋 最近 {lines} 行日誌 ({category}.log)")
    
    log_file = f"logs/{category}.log"
    if not os.path.exists(log_file):
        print(f"❌ 日誌文件不存在: {log_file}")
        print("\n💡 提示: 運行 python3 setup_logging_reports.py 創建日誌系統")
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        for i, line in enumerate(recent_lines, 1):
            print(f"{i:3d}. {line.rstrip()}")
        
        print(f"\n✅ 共 {len(all_lines)} 行日誌")
    except Exception as e:
        print(f"❌ 讀取日誌失敗: {e}")

def view_log_summary(category: str = "trading"):
    """查看日誌摘要"""
    print_header(f"📊 日誌統計摘要 ({category}.log)")
    
    log_file = f"logs/{category}.log"
    if not os.path.exists(log_file):
        print(f"❌ 日誌文件不存在: {log_file}")
        return
    
    summary = {
        'DEBUG': 0,
        'INFO': 0,
        'WARNING': 0,
        'ERROR': 0,
        'CRITICAL': 0,
        'total': 0
    }
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                summary['total'] += 1
                if 'DEBUG' in line:
                    summary['DEBUG'] += 1
                elif 'INFO' in line:
                    summary['INFO'] += 1
                elif 'WARNING' in line:
                    summary['WARNING'] += 1
                elif 'ERROR' in line:
                    summary['ERROR'] += 1
                elif 'CRITICAL' in line:
                    summary['CRITICAL'] += 1
        
        print(f"日誌級別分布:")
        print(f"  🔵 DEBUG    : {summary['DEBUG']:5d} 條")
        print(f"  🟢 INFO     : {summary['INFO']:5d} 條")
        print(f"  🟡 WARNING  : {summary['WARNING']:5d} 條")
        print(f"  🔴 ERROR    : {summary['ERROR']:5d} 條")
        print(f"  ⚫ CRITICAL : {summary['CRITICAL']:5d} 條")
        print(f"  ────────────────────")
        print(f"  📈 總計     : {summary['total']:5d} 條")
    except Exception as e:
        print(f"❌ 統計失敗: {e}")

def view_backtest_reports():
    """查看回測報告"""
    print_header("📊 回測報告列表")
    
    report_dir = "reports/backtest"
    if not os.path.exists(report_dir):
        print(f"❌ 目錄不存在: {report_dir}")
        return
    
    files = sorted(Path(report_dir).glob("*.csv"))
    if not files:
        print("❌ 沒有找到回測報告")
        return
    
    for i, f in enumerate(files, 1):
        size = os.path.getsize(f) / 1024  # KB
        mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i}. {f.name:40s} ({size:6.1f} KB) - {mtime}")
    
    # 顯示最新報告的內容
    if files:
        latest = files[-1]
        print(f"\n📄 最新報告: {latest.name}")
        print("-" * 80)
        try:
            with open(latest, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
                for line in lines:
                    print(line.rstrip())
            if len(lines) == 10:
                print(f"... (還有更多行)")
        except Exception as e:
            print(f"❌ 讀取報告失敗: {e}")

def view_daily_reports():
    """查看日常報告"""
    print_header("📊 日常報告列表")
    
    report_dir = "reports/daily"
    if not os.path.exists(report_dir):
        print(f"❌ 目錄不存在: {report_dir}")
        return
    
    files = sorted(Path(report_dir).glob("*.csv"))
    if not files:
        print("❌ 沒有找到日常報告")
        return
    
    for i, f in enumerate(files, 1):
        size = os.path.getsize(f) / 1024  # KB
        mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i}. {f.name:40s} ({size:6.1f} KB) - {mtime}")
    
    # 顯示最新報告的內容
    if files:
        latest = files[-1]
        print(f"\n📄 最新報告: {latest.name}")
        print("-" * 80)
        try:
            with open(latest, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
                for line in lines:
                    print(line.rstrip())
            if len(lines) == 10:
                print(f"... (還有更多行)")
        except Exception as e:
            print(f"❌ 讀取報告失敗: {e}")

def view_directory_structure():
    """查看目錄結構"""
    print_header("📁 日誌和報告目錄結構")
    
    dirs = {
        'logs': '日誌文件存儲',
        'reports/backtest': '回測報告',
        'reports/daily': '日常報告',
        'config': '配置文件'
    }
    
    for dir_path, description in dirs.items():
        print(f"\n📂 {dir_path}/ ({description})")
        
        if not os.path.exists(dir_path):
            print(f"  ❌ 目錄不存在")
            continue
        
        try:
            files = sorted(os.listdir(dir_path))
            if not files:
                print(f"  (空目錄)")
            else:
                for f in files[:10]:  # 只顯示前 10 個文件
                    full_path = os.path.join(dir_path, f)
                    if os.path.isfile(full_path):
                        size = os.path.getsize(full_path) / 1024
                        print(f"  📄 {f:40s} ({size:6.1f} KB)")
                    else:
                        print(f"  📁 {f}/")
                
                total = len(files)
                if total > 10:
                    print(f"  ... 還有 {total - 10} 個文件")
        except Exception as e:
            print(f"  ❌ 讀取目錄失敗: {e}")

def view_statistics():
    """查看統計信息"""
    print_header("📊 整體統計信息")
    
    # 統計日誌文件
    logs_stats = {}
    log_dir = "logs"
    if os.path.exists(log_dir):
        for f in os.listdir(log_dir):
            if f.endswith('.log'):
                size = os.path.getsize(os.path.join(log_dir, f)) / 1024
                logs_stats[f] = size
    
    # 統計報告文件
    reports_stats = {'backtest': 0, 'daily': 0}
    for category in ['backtest', 'daily']:
        dir_path = f"reports/{category}"
        if os.path.exists(dir_path):
            reports_stats[category] = len(os.listdir(dir_path))
    
    print("\n📋 日誌文件:")
    if logs_stats:
        total_size = sum(logs_stats.values())
        for filename, size in logs_stats.items():
            print(f"  {filename:20s}: {size:8.1f} KB")
        print(f"  {'總計':20s}: {total_size:8.1f} KB")
    else:
        print("  (沒有日誌文件)")
    
    print("\n📊 報告文件:")
    print(f"  回測報告: {reports_stats['backtest']} 個")
    print(f"  日常報告: {reports_stats['daily']} 個")

def search_logs(keyword: str, category: str = "trading"):
    """搜索日誌"""
    print_header(f"🔍 搜索日誌 (關鍵字: '{keyword}')")
    
    log_file = f"logs/{category}.log"
    if not os.path.exists(log_file):
        print(f"❌ 日誌文件不存在: {log_file}")
        return
    
    try:
        matches = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if keyword.lower() in line.lower():
                    matches.append((i, line.rstrip()))
        
        if matches:
            print(f"✅ 找到 {len(matches)} 條匹配結果:\n")
            for line_no, line in matches[:20]:  # 只顯示前 20 條
                print(f"行 {line_no}: {line}")
            
            if len(matches) > 20:
                print(f"\n... 還有 {len(matches) - 20} 條結果")
        else:
            print(f"❌ 沒有找到包含 '{keyword}' 的日誌")
    except Exception as e:
        print(f"❌ 搜索失敗: {e}")

def interactive_menu():
    """交互菜單"""
    while True:
        print("\n" + "=" * 80)
        print("  📊 日誌和報告查看面板")
        print("=" * 80)
        print("""
選項:
  1. 查看最近日誌 (trading.log)
  2. 查看系統日誌 (system.log)
  3. 查看 API 日誌 (api.log)
  4. 查看日誌統計
  5. 查看回測報告
  6. 查看日常報告
  7. 查看目錄結構
  8. 查看整體統計
  9. 搜索日誌
  0. 退出
        """)
        
        choice = input("請選擇 (0-9): ").strip()
        
        if choice == "1":
            lines = input("顯示行數 (默認 20): ").strip()
            view_recent_logs("trading", int(lines) if lines else 20)
        
        elif choice == "2":
            lines = input("顯示行數 (默認 20): ").strip()
            view_recent_logs("system", int(lines) if lines else 20)
        
        elif choice == "3":
            lines = input("顯示行數 (默認 20): ").strip()
            view_recent_logs("api", int(lines) if lines else 20)
        
        elif choice == "4":
            category = input("日誌類別 (trading/system/api, 默認 trading): ").strip()
            view_log_summary(category or "trading")
        
        elif choice == "5":
            view_backtest_reports()
        
        elif choice == "6":
            view_daily_reports()
        
        elif choice == "7":
            view_directory_structure()
        
        elif choice == "8":
            view_statistics()
        
        elif choice == "9":
            keyword = input("輸入搜索關鍵字: ").strip()
            category = input("日誌類別 (trading/system/api, 默認 trading): ").strip()
            if keyword:
                search_logs(keyword, category or "trading")
            else:
                print("❌ 請輸入有效的搜索關鍵字")
        
        elif choice == "0":
            print("\n👋 再見！\n")
            break
        
        else:
            print("❌ 無效的選項，請重新選擇")

def main():
    """主程序"""
    if len(sys.argv) > 1:
        # 命令行模式
        command = sys.argv[1]
        
        if command == "logs":
            category = sys.argv[2] if len(sys.argv) > 2 else "trading"
            lines = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            view_recent_logs(category, lines)
        
        elif command == "summary":
            category = sys.argv[2] if len(sys.argv) > 2 else "trading"
            view_log_summary(category)
        
        elif command == "backtest":
            view_backtest_reports()
        
        elif command == "daily":
            view_daily_reports()
        
        elif command == "dir":
            view_directory_structure()
        
        elif command == "stats":
            view_statistics()
        
        elif command == "search":
            if len(sys.argv) < 3:
                print("❌ 請提供搜索關鍵字")
                print(f"用法: python3 {sys.argv[0]} search <keyword> [category]")
                return
            keyword = sys.argv[2]
            category = sys.argv[3] if len(sys.argv) > 3 else "trading"
            search_logs(keyword, category)
        
        else:
            print(f"""
用法: python3 {sys.argv[0]} <command> [options]

命令:
  logs [category] [lines]     查看最近日誌
  summary [category]          查看日誌統計
  backtest                    查看回測報告
  daily                       查看日常報告
  dir                         查看目錄結構
  stats                       查看整體統計
  search <keyword> [category] 搜索日誌

示例:
  python3 {sys.argv[0]} logs trading 50
  python3 {sys.argv[0]} summary system
  python3 {sys.argv[0]} search "BTC" trading
  python3 {sys.argv[0]} backtest
            """)
    else:
        # 交互模式
        interactive_menu()

if __name__ == "__main__":
    main()
