FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（如果需要）
# RUN apt-get update && apt-get install -y --no-install-recommends ...

# 复制依赖文件
COPY agents-backend/requirements.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY agents-backend/ ./agents-backend/
# 复制 LangGraph 代码（包含 keywords.json）
COPY lang-graph/ ./lang-graph/

# 设置工作目录为 agents-backend，以便 manage.py 能正常运行
WORKDIR /app/agents-backend

# 暴露端口
EXPOSE 8000

# 启动命令 (开发模式用 runserver，生产建议 gunicorn)
# 这里使用 0.0.0.0:8000 让外部可以访问
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

