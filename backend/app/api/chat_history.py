"""
聊天历史记录API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.chat_history import ChatHistory
from app.schemas.chat_history import (
    ChatHistoryCreate,
    ChatHistoryUpdate,
    ChatHistoryResponse,
    ChatHistoryListResponse,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backend/chat-history", tags=["chat-history"])


@router.get("/", response_model=List[ChatHistoryListResponse])
def get_chat_histories(
    application_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    获取聊天历史记录列表
    """
    query = db.query(ChatHistory).filter(
        ChatHistory.application_id == application_id
    )

    histories = (
        query.order_by(ChatHistory.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return histories


@router.get("/{history_id}/", response_model=ChatHistoryResponse)
def get_chat_history(history_id: int, db: Session = Depends(get_db)):
    """
    获取单个聊天历史记录详情
    """
    history = (
        db.query(ChatHistory).filter(ChatHistory.id == history_id).first()
    )
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"聊天历史记录ID {history_id} 不存在",
        )
    return history


@router.post(
    "/", response_model=ChatHistoryResponse, status_code=status.HTTP_201_CREATED
)
def create_chat_history(
    history: ChatHistoryCreate, db: Session = Depends(get_db)
):
    """
    创建聊天历史记录
    """
    # 如果没有提供标题，根据用户输入自动生成
    title = history.title
    if not title and history.user_input:
        # 取用户输入的前30个字符作为标题
        title = history.user_input[:30]
        if len(history.user_input) > 30:
            title += "..."

    db_history = ChatHistory(
        application_id=history.application_id,
        title=title,
        messages=history.messages,
        user_input=history.user_input,
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history


@router.patch("/{history_id}/", response_model=ChatHistoryResponse)
def update_chat_history(
    history_id: int, history: ChatHistoryUpdate, db: Session = Depends(get_db)
):
    """
    更新聊天历史记录
    """
    db_history = (
        db.query(ChatHistory).filter(ChatHistory.id == history_id).first()
    )
    if not db_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"聊天历史记录ID {history_id} 不存在",
        )

    update_data = history.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_history, field, value)

    db.commit()
    db.refresh(db_history)
    return db_history


@router.delete("/{history_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_history(history_id: int, db: Session = Depends(get_db)):
    """
    删除聊天历史记录
    """
    db_history = (
        db.query(ChatHistory).filter(ChatHistory.id == history_id).first()
    )
    if not db_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"聊天历史记录ID {history_id} 不存在",
        )

    db.delete(db_history)
    db.commit()
    return None

