"""
聊天历史记录模型
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class ChatHistory(Base):
    """
    聊天历史记录模型
    """

    __tablename__ = "chat_histories"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(
        Integer, ForeignKey("applications.id"), nullable=False, index=True, comment="应用ID"
    )
    title = Column(String(200), nullable=True, comment="对话标题（自动生成）")
    messages = Column(JSON, nullable=False, comment="消息列表（JSON格式）")
    user_input = Column(Text, nullable=True, comment="用户输入（用于生成标题）")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
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
        return f"<ChatHistory(id={self.id}, application_id={self.application_id}, title='{self.title}')>"

