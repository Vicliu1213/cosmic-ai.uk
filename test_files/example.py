#!/usr/bin/env python3
"""
示例 Python 程序
演示代碼分析功能
"""

def calculate_fibonacci(n):
    """計算費波那契數列"""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def main():
    # 計算前 10 個費波那契數
    for i in range(10):
        print(f"F({i}) = {calculate_fibonacci(i)}")

if __name__ == '__main__':
    main()
