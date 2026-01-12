"""
测试场景脚本
包含多种测试场景：基础并发、阶梯压力、突发流量、稳定性测试
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from concurrent_test import ConcurrentTester
from config import TEST_CONFIG


class TestScenarios:
    """测试场景集合"""
    
    def __init__(self):
        self.tester = ConcurrentTester()
        self.results_dir = TEST_CONFIG["results_dir"]
        self.all_results: Dict[str, Any] = {}
    
    def save_result(self, scenario_name: str, result: Dict[str, Any]):
        """保存测试结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{scenario_name}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        result_data = {
            "scenario": scenario_name,
            "timestamp": timestamp,
            "result": result
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 结果已保存到: {filepath}")
        return filepath
    
    async def scenario_basic_concurrent(self):
        """
        场景1: 基础并发测试
        测试不同并发级别的性能表现
        """
        print("\n" + "="*60)
        print("场景1: 基础并发测试")
        print("="*60)
        
        results = {}
        concurrency_levels = TEST_CONFIG["concurrency_levels"]
        requests_per_level = TEST_CONFIG["requests_per_level"]
        
        for concurrency in concurrency_levels:
            print(f"\n测试并发数: {concurrency}")
            stats = await self.tester.test_concurrent(
                concurrency=concurrency,
                total_requests=requests_per_level,
                verbose=False
            )
            self.tester.print_statistics(stats)
            results[f"concurrency_{concurrency}"] = stats
        
        self.all_results["basic_concurrent"] = results
        self.save_result("basic_concurrent", results)
        return results
    
    async def scenario_ramp_up(self):
        """
        场景2: 阶梯式压力测试
        逐步增加并发数，观察系统性能变化
        """
        print("\n" + "="*60)
        print("场景2: 阶梯式压力测试")
        print("="*60)
        
        config = TEST_CONFIG["ramp_up"]
        start_concurrency = config["start_concurrency"]
        max_concurrency = config["max_concurrency"]
        step = config["step"]
        step_interval = config["step_interval"]
        
        results = {}
        current_concurrency = start_concurrency
        
        while current_concurrency <= max_concurrency:
            print(f"\n当前并发数: {current_concurrency}")
            stats = await self.tester.test_concurrent(
                concurrency=current_concurrency,
                total_requests=current_concurrency * 2,  # 每个级别发送 2 倍并发数的请求
                verbose=False
            )
            self.tester.print_statistics(stats)
            results[f"concurrency_{current_concurrency}"] = stats
            
            if current_concurrency < max_concurrency:
                print(f"等待 {step_interval} 秒后继续...")
                await asyncio.sleep(step_interval)
            
            current_concurrency += step
        
        self.all_results["ramp_up"] = results
        self.save_result("ramp_up", results)
        return results
    
    async def scenario_burst_traffic(self):
        """
        场景3: 突发流量测试
        瞬间启动大量并发请求，测试系统应对突发流量的能力
        """
        print("\n" + "="*60)
        print("场景3: 突发流量测试")
        print("="*60)
        
        config = TEST_CONFIG["burst_test"]
        concurrency = config["concurrency"]
        duration = config["duration"]
        
        print(f"并发数: {concurrency}")
        print(f"持续时间: {duration}秒")
        print(f"模拟突发流量场景...")
        
        # 计算需要发送的请求数（假设每个请求平均10秒，持续时间内可以发送多轮）
        requests_per_round = concurrency
        total_rounds = max(1, duration // 10)  # 假设平均响应时间10秒
        total_requests = requests_per_round * total_rounds
        
        stats = await self.tester.test_concurrent(
            concurrency=concurrency,
            total_requests=total_requests,
            verbose=False
        )
        
        self.tester.print_statistics(stats)
        
        results = {
            "concurrency": concurrency,
            "duration": duration,
            "total_requests": total_requests,
            "stats": stats
        }
        
        self.all_results["burst_traffic"] = results
        self.save_result("burst_traffic", results)
        return results
    
    async def scenario_stability(self):
        """
        场景4: 长时间稳定性测试
        持续运行一段时间，检查是否有内存泄漏、性能衰减等问题
        """
        print("\n" + "="*60)
        print("场景4: 长时间稳定性测试")
        print("="*60)
        
        config = TEST_CONFIG["stability_test"]
        concurrency = config["concurrency"]
        duration = config["duration"]
        
        print(f"并发数: {concurrency}")
        print(f"持续时间: {duration}秒 ({duration//60}分钟)")
        print(f"开始长时间稳定性测试...")
        
        # 分段测试，每5分钟记录一次结果
        segment_duration = 300  # 5分钟
        segments = duration // segment_duration
        results = {}
        
        for segment in range(segments):
            print(f"\n--- 第 {segment + 1}/{segments} 段测试 ---")
            segment_start = segment * segment_duration
            
            # 在持续时间内持续发送请求
            requests_per_segment = concurrency * (segment_duration // 10)  # 假设平均10秒/请求
            
            stats = await self.tester.test_concurrent(
                concurrency=concurrency,
                total_requests=requests_per_segment,
                verbose=False
            )
            
            self.tester.print_statistics(stats)
            results[f"segment_{segment + 1}"] = {
                "time_range": f"{segment_start}-{segment_start + segment_duration}秒",
                "stats": stats
            }
            
            # 如果不是最后一段，等待一段时间再继续
            if segment < segments - 1:
                await asyncio.sleep(10)  # 短暂休息
        
        # 分析性能趋势
        avg_durations = [
            seg["stats"]["duration"]["avg"]
            for seg in results.values()
        ]
        
        if len(avg_durations) > 1:
            first_avg = avg_durations[0]
            last_avg = avg_durations[-1]
            performance_degradation = ((last_avg - first_avg) / first_avg) * 100
            
            print(f"\n性能趋势分析:")
            print(f"  初始平均响应时间: {first_avg:.2f}秒")
            print(f"  最终平均响应时间: {last_avg:.2f}秒")
            print(f"  性能变化: {performance_degradation:+.2f}%")
            
            if performance_degradation > 20:
                print(f"  ⚠️  警告: 检测到明显的性能衰减！")
        
        final_results = {
            "concurrency": concurrency,
            "duration": duration,
            "segments": results,
            "performance_trend": {
                "initial_avg": avg_durations[0] if avg_durations else 0,
                "final_avg": avg_durations[-1] if avg_durations else 0,
                "degradation_percent": performance_degradation if len(avg_durations) > 1 else 0
            }
        }
        
        self.all_results["stability"] = final_results
        self.save_result("stability", final_results)
        return final_results
    
    async def run_all_scenarios(self):
        """运行所有测试场景"""
        print("\n" + "="*60)
        print("开始执行所有测试场景")
        print("="*60)
        
        scenarios = [
            ("基础并发测试", self.scenario_basic_concurrent),
            ("阶梯压力测试", self.scenario_ramp_up),
            ("突发流量测试", self.scenario_burst_traffic),
            ("稳定性测试", self.scenario_stability),
        ]
        
        for name, scenario_func in scenarios:
            try:
                print(f"\n\n{'#'*60}")
                print(f"执行: {name}")
                print(f"{'#'*60}")
                await scenario_func()
            except Exception as e:
                print(f"❌ 场景 '{name}' 执行失败: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # 保存汇总结果
        summary = {
            "timestamp": datetime.now().isoformat(),
            "all_results": self.all_results
        }
        summary_file = self.results_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 所有测试完成！汇总结果已保存到: {summary_file}")


async def main():
    """主函数 - 可以选择运行特定场景或所有场景"""
    import sys
    
    scenarios = TestScenarios()
    
    if len(sys.argv) > 1:
        scenario_name = sys.argv[1]
        if scenario_name == "basic":
            await scenarios.scenario_basic_concurrent()
        elif scenario_name == "ramp":
            await scenarios.scenario_ramp_up()
        elif scenario_name == "burst":
            await scenarios.scenario_burst_traffic()
        elif scenario_name == "stability":
            await scenarios.scenario_stability()
        else:
            print(f"未知场景: {scenario_name}")
            print("可用场景: basic, ramp, burst, stability, all")
    else:
        # 默认运行所有场景
        await scenarios.run_all_scenarios()


if __name__ == "__main__":
    asyncio.run(main())

