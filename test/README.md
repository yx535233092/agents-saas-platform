# 涉密研判接口并发性能测试方案

## 📋 目录结构

```
performance-test/
├── config.py              # 测试配置文件
├── test_data.py          # 测试数据加载器
├── concurrent_test.py     # 并发测试核心脚本
├── test_scenarios.py      # 测试场景脚本
├── report_generator.py    # 报告生成器
├── requirements.txt       # 依赖包
├── README.md             # 说明文档
├── results/              # 测试结果目录
│   ├── reports/          # 生成的报告
│   └── *.json           # 原始测试结果
└── logs/                 # 日志目录
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd performance-test
pip install -r requirements.txt
```

### 2. 配置测试参数

编辑 `config.py` 文件，修改以下配置：

```python
TEST_CONFIG = {
    "api_url": "http://localhost:5001/agent/stream",  # 接口地址
    "timeout": 300,  # 超时时间（秒）
    "use_langserve": True,  # 使用 LangServe 格式（/agent/stream）
    "concurrency_levels": [10, 20, 50, 100, 200],  # 测试的并发级别
    # ... 其他配置
}
```

**重要提示**：
- 默认使用 `/agent/stream` 端点（FastAPI/LangServe），这是前端实际使用的接口
- 如果使用 Flask 的 `/check` 端点，需要设置 `use_langserve: False` 并修改 `api_url` 为 `http://localhost:5001/check`

### 3. 验证接口连接（推荐先执行）

在运行测试前，先验证接口是否可用：

```bash
python verify_connection.py
```

这会测试接口连接、请求格式是否正确，并显示响应示例。

### 4. 运行测试

#### 方式1: 运行单个场景

```bash
# 基础并发测试
python test_scenarios.py basic

# 阶梯压力测试
python test_scenarios.py ramp

# 突发流量测试
python test_scenarios.py burst

# 稳定性测试
python test_scenarios.py stability
```

#### 方式2: 运行所有场景

```bash
python test_scenarios.py all
```

#### 方式3: 快速测试（少量请求）

```bash
python concurrent_test.py
```

## 📊 测试场景说明

### 场景1: 基础并发测试

测试不同并发级别下的性能表现：
- 并发数：10, 20, 50, 100, 200
- 每个级别发送 100 个请求
- 记录响应时间、QPS、成功率等指标

**目的**：找到系统的性能拐点和最大并发能力

### 场景2: 阶梯式压力测试

逐步增加并发数，观察系统性能变化：
- 从 10 并发开始
- 每 30 秒增加 10 个并发
- 最高到 200 并发

**目的**：模拟真实场景中逐步增加的负载

### 场景3: 突发流量测试

瞬间启动大量并发请求：
- 并发数：100
- 持续时间：60 秒

**目的**：测试系统应对突发流量的能力

### 场景4: 长时间稳定性测试

持续运行一段时间：
- 并发数：50
- 持续时间：30 分钟

**目的**：检查内存泄漏、性能衰减等问题

## 📈 查看测试结果

### 1. 生成报告

```bash
python report_generator.py
```

### 2. 查看报告

报告会生成在 `results/reports/` 目录下：
- `*.txt` - 文本报告
- `*.csv` - CSV 格式（基础并发测试）

### 3. 结果文件说明

原始结果保存在 `results/` 目录下，JSON 格式：
- `basic_concurrent_*.json` - 基础并发测试结果
- `ramp_up_*.json` - 阶梯压力测试结果
- `burst_traffic_*.json` - 突发流量测试结果
- `stability_*.json` - 稳定性测试结果
- `summary_*.json` - 所有测试的汇总结果

## 📊 关键性能指标

测试会记录以下指标：

### 响应时间指标
- **最小响应时间**: 最快的请求耗时
- **最大响应时间**: 最慢的请求耗时
- **平均响应时间**: 所有请求的平均耗时
- **P50**: 50% 的请求在这个时间内完成
- **P95**: 95% 的请求在这个时间内完成
- **P99**: 99% 的请求在这个时间内完成

### 吞吐量指标
- **QPS**: 每秒完成的请求数
- **成功率**: 成功请求占总请求的百分比

### 首字节时间 (TTFB)
- 从发送请求到收到第一个字节的时间

## 🔧 自定义测试

### 修改测试数据

测试数据从 `db/test.db` 数据库加载，包含多个测试文档。

### 自定义测试场景

编辑 `test_scenarios.py`，添加新的测试场景：

```python
async def scenario_custom(self):
    """自定义测试场景"""
    stats = await self.tester.test_concurrent(
        concurrency=30,
        total_requests=100,
        verbose=True
    )
    self.tester.print_statistics(stats)
```

## ⚠️ 注意事项

1. **API 限流**: 注意 LLM API 的速率限制，可能需要多个 API Key
2. **测试环境**: 建议在独立环境测试，避免影响开发环境
3. **资源消耗**: 并发测试会消耗大量 CPU、内存和网络资源
4. **测试数据**: 确保测试数据不包含真实敏感信息
5. **成本控制**: LLM API 调用会产生费用，注意控制测试规模

## 🐛 故障排查

### 问题1: 连接被拒绝

```
错误: Connection refused
解决: 检查服务是否启动，端口是否正确
```

### 问题2: 请求超时

```
错误: Request timeout
解决: 增加 config.py 中的 timeout 值
```

### 问题3: 测试数据加载失败

```
错误: 测试数据库不存在
解决: 运行 db/create_testdb.py 创建测试数据
```

## 📝 测试报告示例

```
================================================================================
测试报告: basic_concurrent
生成时间: 2024-01-15 14:30:00
测试时间: 20240115_143000
================================================================================

基础并发测试结果
--------------------------------------------------------------------------------

并发数: 10
  总请求数: 100
  成功: 100 (100.00%)
  失败: 0
  QPS: 10.50
  平均响应时间: 9.52秒
  P95响应时间: 12.30秒
  P99响应时间: 15.20秒
...
```

## 🔗 相关文件

- 接口实现: `agents-langgraph/app.py`
- 测试数据: `db/create_testdb.py`
- 配置文件: `agents-langgraph/.env`

## 📞 支持

如有问题，请查看：
1. 测试日志: `logs/` 目录
2. 错误信息: 测试输出中的错误详情
3. 配置文件: `config.py` 中的配置项

