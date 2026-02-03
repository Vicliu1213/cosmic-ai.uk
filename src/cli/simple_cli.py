#!/usr/bin/env python3
"""
簡單清晰的 Comic AI CLI 對話框
"""

import sys
from stage1 import run_stage1, STAGE1_THEORIES


def main_menu():
    """主選單"""
    print("\n" + "="*50)
    print("           Comic AI 量子分析系統")
    print("="*50)
    print("請選擇操作:")
    print("1. 執行 Stage1 量子分析")
    print("2. 查看可用理論")
    print("3. 查看說明")
    print("4. 離開")
    print("="*50)
    
    while True:
        try:
            choice = input("請輸入選項 (1-4): ").strip()
            print(f"您選擇了: {choice}")
            
            if choice in ["1", "2", "3", "4"]:
                return choice
            else:
                print("錯誤: 請輸入 1-4 的數字")
        except KeyboardInterrupt:
            print("\n再見!")
            sys.exit(0)


def run_analysis():
    """執行分析"""
    print("\n正在執行量子分析...")
    print("分析四大理論: Heisenberg, Bekenstein, Bremermann, Landauer")
    
    try:
        results = run_stage1()
        print("\n" + "="*50)
        print("                分析結果")
        print("="*50)
        
        vector = results["stage1_vector"]
        print(f"精度: {vector['precision']:.2e}")
        print(f"壓縮: {vector['compression']:.2e}") 
        print(f"速度: {vector['speed']:.2e}")
        print(f"能源: {vector['energy']:.2e}")
        print("="*50)
        
    except Exception as e:
        print(f"分析失敗: {e}")
    
    input("\n按 Enter 繼續...")


def show_theories():
    """顯示理論"""
    print("\n" + "="*50)
    print("               可用理論")
    print("="*50)
    
    for key, theory in STAGE1_THEORIES.items():
        print(f"\n{theory.name}:")
        print(f"  類別: {theory.category}")
        print(f"  模型: {theory.math_model}")
        print(f"  說明: {theory.notes}")
    
    print("="*50)
    input("\n按 Enter 繼續...")


def show_help():
    """顯示說明"""
    print("\n" + "="*50)
    print("               使用說明")
    print("="*50)
    print("這是一個量子優勢分析工具")
    print("基於四大物理極限進行分析:")
    print("• Heisenberg 極限 - 量子精密測量")
    print("• Bekenstein 邊界 - 資訊壓縮極限")
    print("• Bremermann 極限 - 計算速度上限")
    print("• Landauer 原理 - 能源消耗下限")
    print("="*50)
    input("\n按 Enter 繼續...")


def main():
    """主程式"""
    print("啟動 Comic AI 系統...")
    
    while True:
        choice = main_menu()
        
        if choice == "1":
            run_analysis()
        elif choice == "2":
            show_theories()
        elif choice == "3":
            show_help()
        elif choice == "4":
            print("\n感謝使用!")
            break


if __name__ == "__main__":
    main()