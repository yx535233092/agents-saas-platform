# 项目结构说明

## 目录结构

```
confidential-judgement-agent/
├── confidential_judgement_agent/    # 主包目录
│   ├── __init__.py                  # 包初始化文件
│   ├── api/                         # API 模块
│   │   ├── __init__.py
│   │   ├── sse_api.py              # SSE 流式 API 服务
│   │   └── serve.py                # LangServe API 服务
│   ├── config/                      # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py             # 配置管理（环境变量、路径等）
│   ├── workflow/                    # 工作流模块
│   │   ├── __init__.py
│   │   ├── nodes.py                # 工作流节点定义
│   │   └── graph.py                # 工作流图定义和编译
│   └── utils/                       # 工具函数模块
│       ├── __init__.py
│       ├── output.py               # 输出格式化工具
│       ├── secret_menu_parse.py    # 秘密目录解析工具
│       ├── public_judgement.py      # 公开性判别工具
│       └── format_to_json.py       # JSON 格式化工具
├── tests/                           # 测试目录
│   ├── __init__.py
│   └── test_userinput.py           # 用户输入测试脚本
├── static/                          # 静态配置文件
│   ├── keywords.json               # 关键词配置
│   ├── secret_menu.json            # 秘密目录配置
│   └── short_sentence.json         # 短句配置
├── main.py                          # 应用入口文件
├── requirements.txt                 # Python 依赖
├── Dockerfile                       # Docker 构建配置
├── env.example                      # 环境变量示例
├── README.md                        # 项目说明文档
└── .gitignore                       # Git 忽略配置
```

## 模块说明

### confidential_judgement_agent/
主包目录，包含所有核心业务逻辑。

#### api/
API 服务模块，提供两种 API 接口：
- **sse_api.py**: SSE (Server-Sent Events) 流式 API，支持实时流式响应
- **serve.py**: LangServe API，标准的 LangGraph 工作流 API

#### config/
配置管理模块：
- **settings.py**: 统一管理所有配置项，包括：
  - LLM 配置（模型、API Key、Base URL 等）
  - API 配置（主机、端口）
  - CORS 配置
  - 日志配置
  - 静态文件路径

#### workflow/
工作流模块：
- **nodes.py**: 定义所有工作流节点函数
  - `start_node`: 开始节点（数据清洗）
  - `judgement_secretlogo_node`: 秘标识别节点
  - `judgement_scene_node`: 场景识别节点
  - `judgement_secret_directory_node`: 秘密目录判别节点
  - `judgement_public_content_node`: 内容公开判别节点
  - `secret_analysis_node`: 正向涉密分析节点
  - `public_analysis_node`: 反向非涉密分析节点
  - `decision_review_node`: 决策评审节点
- **graph.py**: 定义工作流图结构，连接各个节点

#### utils/
工具函数模块：
- **output.py**: 控制台输出格式化
- **secret_menu_parse.py**: 秘密目录 LLM 判别
- **public_judgement.py**: 公开性判别
- **format_to_json.py**: JSON 格式化工具

### tests/
测试目录，包含测试脚本和测试用例。

### static/
静态配置文件目录，存放 JSON 格式的配置文件。

## 使用方式

### 开发环境
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制 env.example 为 .env 并修改）
cp env.example .env

# 运行 SSE API
python main.py sse

# 运行 LangServe API
python main.py serve
```

### Docker 部署
```bash
# 构建镜像
docker build -t confidential-judgement-agent .

# 运行容器
docker run -p 5001:5001 \
  -e SILICONFLOW_API_KEY=your_key \
  confidential-judgement-agent
```

## 代码组织原则

1. **模块化**: 按功能划分模块，每个模块职责单一
2. **配置集中**: 所有配置统一在 `config/settings.py` 管理
3. **依赖注入**: 通过配置模块获取配置，避免硬编码
4. **清晰分层**: API 层、工作流层、工具层分离
5. **易于扩展**: 新节点和工具函数可以轻松添加

## 扩展指南

### 添加新节点
1. 在 `workflow/nodes.py` 中定义节点函数
2. 在 `workflow/graph.py` 中注册节点和边

### 添加新工具函数
1. 在 `utils/` 目录下创建新的工具文件
2. 在 `utils/__init__.py` 中导出

### 添加新 API 端点
1. 在 `api/` 目录下创建新的 API 文件
2. 在 `main.py` 中添加新的运行模式（如需要）

