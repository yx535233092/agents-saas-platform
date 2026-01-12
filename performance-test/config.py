"""
并发测试配置文件
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 测试配置
TEST_CONFIG = {
    # 接口配置
    # 注意：前端使用的是 /agent/stream (FastAPI/LangServe)，而不是 /check (Flask)
    "api_url": os.getenv("API_URL", "http://localhost:5001/agent/stream"),
    "timeout": int(os.getenv("TIMEOUT", "300")),  # 5分钟超时
    "use_langserve": True,  # 是否使用 LangServe 格式（/agent/stream）
    # 测试数据配置
    "test_db_path": PROJECT_ROOT / "db" / "test.db",
    # 并发测试配置
    "concurrency_levels": [10, 20, 50, 100, 200],  # 测试的并发级别
    "requests_per_level": 100,  # 每个并发级别发送的请求总数
    # 阶梯压力测试配置
    "ramp_up": {
        "start_concurrency": 10,
        "max_concurrency": 200,
        "step": 10,  # 每次增加的并发数
        "step_interval": 30,  # 每步间隔（秒）
    },
    # 突发流量测试配置
    "burst_test": {
        "concurrency": 100,
        "duration": 60,  # 持续时间（秒）
    },
    # 稳定性测试配置
    "stability_test": {
        "concurrency": 50,
        "duration": 1800,  # 30分钟
    },
    # 结果输出配置
    "results_dir": PROJECT_ROOT / "performance-test" / "results",
    "logs_dir": PROJECT_ROOT / "performance-test" / "logs",
}

# 确保结果目录存在
TEST_CONFIG["results_dir"].mkdir(parents=True, exist_ok=True)
TEST_CONFIG["logs_dir"].mkdir(parents=True, exist_ok=True)
