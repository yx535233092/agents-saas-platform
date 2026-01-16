"""
聊天历史记录相关的Pydantic模型
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ChatHistoryBase(BaseModel):
    """聊天历史记录基础模型"""

    application_id: int = Field(..., description="应用ID")
    title: Optional[str] = Field(None, max_length=200, description="对话标题")
    messages: List[Dict[str, Any]] = Field(..., description="消息列表")
    user_input: Optional[str] = Field(None, description="用户输入")


class ChatHistoryCreate(ChatHistoryBase):
    """创建聊天历史记录的请求模型"""

    pass


class ChatHistoryUpdate(BaseModel):
    """更新聊天历史记录的请求模型"""

    title: Optional[str] = Field(None, max_length=200, description="对话标题")
    messages: Optional[List[Dict[str, Any]]] = Field(None, description="消息列表")


class ChatHistoryResponse(ChatHistoryBase):
    """聊天历史记录响应模型"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryListResponse(BaseModel):
    """聊天历史记录列表响应模型"""

    id: int
    application_id: int
    title: Optional[str]
    user_input: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

