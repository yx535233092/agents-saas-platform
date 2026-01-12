"""
测试报告生成器
生成详细的测试报告，包括统计图表
"""
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from config import TEST_CONFIG


class ReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, results_dir: Path = None):
        self.results_dir = results_dir or TEST_CONFIG["results_dir"]
        self.reports_dir = self.results_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def load_result_file(self, filepath: Path) -> Dict[str, Any]:
        """加载结果文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_text_report(self, result_data: Dict[str, Any]) -> str:
        """生成文本报告"""
        scenario = result_data.get("scenario", "unknown")
        timestamp = result_data.get("timestamp", "")
        result = result_data.get("result", {})
        
        report_lines = [
            "=" * 80,
            f"测试报告: {scenario}",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"测试时间: {timestamp}",
            "=" * 80,
            ""
        ]
        
        if scenario == "basic_concurrent":
            report_lines.extend(self._format_basic_concurrent(result))
        elif scenario == "ramp_up":
            report_lines.extend(self._format_ramp_up(result))
        elif scenario == "burst_traffic":
            report_lines.extend(self._format_burst_traffic(result))
        elif scenario == "stability":
            report_lines.extend(self._format_stability(result))
        else:
            report_lines.append(json.dumps(result, indent=2, ensure_ascii=False))
        
        return "\n".join(report_lines)
    
    def _format_basic_concurrent(self, result: Dict[str, Any]) -> List[str]:
        """格式化基础并发测试结果"""
        lines = ["基础并发测试结果", "-" * 80, ""]
        
        for key, stats in sorted(result.items(), key=lambda x: int(x[0].split('_')[1])):
            concurrency = key.split('_')[1]
            lines.extend([
                f"并发数: {concurrency}",
                f"  总请求数: {stats['total_requests']}",
                f"  成功: {stats['successful']} ({stats['success_rate']:.2f}%)",
                f"  失败: {stats['failed']}",
                f"  QPS: {stats['qps']:.2f}",
                f"  平均响应时间: {stats['duration']['avg']:.2f}秒",
                f"  P95响应时间: {stats['duration']['p95']:.2f}秒",
                f"  P99响应时间: {stats['duration']['p99']:.2f}秒",
                ""
            ])
        
        return lines
    
    def _format_ramp_up(self, result: Dict[str, Any]) -> List[str]:
        """格式化阶梯压力测试结果"""
        lines = ["阶梯压力测试结果", "-" * 80, ""]
        
        for key, stats in sorted(result.items(), key=lambda x: int(x[0].split('_')[1])):
            concurrency = key.split('_')[1]
            lines.extend([
                f"并发数: {concurrency}",
                f"  成功率: {stats['success_rate']:.2f}%",
                f"  QPS: {stats['qps']:.2f}",
                f"  平均响应时间: {stats['duration']['avg']:.2f}秒",
                ""
            ])
        
        return lines
    
    def _format_burst_traffic(self, result: Dict[str, Any]) -> List[str]:
        """格式化突发流量测试结果"""
        stats = result.get("stats", {})
        lines = [
            "突发流量测试结果",
            "-" * 80,
            f"并发数: {result.get('concurrency', 'N/A')}",
            f"持续时间: {result.get('duration', 'N/A')}秒",
            f"总请求数: {result.get('total_requests', 'N/A')}",
            "",
            "性能指标:",
            f"  成功: {stats.get('successful', 0)} ({stats.get('success_rate', 0):.2f}%)",
            f"  失败: {stats.get('failed', 0)}",
            f"  QPS: {stats.get('qps', 0):.2f}",
            f"  平均响应时间: {stats['duration']['avg']:.2f}秒" if 'duration' in stats else "",
            f"  P95响应时间: {stats['duration']['p95']:.2f}秒" if 'duration' in stats else "",
            ""
        ]
        return [line for line in lines if line]
    
    def _format_stability(self, result: Dict[str, Any]) -> List[str]:
        """格式化稳定性测试结果"""
        lines = [
            "稳定性测试结果",
            "-" * 80,
            f"并发数: {result.get('concurrency', 'N/A')}",
            f"持续时间: {result.get('duration', 'N/A')}秒",
            "",
            "分段测试结果:",
            ""
        ]
        
        for segment_key, segment_data in result.get("segments", {}).items():
            segment_num = segment_key.split('_')[1]
            stats = segment_data.get("stats", {})
            lines.extend([
                f"  第 {segment_num} 段 ({segment_data.get('time_range', 'N/A')}):",
                f"    成功率: {stats.get('success_rate', 0):.2f}%",
                f"    平均响应时间: {stats['duration']['avg']:.2f}秒" if 'duration' in stats else "",
                ""
            ])
        
        trend = result.get("performance_trend", {})
        if trend:
            lines.extend([
                "性能趋势:",
                f"  初始平均响应时间: {trend.get('initial_avg', 0):.2f}秒",
                f"  最终平均响应时间: {trend.get('final_avg', 0):.2f}秒",
                f"  性能变化: {trend.get('degradation_percent', 0):+.2f}%",
                ""
            ])
        
        return lines
    
    def generate_csv_report(self, result_data: Dict[str, Any], output_file: Path):
        """生成 CSV 报告"""
        scenario = result_data.get("scenario", "unknown")
        result = result_data.get("result", {})
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            if scenario == "basic_concurrent":
                writer.writerow([
                    "并发数", "总请求数", "成功数", "失败数", "成功率(%)",
                    "QPS", "平均响应时间(秒)", "P50(秒)", "P95(秒)", "P99(秒)"
                ])
                
                for key, stats in sorted(result.items(), key=lambda x: int(x[0].split('_')[1])):
                    concurrency = key.split('_')[1]
                    writer.writerow([
                        concurrency,
                        stats['total_requests'],
                        stats['successful'],
                        stats['failed'],
                        f"{stats['success_rate']:.2f}",
                        f"{stats['qps']:.2f}",
                        f"{stats['duration']['avg']:.2f}",
                        f"{stats['duration']['p50']:.2f}",
                        f"{stats['duration']['p95']:.2f}",
                        f"{stats['duration']['p99']:.2f}",
                    ])
    
    def generate_all_reports(self):
        """为所有结果文件生成报告"""
        result_files = list(self.results_dir.glob("*.json"))
        summary_files = [f for f in result_files if f.name.startswith("summary_")]
        result_files = [f for f in result_files if not f.name.startswith("summary_")]
        
        print(f"找到 {len(result_files)} 个结果文件")
        
        for result_file in result_files:
            try:
                result_data = self.load_result_file(result_file)
                
                # 生成文本报告
                text_report = self.generate_text_report(result_data)
                report_file = self.reports_dir / f"{result_file.stem}.txt"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(text_report)
                print(f"✅ 文本报告: {report_file}")
                
                # 生成 CSV 报告（仅基础并发测试）
                if result_data.get("scenario") == "basic_concurrent":
                    csv_file = self.reports_dir / f"{result_file.stem}.csv"
                    self.generate_csv_report(result_data, csv_file)
                    print(f"✅ CSV报告: {csv_file}")
            
            except Exception as e:
                print(f"❌ 处理文件 {result_file} 时出错: {str(e)}")
        
        print(f"\n所有报告已生成到: {self.reports_dir}")


if __name__ == "__main__":
    generator = ReportGenerator()
    generator.generate_all_reports()

