#!/usr/bin/env python3
"""
統一交易系統初始化腳本
Initialize Unified Trading System

用法:
  python init_trading_system.py --setup         # 初始化配置文件
  python init_trading_system.py --test          # 運行測試
  python init_trading_system.py --dashboard     # 啟動儀表板
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_configs():
    """設置配置文件"""
    from .config_manager import ConfigManager, create_example_configs, BotConfig, BotType
    
    logger.info("Setting up configuration files...")
    
    # 創建配置目錄和示例文件
    create_example_configs()
    
    # 初始化配置管理器
    manager = ConfigManager()
    
    # 加載示例配置
    manager.load_all()
    
    # 驗證配置
    errors = manager.validate_configs()
    if errors:
        logger.warning(f"Config validation errors: {errors}")
    else:
        logger.info("All configurations are valid")
    
    # 保存配置
    manager.save_all()
    
    logger.info("Configuration setup complete")


async def test_system():
    """測試統一交易系統"""
    from .unified_trading_system import (
        BotConfig, BotType, get_bot_manager, TradingSignal, SignalType
    )
    from .config_manager import ConfigManager
    
    logger.info("Testing Unified Trading System...")
    
    # 初始化管理器
    config_manager = ConfigManager()
    config_manager.load_all()
    
    bot_manager = get_bot_manager()
    config_manager.apply_to_bot_manager(bot_manager)
    
    logger.info(f"Registered bots: {list(bot_manager.bots.keys())}")
    
    # 測試 Bot 連接
    logger.info("Testing bot connections...")
    results = await bot_manager.connect_all()
    
    for bot_name, success in results.items():
        status = "✓ Connected" if success else "✗ Failed"
        logger.info(f"  {bot_name}: {status}")
    
    # 測試信號執行
    logger.info("Testing signal execution...")
    
    test_signals = [
        TradingSignal(
            signal_id="TEST_001",
            signal_type=SignalType.BUY,
            symbol="BTC/USDT",
            quantity=1.0,
            confidence=0.8
        ),
        TradingSignal(
            signal_id="TEST_002",
            signal_type=SignalType.SELL,
            symbol="ETH/USDT",
            quantity=10.0,
            confidence=0.6
        ),
    ]
    
    for signal in test_signals:
        execution = await bot_manager.execute_signal(signal)
        logger.info(f"  Signal {signal.signal_id}: {execution.status}")
    
    # 測試指標
    logger.info("Testing metrics...")
    system_metrics = bot_manager.get_system_metrics()
    logger.info(f"  Total trades: {system_metrics['total_trades']}")
    logger.info(f"  Total PnL: ${system_metrics['total_pnl']:.2f}")
    logger.info(f"  Win rate: {system_metrics['win_rate']:.2%}")
    
    # 測試 Bot 切換
    logger.info("Testing bot switching...")
    bots = list(bot_manager.bots.keys())
    if len(bots) > 1:
        new_bot = bots[1]
        bot_manager.switch_active_bot(new_bot)
        logger.info(f"  Switched to: {new_bot}")
    
    # 斷開所有連接
    logger.info("Disconnecting bots...")
    await bot_manager.disconnect_all()
    
    logger.info("Testing complete!")


async def start_dashboard(host: str = "0.0.0.0", port: int = 8000):
    """啟動儀表板"""
    import uvicorn
    from .unified_dashboard import create_dashboard_app
    
    logger.info(f"Starting Unified Trading Dashboard on {host}:{port}")
    
    app = create_dashboard_app()
    
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()


async def interactive_shell():
    """交互式 Shell"""
    from .unified_trading_system import get_bot_manager, TradingSignal, SignalType
    from .config_manager import get_config_manager
    
    manager = get_bot_manager()
    config_manager = get_config_manager()
    
    logger.info("Starting interactive shell...")
    logger.info("Type 'help' for available commands")
    
    # 加載配置並連接 Bot
    config_manager.load_all()
    config_manager.apply_to_bot_manager(manager)
    await manager.connect_all()
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command == "exit" or command == "quit":
                logger.info("Exiting...")
                break
            
            elif command == "help":
                print("""
Available commands:
  list_bots        - List all registered bots
  status          - Show bot status
  switch <bot>    - Switch active bot
  execute         - Execute a test signal
  metrics         - Show system metrics
  exit/quit       - Exit shell
                """)
            
            elif command == "list_bots":
                bots = manager.get_bot_list()
                for bot in bots:
                    active = " (ACTIVE)" if bot["name"] == manager.active_bot else ""
                    print(f"  {bot['name']}{active}: {bot['status']}")
            
            elif command == "status":
                status = await manager.get_all_status()
                for bot_name, bot_status in status.items():
                    print(f"  {bot_name}: {bot_status}")
            
            elif command.startswith("switch "):
                bot_name = command[7:].strip()
                success = manager.switch_active_bot(bot_name)
                if success:
                    print(f"Switched to {bot_name}")
                else:
                    print(f"Failed to switch to {bot_name}")
            
            elif command == "execute":
                signal = TradingSignal(
                    signal_id="SHELL_001",
                    signal_type=SignalType.BUY,
                    symbol="BTC/USDT",
                    quantity=1.0,
                    confidence=0.7
                )
                execution = await manager.execute_signal(signal)
                print(f"Execution: {execution.status}")
            
            elif command == "metrics":
                metrics = manager.get_system_metrics()
                print(f"  Total trades: {metrics['total_trades']}")
                print(f"  Total PnL: ${metrics['total_pnl']:.2f}")
                print(f"  Win rate: {metrics['win_rate']:.2%}")
            
            else:
                print(f"Unknown command: {command}")
        
        except KeyboardInterrupt:
            logger.info("Interrupted")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
    
    # 清理資源
    await manager.disconnect_all()


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Unified Trading System"
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup configuration files"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run system tests"
    )
    
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Start the dashboard"
    )
    
    parser.add_argument(
        "--shell",
        action="store_true",
        help="Start interactive shell"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Dashboard host (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Dashboard port (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # 如果沒有指定任何參數，顯示幫助
    if not (args.setup or args.test or args.dashboard or args.shell):
        parser.print_help()
        return
    
    if args.setup:
        setup_configs()
    
    if args.test:
        asyncio.run(test_system())
    
    if args.shell:
        asyncio.run(interactive_shell())
    
    if args.dashboard:
        asyncio.run(start_dashboard(args.host, args.port))


if __name__ == "__main__":
    main()
