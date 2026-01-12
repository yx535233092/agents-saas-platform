"""
应用管理数据库模型
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Application(Base):
    """
    应用模型
    """

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True, comment="应用名称")
    description = Column(Text, nullable=True, comment="应用描述")
    app_type = Column(
        String(50),
        nullable=False,
        default="custom",
        comment="应用类型：secret_judgement/custom",
    )
    api_endpoint = Column(String(500), nullable=False, comment="API端点地址")
    api_method = Column(String(10), nullable=False, default="POST", comment="HTTP方法")
    request_format = Column(
        String(50), nullable=True, default="json", comment="请求格式"
    )
    response_format = Column(
        String(50), nullable=True, default="json", comment="响应格式"
    )
    headers = Column(JSON, nullable=True, comment="自定义请求头")
    timeout = Column(Integer, nullable=True, default=300, comment="超时时间（秒）")
    icon = Column(String(50), nullable=True, default="bot", comment="图标标识")
    icon_color = Column(
        String(50), nullable=True, default="text-blue-500", comment="图标颜色"
    )
    is_active = Column(
        Boolean, nullable=False, default=True, index=True, comment="是否启用"
    )
    sort_order = Column(Integer, nullable=False, default=0, index=True, comment="排序")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )

    def __repr__(self):
        return f"<Application(id={self.id}, name='{self.name}', app_type='{self.app_type}')>"
