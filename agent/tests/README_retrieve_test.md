# 测试 retrieve_secret_menu 节点

## 快速开始

### 方法1: 直接运行测试脚本

```bash
cd agent
python tests/test_retrieve_secret_menu.py
```

### 方法2: 使用 Python 交互式环境

```python
# 进入 agent 目录
cd agent

# 启动 Python
python

# 在 Python 中执行
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from confidential_judgement_agent.workflow.nodes import retrieve_secret_menu
from confidential_judgement_agent.workflow.state import State

# 准备测试数据
test_state: State = {
    "current_node": "retrieve_secret_menu",
    "doc_title": "测试文档",
    "doc_content": "涉及消防救援体制机制改革等重大事项的方针政策、工作部署",
    "scene": "测试场景",
}

# 运行测试
result = retrieve_secret_menu(test_state)

# 查看结果
print(result)
```

### 方法3: 使用 pytest（如果已安装）

```bash
cd agent
pytest tests/test_retrieve_secret_menu.py -v
```

## 环境变量配置

确保在 `.env` 文件中配置了以下变量：

```env
RETRIEVAL_API_URL=http://119.45.162.155/v1/chunk/retrieval_test
RETRIEVAL_AUTHORIZATION=IjQwZGQxNGY4ZTIyODExZjBiZDRlNTJlMzU3YWYyN2E0Ig.aU4yCA.AsCQmLk33K1PQFLb2XoF_Z9cobk
RETRIEVAL_KB_ID=08a864acf29f11f0bd4e52e357af27a4
RETRIEVAL_SEARCH_ID=7c760ac2f2a111f0bd4e52e357af27a4
RETRIEVAL_PAGE_SIZE=50
```

## 测试内容

测试脚本包含以下测试用例：

1. **正常情况测试**: 使用有效的文档内容进行检索
2. **空内容测试**: 测试空文档内容的错误处理

## 预期输出

成功时，应该看到：
- `retrieval_result.success = True`
- `retrieval_result.code = 0`
- `retrieval_result.chunks_count > 0`
- `retrieval_result.chunk_summary` 包含检索到的内容摘要

失败时，应该看到：
- `retrieval_result.success = False`
- `retrieval_result.error` 包含错误信息

