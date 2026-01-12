#!/usr/bin/env python3
"""
便捷测试运行脚本
提供交互式菜单选择测试场景
"""
import asyncio
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from test_scenarios import TestScenarios
from concurrent_test import ConcurrentTester


def print_menu():
    """打印菜单"""
    print("\n" + "="*60)
    print("涉密研判接口并发性能测试")
    print("="*60)
    print("1. 基础并发测试 (测试不同并发级别的性能)")
    print("2. 阶梯压力测试 (逐步增加并发数)")
    print("3. 突发流量测试 (瞬间大量并发)")
    print("4. 稳定性测试 (长时间运行)")
    print("5. 运行所有场景")
    print("6. 快速测试 (5并发, 10请求)")
    print("0. 退出")
    print("="*60)


async def quick_test():
    """快速测试"""
    print("\n开始快速测试...")
    tester = ConcurrentTester()
    stats = await tester.test_concurrent(
        concurrency=5,
        total_requests=10,
        verbose=True
    )
    tester.print_statistics(stats)


async def main():
    """主函数"""
    scenarios = TestScenarios()
    
    while True:
        print_menu()
        choice = input("\n请选择测试场景 (0-6): ").strip()
        
        if choice == "0":
            print("退出测试")
            break
        elif choice == "1":
            await scenarios.scenario_basic_concurrent()
        elif choice == "2":
            await scenarios.scenario_ramp_up()
        elif choice == "3":
            await scenarios.scenario_burst_traffic()
        elif choice == "4":
            print("⚠️  稳定性测试需要较长时间，确认继续？(y/n): ", end="")
            if input().strip().lower() == 'y':
                await scenarios.scenario_stability()
            else:
                print("已取消")
        elif choice == "5":
            print("⚠️  将运行所有测试场景，可能需要很长时间，确认继续？(y/n): ", end="")
            if input().strip().lower() == 'y':
                await scenarios.run_all_scenarios()
            else:
                print("已取消")
        elif choice == "6":
            await quick_test()
        else:
            print("❌ 无效选择，请重新输入")
        
        print("\n按 Enter 继续...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试已中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

