#!/usr/bin/env python3
"""
防閃退和斷線重連系統 - 快速測試
Quick Test for Crash Prevention & Auto-Reconnection System
"""

import sys
sys.path.insert(0, '/root/comic_ai')

from system_robustness import RobustConnection, ReconnectionConfig
import time


def test_basic_connection():
    """測試基本連接"""
    print("\n" + "=" * 60)
    print("✅ 測試1: 基本連接")
    print("=" * 60)

    def mock_connect():
        return {"status": "connected"}

    connection = RobustConnection(
        name="Test Server",
        connect_func=mock_connect
    )

    result = connection.connect()
    print(f"連接結果: {'✅ 成功' if result else '❌ 失敗'}")

    status = connection.get_status()
    print(f"連接狀態: {status['state']}")
    print(f"成功次數: {status['metrics']['successful_connections']}")


def test_reconnection_with_failures():
    """測試失敗後的重連"""
    print("\n" + "=" * 60)
    print("✅ 測試2: 失敗後重連")
    print("=" * 60)

    attempt = [0]

    def mock_connect_with_failure():
        attempt[0] += 1
        if attempt[0] < 3:
            raise ConnectionError(f"連接失敗 (嘗試 #{attempt[0]})")
        return {"status": "connected"}

    connection = RobustConnection(
        name="Retry Server",
        connect_func=mock_connect_with_failure,
        config=ReconnectionConfig(max_retries=5, initial_delay=0.1)
    )

    result = connection.connect()
    print(f"連接結果: {'✅ 成功' if result else '❌ 失敗'}")

    status = connection.get_status()
    print(f"總嘗試次數: {len(status['connection_history'])}")
    print(f"成功次數: {status['metrics']['successful_connections']}")
    print(f"失敗次數: {status['metrics']['failed_connections']}")


def test_health_check():
    """測試健康檢查"""
    print("\n" + "=" * 60)
    print("✅ 測試3: 健康檢查")
    print("=" * 60)

    def mock_connect():
        return {"status": "connected"}

    check_count = [0]

    def mock_health_check():
        check_count[0] += 1
        return True

    connection = RobustConnection(
        name="Health Check Server",
        connect_func=mock_connect,
        health_check_func=mock_health_check,
        config=ReconnectionConfig(health_check_interval=1.0)
    )

    connection.connect()
    print("✅ 已連接")

    print("啟動健康檢查 (3秒)...")
    connection.start_health_check()
    time.sleep(3)
    connection.stop_health_check()

    print(f"健康檢查執行次數: {check_count[0]}")


def test_connection_failure():
    """測試連接失敗"""
    print("\n" + "=" * 60)
    print("✅ 測試4: 連接完全失敗")
    print("=" * 60)

    def mock_connect():
        raise ConnectionError("服務不可用")

    connection = RobustConnection(
        name="Failed Server",
        connect_func=mock_connect,
        config=ReconnectionConfig(max_retries=2, initial_delay=0.1)
    )

    result = connection.connect()
    print(f"連接結果: {'✅ 成功' if result else '❌ 失敗 (預期)'}")

    status = connection.get_status()
    print(f"連接狀態: {status['state']}")
    print(f"失敗次數: {status['metrics']['failed_connections']}")
    if status['metrics']['last_error']:
        print(f"最後錯誤: {status['metrics']['last_error']}")


def main():
    """主測試函數"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  防閃退和斷線重連系統 - 快速測試".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    try:
        test_basic_connection()
        test_reconnection_with_failures()
        test_health_check()
        test_connection_failure()

        print("\n" + "=" * 60)
        print("✅ 所有測試完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
