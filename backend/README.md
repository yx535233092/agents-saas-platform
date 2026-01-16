# 应用管理 API

基于 FastAPI 实现的应用管理接口服务。

## 功能特性

- ✅ 应用的增删改查（CRUD）
- ✅ 应用列表查询（支持分页和过滤）
- ✅ 公开应用列表（仅返回启用中的应用）
- ✅ 应用连接测试功能
- ✅ 支持多种 HTTP 方法和请求格式
- ✅ 完整的请求验证和错误处理
- ✅ 测试数据库连接和批量处理功能

## 安装依赖

```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 运行服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### 应用管理

- `GET /api/applications/` - 获取应用列表
- `GET /api/applications/public/` - 获取公开应用列表
- `GET /api/applications/{id}/` - 获取单个应用详情
- `POST /api/applications/` - 创建新应用
- `PATCH /api/applications/{id}/` - 更新应用
- `DELETE /api/applications/{id}/` - 删除应用
- `POST /api/applications/{id}/test/` - 测试应用连接

### 测试数据库

- `GET /backend/test-db/` - 获取测试数据库中的所有数据（支持分页）
- `GET /backend/test-db/count` - 获取测试数据库中的数据总数
- `GET /backend/test-db/{record_id}` - 根据 ID 获取单条测试数据
- `GET /backend/test-db/connection/test` - 测试数据库连接
- `POST /backend/test-db/batch-process` - 批量处理数据（获取数据列表）

## 数据库

### 应用数据库

默认使用 SQLite 数据库（`applications.db`），可以通过环境变量 `DATABASE_URL` 修改。

例如使用 PostgreSQL：

```bash
export DATABASE_URL="postgresql://user:password@localhost/dbname"
```

### 测试数据库

测试数据库用于存储测试文档数据，默认路径为 `db/test.db`。

可以通过环境变量 `TEST_DB_PATH` 自定义测试数据库路径：

```bash
export TEST_DB_PATH="/path/to/your/test.db"
```

测试数据库应包含一个名为 `test` 的表，包含以下字段：
- `id` (INTEGER PRIMARY KEY)
- `文件名` (TEXT)
- `摘要` (TEXT)
- `全文` (TEXT)
- 其他自定义字段...

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py      # 应用数据库配置
│   │   └── test_db.py       # 测试数据库连接和批量处理工具
│   ├── models/
│   │   ├── __init__.py
│   │   └── application.py   # 应用数据模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── application.py   # Pydantic模型
│   └── api/
│       ├── __init__.py
│       ├── applications.py  # 应用管理路由
│       └── test_db.py        # 测试数据库 API 路由
├── requirements.txt
└── README.md
```
