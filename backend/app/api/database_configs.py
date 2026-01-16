"""
数据库配置管理API路由
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.db_connector import DatabaseConnector
from app.models.database_config import DatabaseConfig
from app.schemas.database_config import (
    DatabaseConfigCreate,
    DatabaseConfigUpdate,
    DatabaseConfigResponse,
    DatabaseTestResponse,
)
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backend/database-configs", tags=["database-configs"])


@router.get("/", response_model=List[DatabaseConfigResponse])
def get_database_configs(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db),
):
    """
    获取数据库配置列表
    """
    query = db.query(DatabaseConfig)

    # 如果指定了is_active，进行过滤
    if is_active is not None:
        query = query.filter(DatabaseConfig.is_active == is_active)

    # 按sort_order和id排序
    configs = (
        query.order_by(DatabaseConfig.sort_order.asc(), DatabaseConfig.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return configs


@router.get("/{config_id}/", response_model=DatabaseConfigResponse)
def get_database_config(config_id: int, db: Session = Depends(get_db)):
    """
    获取单个数据库配置详情
    """
    config = (
        db.query(DatabaseConfig).filter(DatabaseConfig.id == config_id).first()
    )
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"数据库配置ID {config_id} 不存在",
        )
    return config


@router.post(
    "/", response_model=DatabaseConfigResponse, status_code=status.HTTP_201_CREATED
)
def create_database_config(
    config: DatabaseConfigCreate, db: Session = Depends(get_db)
):
    """
    创建新数据库配置
    """
    # 检查名称是否已存在
    existing = (
        db.query(DatabaseConfig)
        .filter(DatabaseConfig.name == config.name)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"配置名称 '{config.name}' 已存在",
        )

    # 如果设置为默认配置，取消其他配置的默认状态
    if config.is_default:
        db.query(DatabaseConfig).update({"is_default": False})

    # 创建配置对象
    db_config = DatabaseConfig(**config.model_dump())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@router.patch("/{config_id}/", response_model=DatabaseConfigResponse)
def update_database_config(
    config_id: int, config: DatabaseConfigUpdate, db: Session = Depends(get_db)
):
    """
    更新数据库配置信息
    """
    db_config = (
        db.query(DatabaseConfig).filter(DatabaseConfig.id == config_id).first()
    )
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"数据库配置ID {config_id} 不存在",
        )

    # 如果更新名称，检查是否与其他配置冲突
    update_data = config.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = (
            db.query(DatabaseConfig)
            .filter(
                DatabaseConfig.name == update_data["name"],
                DatabaseConfig.id != config_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"配置名称 '{update_data['name']}' 已存在",
            )

    # 如果设置为默认配置，取消其他配置的默认状态
    if update_data.get("is_default"):
        db.query(DatabaseConfig).filter(
            DatabaseConfig.id != config_id
        ).update({"is_default": False})

    # 更新字段
    for field, value in update_data.items():
        setattr(db_config, field, value)

    db.commit()
    db.refresh(db_config)
    return db_config


@router.delete("/{config_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_database_config(config_id: int, db: Session = Depends(get_db)):
    """
    删除数据库配置
    """
    db_config = (
        db.query(DatabaseConfig).filter(DatabaseConfig.id == config_id).first()
    )
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"数据库配置ID {config_id} 不存在",
        )

    db.delete(db_config)
    db.commit()
    return None


@router.post("/{config_id}/test/", response_model=DatabaseTestResponse)
def test_database_connection(config_id: int, db: Session = Depends(get_db)):
    """
    测试数据库连接
    """
    db_config = (
        db.query(DatabaseConfig).filter(DatabaseConfig.id == config_id).first()
    )
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"数据库配置ID {config_id} 不存在",
        )

    # 构建配置字典
    config_dict = {
        "db_type": db_config.db_type,
        "host": db_config.host,
        "port": db_config.port,
        "database": db_config.database,
        "username": db_config.username,
        "password": db_config.password,
        "connection_string": db_config.connection_string,
        "extra_params": db_config.extra_params or {},
    }

    # 测试连接
    try:
        connector = DatabaseConnector(config_dict)
        result = connector.test_connection()
        return DatabaseTestResponse(**result)
    except Exception as e:
        logger.error(f"测试数据库连接时发生错误: {str(e)}", exc_info=True)
        return DatabaseTestResponse(
            success=False,
            message=f"测试失败: {str(e)}",
            details={"error": str(e)},
        )


@router.post("/test/", response_model=DatabaseTestResponse)
def test_database_connection_direct(
    config: DatabaseConfigCreate = Body(...),
):
    """
    直接测试数据库连接（不保存配置）
    """
    # 构建配置字典
    config_dict = config.model_dump()

    # 测试连接
    try:
        connector = DatabaseConnector(config_dict)
        result = connector.test_connection()
        return DatabaseTestResponse(**result)
    except Exception as e:
        logger.error(f"测试数据库连接时发生错误: {str(e)}", exc_info=True)
        return DatabaseTestResponse(
            success=False,
            message=f"测试失败: {str(e)}",
            details={"error": str(e)},
        )


class DatabaseQueryRequest(BaseModel):
    """数据库查询请求模型"""
    table_name: str = "test"
    columns: Optional[List[str]] = None
    limit: Optional[int] = None
    offset: int = 0


class DatabaseQueryResponse(BaseModel):
    """数据库查询响应模型"""
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    count: Optional[int] = None
    error: Optional[str] = None


@router.post("/{config_id}/query/", response_model=DatabaseQueryResponse)
def query_database_data(
    config_id: int,
    request: DatabaseQueryRequest = Body(...),
    db: Session = Depends(get_db),
):
    """
    查询数据库数据
    """
    db_config = (
        db.query(DatabaseConfig).filter(DatabaseConfig.id == config_id).first()
    )
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"数据库配置ID {config_id} 不存在",
        )

    if not db_config.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="数据库配置未启用",
        )

    # 构建配置字典
    config_dict = {
        "db_type": db_config.db_type,
        "host": db_config.host,
        "port": db_config.port,
        "database": db_config.database,
        "username": db_config.username,
        "password": db_config.password,
        "connection_string": db_config.connection_string,
        "extra_params": db_config.extra_params or {},
    }

    # 查询数据
    try:
        connector = DatabaseConnector(config_dict)
        data = connector.query_data(
            table_name=request.table_name,
            columns=request.columns,
            limit=request.limit,
            offset=request.offset,
        )
        count = connector.get_data_count(table_name=request.table_name)

        return DatabaseQueryResponse(
            success=True,
            message=f"成功查询 {len(data)} 条数据",
            data=data,
            count=count,
        )
    except Exception as e:
        logger.error(f"查询数据库数据时发生错误: {str(e)}", exc_info=True)
        return DatabaseQueryResponse(
            success=False,
            message=f"查询失败: {str(e)}",
            data=None,
            count=None,
            error=str(e),
        )

