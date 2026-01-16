"""
模型配置数据库模型
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class ModelConfig(Base):
    """
    模型配置模型
    """

    __tablename__ = "model_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True, comment="模型名称")
    model_id = Column(String(200), nullable=False, index=True, comment="模型标识")
    description = Column(Text, nullable=True, comment="模型描述")
    provider = Column(
        String(50),
        nullable=False,
        default="siliconflow",
        comment="供应商：openai/anthropic/deepseek/alibaba/siliconflow/other",
    )
    icon = Column(
        String(50),
        nullable=True,
        default="sparkles",
        comment="图标：sparkles/zap/brain/cpu/bot",
    )
    icon_color = Column(
        String(50), nullable=True, default="text-blue-500", comment="图标颜色"
    )
    max_tokens = Column(Integer, nullable=False, default=4096, comment="最大token数")
    api_base_url = Column(String(500), nullable=True, comment="API基础URL")
    api_key = Column(Text, nullable=True, comment="API密钥（加密存储）")
    api_key_env = Column(String(200), nullable=True, comment="API密钥环境变量名")
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
        return f"<ModelConfig(id={self.id}, name='{self.name}', model_id='{self.model_id}')>"

