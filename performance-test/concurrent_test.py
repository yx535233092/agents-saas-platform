"""
并发测试核心脚本
支持 SSE 流式响应的并发测试
"""
import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from config import TEST_CONFIG
from test_data import TestDataLoader


@dataclass
class RequestResult:
    """单个请求的结果"""
    request_id: int
    success: bool
    start_time: float
    end_time: float
    duration: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_size: int = 0
    first_byte_time: Optional[float] = None  # 首字节时间（TTFB）
    final_data: Optional[Dict] = None  # 最终结果数据
    nodes_processed: List[str] = field(default_factory=list)  # 处理的节点列表


class ConcurrentTester:
    """并发测试器"""
    
    def __init__(self, api_url: str = None, timeout: int = None, use_langserve: bool = None):
        self.api_url = api_url or TEST_CONFIG["api_url"]
        self.timeout = timeout or TEST_CONFIG["timeout"]
        self.use_langserve = use_langserve if use_langserve is not None else TEST_CONFIG.get("use_langserve", True)
        self.data_loader = TestDataLoader()
        self.results: List[RequestResult] = []
    
    async def send_request(
        self,
        session: aiohttp.ClientSession,
        request_id: int,
        test_data: Dict,
        verbose: bool = False
    ) -> RequestResult:
        """
        发送单个请求并处理 SSE 流式响应
        
        Args:
            session: aiohttp 会话
            request_id: 请求ID
            test_data: 测试数据（包含 doc_title 和 doc_content）
            verbose: 是否输出详细信息
        
        Returns:
            RequestResult: 请求结果
        """
        start_time = time.time()
        result = RequestResult(
            request_id=request_id,
            success=False,
            start_time=start_time,
            end_time=start_time,
            duration=0.0
        )
        
        try:
            # 根据接口类型选择不同的请求格式
            if self.use_langserve:
                # LangServe 格式 (/agent/stream)
                payload = {
                    "input": {
                        "doc_title": test_data["doc_title"],
                        "doc_content": test_data["doc_content"],
                        "current_node": "start_node",
                        "is_sensitive": False,
                        "scene": "",
                        "evidence": "",
                        "secret_analysis_result": {},
                        "public_analysis_result": {},
                        "confidence": 0
                    }
                }
            else:
                # Flask 格式 (/check)
                payload = {
                    "doc_title": test_data["doc_title"],
                    "doc_content": test_data["doc_content"]
                }
            
            if verbose:
                print(f"[请求 {request_id}] 开始发送 - {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with session.post(
                self.api_url,
                json=payload,
                timeout=timeout
            ) as response:
                result.status_code = response.status
                
                if response.status != 200:
                    error_text = await response.text()
                    result.error_message = f"HTTP {response.status}: {error_text[:200]}"
                    result.end_time = time.time()
                    result.duration = result.end_time - result.start_time
                    return result
                
                # 处理流式响应（SSE 格式）
                first_byte_received = False
                buffer = ""
                nodes_seen = set()
                line_buffer = ""  # 用于处理跨块的行
                
                # 统一处理 SSE 流式响应（LangServe 和 Flask 都使用 SSE）
                async for chunk in response.content.iter_any():
                    if not first_byte_received:
                        result.first_byte_time = time.time() - result.start_time
                        first_byte_received = True
                    
                    chunk_text = chunk.decode('utf-8', errors='ignore')
                    buffer += chunk_text
                    result.response_size += len(chunk_text)
                    
                    # 处理可能跨块的行
                    line_buffer += chunk_text
                    lines = line_buffer.split('\n')
                    # 保留最后一个不完整的行
                    line_buffer = lines[-1]
                    
                    # 处理完整的行
                    for line in lines[:-1]:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # 解析 SSE 格式: data: {...}
                        if line.startswith('data: '):
                            try:
                                data_str = line[6:].strip()
                                if data_str:
                                    data = json.loads(data_str)
                                    if isinstance(data, dict):
                                        # 记录处理的节点
                                        if 'node' in data:
                                            nodes_seen.add(data['node'])
                                        # 记录最终结果
                                        if data.get('type') == 'final':
                                            result.final_data = data.get('data', {})
                            except json.JSONDecodeError:
                                # 尝试解析其他可能的格式
                                pass
                
                result.nodes_processed = list(nodes_seen)
                result.success = True
                result.end_time = time.time()
                result.duration = result.end_time - result.start_time
                
                if verbose:
                    print(f"[请求 {request_id}] 完成 - 耗时: {result.duration:.2f}秒, "
                          f"状态: {response.status}, 节点数: {len(nodes_seen)}")
        
        except asyncio.TimeoutError:
            result.error_message = f"请求超时（>{self.timeout}秒）"
            result.end_time = time.time()
            result.duration = result.end_time - result.start_time
            if verbose:
                print(f"[请求 {request_id}] 超时")
        
        except Exception as e:
            result.error_message = str(e)[:200]
            result.end_time = time.time()
            result.duration = result.end_time - result.start_time
            if verbose:
                print(f"[请求 {request_id}] 错误: {result.error_message}")
        
        return result
    
    async def test_concurrent(
        self,
        concurrency: int,
        total_requests: int = None,
        ramp_up_time: float = 0.0,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        执行并发测试
        
        Args:
            concurrency: 并发数
            total_requests: 总请求数（如果为None，则等于并发数）
            ramp_up_time: 启动时间（秒），0表示快速启动
            verbose: 是否输出详细信息
        
        Returns:
            测试结果统计
        """
        if total_requests is None:
            total_requests = concurrency
        
        print(f"\n{'='*60}")
        print(f"开始并发测试")
        print(f"并发数: {concurrency}")
        print(f"总请求数: {total_requests}")
        print(f"启动时间: {ramp_up_time}秒")
        print(f"{'='*60}\n")
        
        # 加载测试数据
        test_data_list = self.data_loader.load_test_data()
        if not test_data_list:
            raise ValueError("没有可用的测试数据")
        
        # 准备测试数据（循环使用）
        test_data_queue = []
        for i in range(total_requests):
            test_data_queue.append(test_data_list[i % len(test_data_list)])
        
        # 创建 HTTP 会话
        connector = aiohttp.TCPConnector(limit=concurrency * 2)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            # 执行测试
            test_start_time = time.time()
            self.results = []
            
            if ramp_up_time > 0:
                # 阶梯启动
                tasks = []
                batch_size = max(1, concurrency // max(1, int(ramp_up_time)))
                batch_interval = ramp_up_time / max(1, (total_requests // batch_size))
                
                request_idx = 0
                for batch_start in range(0, total_requests, batch_size):
                    batch_end = min(batch_start + batch_size, total_requests)
                    batch_tasks = []
                    
                    for i in range(batch_start, batch_end):
                        test_data = test_data_queue[i]
                        task = self.send_request(session, i + 1, test_data, verbose=False)
                        batch_tasks.append(task)
                    
                    tasks.extend(batch_tasks)
                    
                    if batch_end < total_requests:
                        await asyncio.sleep(batch_interval)
                    
                    if verbose:
                        print(f"已启动 {batch_end}/{total_requests} 个请求")
                
                # 等待所有任务完成
                self.results = await asyncio.gather(*tasks)
            else:
                # 快速启动（尽量同时）
                tasks = []
                for i in range(total_requests):
                    test_data = test_data_queue[i]
                    task = self.send_request(session, i + 1, test_data, verbose=verbose)
                    tasks.append(task)
                
                # 等待所有任务完成
                self.results = await asyncio.gather(*tasks)
            
            test_end_time = time.time()
            total_duration = test_end_time - test_start_time
        
        # 统计结果
        return self._calculate_statistics(total_duration)
    
    def _calculate_statistics(self, total_duration: float) -> Dict[str, Any]:
        """计算测试统计信息"""
        if not self.results:
            return {}
        
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        durations = [r.duration for r in successful]
        ttfb_times = [r.first_byte_time for r in successful if r.first_byte_time is not None]
        
        stats = {
            "total_requests": len(self.results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(self.results) * 100 if self.results else 0,
            "total_duration": total_duration,
            "qps": len(successful) / total_duration if total_duration > 0 else 0,
            "duration": {
                "min": min(durations) if durations else 0,
                "max": max(durations) if durations else 0,
                "avg": sum(durations) / len(durations) if durations else 0,
                "p50": self._percentile(durations, 50) if durations else 0,
                "p95": self._percentile(durations, 95) if durations else 0,
                "p99": self._percentile(durations, 99) if durations else 0,
            },
            "ttfb": {
                "min": min(ttfb_times) if ttfb_times else 0,
                "max": max(ttfb_times) if ttfb_times else 0,
                "avg": sum(ttfb_times) / len(ttfb_times) if ttfb_times else 0,
            },
            "errors": [
                {
                    "request_id": r.request_id,
                    "error": r.error_message,
                    "status_code": r.status_code
                }
                for r in failed
            ],
        }
        
        return stats
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        return sorted_data[index]
    
    def print_statistics(self, stats: Dict[str, Any]):
        """打印统计信息"""
        print(f"\n{'='*60}")
        print(f"测试结果统计")
        print(f"{'='*60}")
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功: {stats['successful']} ({stats['success_rate']:.2f}%)")
        print(f"失败: {stats['failed']}")
        print(f"总耗时: {stats['total_duration']:.2f}秒")
        print(f"QPS: {stats['qps']:.2f}")
        print(f"\n响应时间统计:")
        print(f"  最小: {stats['duration']['min']:.2f}秒")
        print(f"  最大: {stats['duration']['max']:.2f}秒")
        print(f"  平均: {stats['duration']['avg']:.2f}秒")
        print(f"  P50: {stats['duration']['p50']:.2f}秒")
        print(f"  P95: {stats['duration']['p95']:.2f}秒")
        print(f"  P99: {stats['duration']['p99']:.2f}秒")
        
        if stats['ttfb']['avg'] > 0:
            print(f"\n首字节时间 (TTFB):")
            print(f"  最小: {stats['ttfb']['min']:.2f}秒")
            print(f"  最大: {stats['ttfb']['max']:.2f}秒")
            print(f"  平均: {stats['ttfb']['avg']:.2f}秒")
        
        if stats['errors']:
            print(f"\n错误详情 (前10个):")
            for error in stats['errors'][:10]:
                print(f"  请求 {error['request_id']}: {error['error']}")
        
        print(f"{'='*60}\n")


if __name__ == "__main__":
    # 简单测试
    async def main():
        tester = ConcurrentTester()
        stats = await tester.test_concurrent(
            concurrency=5,
            total_requests=10,
            verbose=True
        )
        tester.print_statistics(stats)
    
    asyncio.run(main())

