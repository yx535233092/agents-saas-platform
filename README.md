# 🛡️ Agents SaaS Platform

> 基于多智能体协同的 AI 文档涉密审核平台

一个现代化的 SaaS 平台，利用多个 AI 智能体协同工作，对文档内容进行多维度涉密审核与风险评估.

## ✨ 核心特性

- **多智能体协同审核** - 采用关键词匹配、语义分析、非涉密证明三重智能体并行分析
- **实时流式输出** - SSE 流式传输，实时展示审核过程与分析结果
- **可视化审核流程** - 清晰展示每个智能体的分析进度与置信度
- **用户权限管理** - 完整的用户、角色、权限管理后台
- **JWT 身份认证** - 安全的 Token 认证机制
- **Docker 一键部署** - 支持容器化快速部署

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                       │
│                   React 19 + TypeScript + Vite                │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/SSE
┌──────────────────────────▼──────────────────────────────────┐
│                     Backend (Django REST)                     │
│              Django + DRF + JWT + LangChain                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    AI Agents Pipeline                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐     │
│  │  关键词匹配  │  │  语义分析   │  │  非涉密证明     │     │
│  │   Agent     │  │   Agent     │  │    Agent         │     │
│  │  (40%权重)  │  │  (30%权重)  │  │   (30%权重)     │     │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘     │
│         └────────────────┼──────────────────┘               │
│                          ▼                                   │
│               ┌─────────────────────┐                        │
│               │   决策评审 Agent     │                        │
│               │  (综合加权判定)      │                        │
│               └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## 🤖 智能体说明

| 智能体         | 权重 | 功能描述                                   |
| -------------- | ---- | ------------------------------------------ |
| **关键词匹配** | 40%  | 基于敏感关键词库进行正则匹配与语义关联检测 |
| **语义分析**   | 30%  | 深度语义推断，识别隐晦涉密信息与敏感上下文 |
| **非涉密证明** | 30%  | 反向验证，评估文档公开性特征与风险点       |
| **决策评审**   | -    | 综合三个智能体结果，加权计算最终涉密判定   |

## 🛠️ 技术栈

### 前端 (agents-web)

- **框架**: React 19 + TypeScript
- **构建工具**: Vite 7
- **UI 组件**: Radix UI + TailwindCSS 4
- **状态管理**: Zustand
- **路由**: React Router 7
- **HTTP 客户端**: Axios
- **Markdown 渲染**: react-markdown

### 后端 (agents-backend)

- **框架**: Django 5 + Django REST Framework
- **认证**: djangorestframework-simplejwt
- **跨域**: django-cors-headers
- **AI/LLM**: LangChain + langchain-openai

### AI 服务 (agents-langraph)

- **LLM 接口**: SiliconFlow API
- **模型**: 可配置 (默认 gpt-3.5-turbo)

## 📁 项目结构

```
agents-saas-platform/
├── agents-web/              # 前端项目
│   ├── src/
│   │   ├── components/      # 通用组件
│   │   ├── layouts/         # 布局组件 (主页/后台/登录)
│   │   ├── pages/           # 页面组件
│   │   ├── services/        # API 服务
│   │   ├── stores/          # 状态管理
│   │   ├── types/           # TypeScript 类型
│   │   └── router/          # 路由配置
│   └── Dockerfile
│
├── agents-backend/          # 后端项目
│   ├── api/                 # API 应用
│   │   ├── models.py        # 数据模型
│   │   ├── views.py         # 视图 & 智能体API
│   │   ├── serializers.py   # 序列化器
│   │   └── agents_logic.py  # 智能体逻辑
│   ├── backend/             # Django 配置
│   └── Dockerfile
│
├── agents-langraph/         # AI 智能体模块
│   ├── agents.py            # 智能体定义
│   ├── nodes.py             # 节点定义
│   ├── serve.py             # API 服务
│   └── static/              # 敏感词库
│       └── keywords.json
│
├── docker/
│   └── docker-compose.yml   # Docker 编排
│
└── db/                      # 测试数据库
```

## 🚀 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose (可选)

### 方式一：Docker 部署 (推荐)

```bash
# 1. 克隆项目
git clone <repository-url>
cd agents-saas-platform

# 2. 配置环境变量
# 编辑 docker/docker-compose.yml 中的 SILICONFLOW_API_KEY

# 3. 启动服务
cd docker
docker-compose up -d

# 访问
# 前端: http://localhost
# 后端: http://localhost:8000
```

### 方式二：本地开发

#### 启动后端

```bash
cd agents-backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cat > .env << EOF
DEBUG=True
MODEL=gpt-3.5-turbo
SILICONFLOW_API_KEY=your_api_key_here
EOF

# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动服务
python manage.py runserver
```

#### 启动前端

```bash
cd agents-web

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

## 📡 API 接口

### 认证接口

| 方法 | 路径                  | 描述             |
| ---- | --------------------- | ---------------- |
| POST | `/api/token/`         | 获取 JWT Token   |
| POST | `/api/token/refresh/` | 刷新 Token       |
| GET  | `/api/me/`            | 获取当前用户信息 |

### 业务接口

| 方法 | 路径                | 描述                    |
| ---- | ------------------- | ----------------------- |
| POST | `/api/agent/check/` | 文档涉密审核 (SSE 流式) |
| GET  | `/api/users/`       | 用户列表                |
| GET  | `/api/roles/`       | 角色列表                |
| GET  | `/api/permissions/` | 权限列表                |

### 文档审核请求示例

```bash
curl -X POST http://localhost:8000/api/agent/check/ \
  -H "Content-Type: application/json" \
  -d '{
    "doc_title": "测试文档",
    "doc_content": "待审核的文档内容..."
  }'
```

## 🔧 环境变量

| 变量名                | 描述                 | 默认值          |
| --------------------- | -------------------- | --------------- |
| `DEBUG`               | 调试模式             | `True`          |
| `MODEL`               | LLM 模型名称         | `gpt-3.5-turbo` |
| `SILICONFLOW_API_KEY` | SiliconFlow API 密钥 | -               |
| `ALLOWED_HOSTS`       | Django 允许的主机    | `*`             |

## 📄 页面路由

| 路径               | 描述           |
| ------------------ | -------------- |
| `/`                | 首页 Landing   |
| `/chat-square`     | 文档审核对话页 |
| `/apps/:id`        | 应用对话页     |
| `/login`           | 登录页         |
| `/admin/dashboard` | 管理后台首页   |
| `/admin/users`     | 用户管理       |
| `/admin/roles`     | 角色管理       |

## 🧪 测试

```bash
# 后端测试
cd agents-backend
python manage.py test

# 前端测试
cd agents-web
npm run lint
```

## 📦 构建部署

```bash
# 前端构建
cd agents-web
npm run build

# Docker 构建
cd docker
docker-compose build
docker-compose up -d
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📝 License

MIT License

---

<p align="center">
  Made with ❤️ by H3C Team
</p>
