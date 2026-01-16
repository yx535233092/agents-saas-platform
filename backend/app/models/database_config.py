"""
数据库配置模型
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class DatabaseConfig(Base):
    """
    数据库配置模型
    """

    __tablename__ = "database_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True, comment="配置名称")
    description = Column(Text, nullable=True, comment="配置描述")
    db_type = Column(
        String(50),
        nullable=False,
        default="sqlite",
        comment="数据库类型：sqlite/postgresql/mysql/mssql",
    )
    host = Column(String(255), nullable=True, comment="数据库主机地址")
    port = Column(Integer, nullable=True, comment="数据库端口")
    database = Column(String(255), nullable=True, comment="数据库名称")
    username = Column(String(255), nullable=True, comment="用户名")
    password = Column(String(255), nullable=True, comment="密码（加密存储）")
    connection_string = Column(Text, nullable=True, comment="连接字符串（完整连接信息）")
    extra_params = Column(JSON, nullable=True, comment="额外参数（JSON格式）")
    is_active = Column(
        Boolean, nullable=False, default=True, index=True, comment="是否启用"
    )
    is_default = Column(
        Boolean, nullable=False, default=False, index=True, comment="是否默认配置"
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
        return f"<DatabaseConfig(id={self.id}, name='{self.name}', db_type='{self.db_type}')>"

