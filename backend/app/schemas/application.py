"""
应用管理相关的Pydantic模型
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ApplicationBase(BaseModel):
    """应用基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="应用名称")
    description: Optional[str] = Field(None, description="应用描述")
    app_type: str = Field(default="custom", description="应用类型：secret_judgement/custom")
    api_endpoint: str = Field(..., min_length=1, max_length=500, description="API端点地址")
    api_method: str = Field(default="POST", description="HTTP方法：POST/GET/PUT/DELETE")
    request_format: Optional[str] = Field(default="json", description="请求格式")
    response_format: Optional[str] = Field(default="json", description="响应格式")
    headers: Optional[Dict[str, str]] = Field(default=None, description="自定义请求头")
    timeout: Optional[int] = Field(default=300, ge=1, le=3600, description="超时时间（秒）")
    icon: Optional[str] = Field(default="bot", description="图标标识")
    icon_color: Optional[str] = Field(default="text-blue-500", description="图标颜色")
    is_active: Optional[bool] = Field(default=True, description="是否启用")
    sort_order: Optional[int] = Field(default=0, description="排序")

    @field_validator('app_type')
    @classmethod
    def validate_app_type(cls, v):
        if v not in ['secret_judgement', 'custom']:
            raise ValueError('app_type必须是secret_judgement或custom')
        return v

    @field_validator('api_method')
    @classmethod
    def validate_api_method(cls, v):
        if v.upper() not in ['POST', 'GET', 'PUT', 'DELETE']:
            raise ValueError('api_method必须是POST/GET/PUT/DELETE之一')
        return v.upper()


class ApplicationCreate(ApplicationBase):
    """创建应用的请求模型"""
    pass


class ApplicationUpdate(BaseModel):
    """更新应用的请求模型（所有字段可选）"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="应用名称")
    description: Optional[str] = Field(None, description="应用描述")
    app_type: Optional[str] = Field(None, description="应用类型")
    api_endpoint: Optional[str] = Field(None, min_length=1, max_length=500, description="API端点地址")
    api_method: Optional[str] = Field(None, description="HTTP方法")
    request_format: Optional[str] = Field(None, description="请求格式")
    response_format: Optional[str] = Field(None, description="响应格式")
    headers: Optional[Dict[str, str]] = Field(None, description="自定义请求头")
    timeout: Optional[int] = Field(None, ge=1, le=3600, description="超时时间（秒）")
    icon: Optional[str] = Field(None, description="图标标识")
    icon_color: Optional[str] = Field(None, description="图标颜色")
    is_active: Optional[bool] = Field(None, description="是否启用")
    sort_order: Optional[int] = Field(None, description="排序")


class ApplicationResponse(ApplicationBase):
    """应用响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationTestRequest(BaseModel):
    """测试应用的请求模型"""
    test_data: Optional[Dict[str, Any]] = Field(default=None, description="测试数据")


class ApplicationTestResponse(BaseModel):
    """测试应用的响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = Field(default=None, description="测试响应数据")

