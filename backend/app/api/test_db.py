"""
测试数据库 API 路由
提供测试数据库的连接和批量处理功能
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Query, Body
from pydantic import BaseModel

from app.core.test_db import test_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backend/test-db", tags=["test-db"])


class TestDbResponse(BaseModel):
    """测试数据库响应模型"""
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    count: Optional[int] = None
    error: Optional[str] = None


class ConnectionTestResponse(BaseModel):
    """连接测试响应模型"""
    connected: bool
    db_path: str
    table_exists: bool
    record_count: int
    message: str
    error: Optional[str] = None


class BatchProcessRequest(BaseModel):
    """批量处理请求模型"""
    limit: Optional[int] = None
    offset: int = 0
    batch_size: int = 10


@router.get("/", response_model=TestDbResponse)
def get_test_db_data(
    limit: Optional[int] = Query(None, description="限制返回的记录数"),
    offset: int = Query(0, ge=0, description="偏移量，用于分页"),
):
    """
    获取测试数据库中的所有数据

    Args:
        limit: 限制返回的记录数
        offset: 偏移量

    Returns:
        测试数据列表
    """
    try:
        # 获取数据
        data = test_db.get_all_data(limit=limit, offset=offset)
        count = test_db.get_data_count()

        logger.info(f"成功获取 {len(data)} 条测试数据（总计: {count}）")

        return TestDbResponse(
            success=True,
            message=f"成功获取 {len(data)} 条数据",
            data=data,
            count=count,
        )
    except FileNotFoundError as e:
        logger.error(f"测试数据库文件不存在: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"测试数据库文件不存在: {str(e)}",
        )
    except Exception as e:
        logger.error(f"获取测试数据时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取测试数据失败: {str(e)}",
        )


@router.get("/count", response_model=Dict[str, int])
def get_test_db_count():
    """
    获取测试数据库中的数据总数

    Returns:
        数据总数
    """
    try:
        count = test_db.get_data_count()
        return {"count": count}
    except Exception as e:
        logger.error(f"获取数据总数时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据总数失败: {str(e)}",
        )


@router.get("/{record_id}", response_model=TestDbResponse)
def get_test_db_record(record_id: int):
    """
    根据 ID 获取单条测试数据

    Args:
        record_id: 记录 ID

    Returns:
        测试数据
    """
    try:
        data = test_db.get_data_by_id(record_id)
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"记录 ID {record_id} 不存在",
            )

        return TestDbResponse(
            success=True,
            message="成功获取数据",
            data=[data],
            count=1,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取测试数据时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取测试数据失败: {str(e)}",
        )


@router.get("/connection/test", response_model=ConnectionTestResponse)
def test_connection():
    """
    测试数据库连接

    Returns:
        连接测试结果
    """
    try:
        result = test_db.test_connection()
        return ConnectionTestResponse(**result)
    except Exception as e:
        logger.error(f"测试数据库连接时发生错误: {str(e)}")
        return ConnectionTestResponse(
            connected=False,
            db_path=test_db.db_path,
            table_exists=False,
            record_count=0,
            message=f"连接测试失败: {str(e)}",
            error=str(e),
        )


@router.post("/batch-process", response_model=Dict[str, Any])
def batch_process_data(
    request: BatchProcessRequest = Body(...),
):
    """
    批量处理测试数据库中的数据

    注意：此端点仅用于演示批量处理功能。
    实际的处理逻辑应该由调用方实现，这里只返回数据列表。

    Args:
        request: 批量处理请求参数

    Returns:
        处理结果统计
    """
    try:
        # 获取要处理的数据
        data = test_db.get_all_data(limit=request.limit, offset=request.offset)

        return {
            "success": True,
            "message": f"获取到 {len(data)} 条数据，可以进行批量处理",
            "data_count": len(data),
            "total_count": test_db.get_data_count(),
            "batch_size": request.batch_size,
            "offset": request.offset,
            "limit": request.limit,
            "note": "实际的处理逻辑应由调用方实现，这里只返回数据列表",
        }
    except Exception as e:
        logger.error(f"批量处理时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量处理失败: {str(e)}",
        )

