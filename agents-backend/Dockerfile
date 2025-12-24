# ==================== Django Backend Dockerfile ====================
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 添加 gunicorn 用于生产环境
RUN pip install --no-cache-dir gunicorn

# 复制项目代码
COPY . .

# 收集静态文件（如果有的话）
# RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 启动命令
# 开发环境使用 runserver
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# 生产环境使用 gunicorn（取消注释下面这行，注释上面那行）
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "backend.wsgi:application"]
