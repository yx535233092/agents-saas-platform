# 涉密研判智能体

基于 LangGraph 的涉密文档研判智能体系统，支持流式处理和多种 API 接口。

## 项目结构

```
confidential-judgement-agent/
├── confidential_judgement_agent/    # 主包目录
│   ├── __init__.py
│   ├── api/                         # API 模块
│   │   ├── __init__.py
│   │   ├── sse_api.py              # SSE 流式 API
│   │   └── serve.py                # LangServe API
│   ├── config/                      # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py             # 配置管理
│   ├── workflow/                    # 工作流模块
│   │   ├── __init__.py
│   │   ├── nodes.py                # 节点定义
│   │   └── graph.py                # 工作流图定义
│   └── utils/                       # 工具函数
│       ├── __init__.py
│       ├── output.py
│       ├── secret_menu_parse.py
│       ├── public_judgement.py
│       └── format_to_json.py
├── tests/                           # 测试目录
│   ├── __init__.py
│   └── test_userinput.py
├── static/                          # 静态文件
│   ├── keywords.json
│   ├── secret_menu.json
│   └── short_sentence.json
├── main.py                          # 入口文件
├── requirements.txt                 # 依赖文件
├── Dockerfile                       # Docker 配置
├── env.example                      # 环境变量示例
├── README.md                        # 项目说明
└── PROJECT_STRUCTURE.md             # 项目结构详细说明
```

## 功能特性

- **模块化设计**：清晰的目录结构，便于维护和扩展
- **配置管理**：统一的配置管理，支持环境变量
- **多种 API**：支持 SSE 流式 API 和 LangServe API
- **工作流引擎**：基于 LangGraph 的工作流系统
- **流式处理**：支持实时流式响应

## 安装

1. 克隆项目
```bash
git clone <repository-url>
cd confidential-judgement-agent
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
复制 `env.example` 为 `.env` 并修改配置：
```bash
cp env.example .env
```

编辑 `.env` 文件，设置必要的配置项：
```env
MODEL=deepseek-chat
SILICONFLOW_API_KEY=your_api_key
LLM_BASE_URL=https://api.siliconflow.cn/v1
API_HOST=0.0.0.0
API_PORT=5001
```

## 使用方法

### 运行 SSE API 服务
```bash
python main.py sse
```

### 运行 LangServe API 服务
```bash
python main.py serve
```

### 运行测试
```bash
python -m tests.test_userinput
```

## API 接口

### SSE API

- **POST** `/api/check` - 涉密研判接口（SSE 流式）
- **GET** `/health` - 健康检查

### LangServe API

- **POST** `/agent/invoke` - 工作流调用接口
- **POST** `/agent/stream` - 工作流流式接口

## Docker 部署

```bash
# 构建镜像
docker build -t confidential-judgement-agent .

# 运行容器
docker run -p 5001:5001 \
  -e SILICONFLOW_API_KEY=your_api_key \
  -e MODEL=deepseek-chat \
  confidential-judgement-agent
```

## 开发

### 目录说明

- `confidential_judgement_agent/` - 主包，包含所有核心代码
- `confidential_judgement_agent/api/` - API 接口实现
- `confidential_judgement_agent/workflow/` - 工作流定义和节点
- `confidential_judgement_agent/config/` - 配置管理
- `confidential_judgement_agent/utils/` - 工具函数
- `tests/` - 测试代码
- `static/` - 静态配置文件

### 添加新节点

1. 在 `confidential_judgement_agent/workflow/nodes.py` 中定义节点函数
2. 在 `confidential_judgement_agent/workflow/graph.py` 中注册节点和边

## 许可证

[添加许可证信息]
