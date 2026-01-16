"""
数据库配置相关的Pydantic模型
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class DatabaseConfigBase(BaseModel):
    """数据库配置基础模型"""

    name: str = Field(..., min_length=1, max_length=200, description="配置名称")
    description: Optional[str] = Field(None, description="配置描述")
    db_type: str = Field(
        default="sqlite", description="数据库类型：sqlite/postgresql/mysql/mssql"
    )
    host: Optional[str] = Field(None, max_length=255, description="数据库主机地址")
    port: Optional[int] = Field(None, ge=1, le=65535, description="数据库端口")
    database: Optional[str] = Field(None, max_length=255, description="数据库名称")
    username: Optional[str] = Field(None, max_length=255, description="用户名")
    password: Optional[str] = Field(None, max_length=255, description="密码")
    connection_string: Optional[str] = Field(None, description="连接字符串（完整连接信息）")
    extra_params: Optional[Dict[str, Any]] = Field(None, description="额外参数（JSON格式）")
    is_active: Optional[bool] = Field(default=True, description="是否启用")
    is_default: Optional[bool] = Field(default=False, description="是否默认配置")
    sort_order: Optional[int] = Field(default=0, description="排序")

    @field_validator("db_type")
    @classmethod
    def validate_db_type(cls, v):
        allowed_types = ["sqlite", "postgresql", "mysql", "mssql"]
        if v not in allowed_types:
            raise ValueError(f"db_type必须是以下之一: {', '.join(allowed_types)}")
        return v

    @field_validator("connection_string")
    @classmethod
    def validate_connection_string(cls, v, info):
        """验证连接字符串或单独字段"""
        # 如果提供了连接字符串，则不需要单独字段
        if v:
            return v
        # 如果没有连接字符串，检查是否提供了必要的单独字段
        db_type = info.data.get("db_type", "sqlite")
        if db_type == "sqlite":
            # SQLite 只需要 connection_string 或 database
            return v
        else:
            # 其他数据库类型需要 host, database 等
            host = info.data.get("host")
            database = info.data.get("database")
            if not host or not database:
                # 如果没有提供连接字符串，且缺少必要字段，这里不强制要求
                # 因为可能在更新时只更新部分字段
                pass
        return v


class DatabaseConfigCreate(DatabaseConfigBase):
    """创建数据库配置的请求模型"""

    pass


class DatabaseConfigUpdate(BaseModel):
    """更新数据库配置的请求模型（所有字段可选）"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=200, description="配置名称"
    )
    description: Optional[str] = Field(None, description="配置描述")
    db_type: Optional[str] = Field(None, description="数据库类型")
    host: Optional[str] = Field(None, max_length=255, description="数据库主机地址")
    port: Optional[int] = Field(None, ge=1, le=65535, description="数据库端口")
    database: Optional[str] = Field(None, max_length=255, description="数据库名称")
    username: Optional[str] = Field(None, max_length=255, description="用户名")
    password: Optional[str] = Field(None, max_length=255, description="密码")
    connection_string: Optional[str] = Field(None, description="连接字符串")
    extra_params: Optional[Dict[str, Any]] = Field(None, description="额外参数")
    is_active: Optional[bool] = Field(None, description="是否启用")
    is_default: Optional[bool] = Field(None, description="是否默认配置")
    sort_order: Optional[int] = Field(None, description="排序")


class DatabaseConfigResponse(DatabaseConfigBase):
    """数据库配置响应模型"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DatabaseTestResponse(BaseModel):
    """数据库连接测试响应模型"""

    success: bool
    message: str
    details: Optional[Dict[str, Any]] = Field(default=None, description="测试详情")

