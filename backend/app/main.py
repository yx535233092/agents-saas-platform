"""
FastAPI主应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import applications

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="应用管理API", description="智能体SaaS平台应用管理接口", version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（路径已在router中定义，不需要额外前缀）
app.include_router(applications.router)


@app.get("/")
def root():
    """
    根路径
    """
    return {"message": "应用管理API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health_check():
    """
    健康检查
    """
    return {"status": "ok"}
