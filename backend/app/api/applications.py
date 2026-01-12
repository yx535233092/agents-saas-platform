"""
应用管理API路由
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.application import Application
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationTestRequest,
    ApplicationTestResponse,
)
import httpx

router = APIRouter(prefix="/backend/applications", tags=["applications"])


@router.get("/", response_model=List[ApplicationResponse])
def get_applications(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db),
):
    """
    获取应用列表
    """
    query = db.query(Application)

    # 如果指定了is_active，进行过滤
    if is_active is not None:
        query = query.filter(Application.is_active == is_active)

    # 按sort_order和id排序
    applications = (
        query.order_by(Application.sort_order.asc(), Application.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return applications


@router.get("/public/", response_model=List[ApplicationResponse])
def get_public_applications(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    获取公开的应用列表（仅返回启用中的应用）
    """
    applications = (
        db.query(Application)
        .filter(Application.is_active == True)
        .order_by(Application.sort_order.asc(), Application.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return applications


@router.get("/{application_id}/", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    """
    获取单个应用详情
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"应用ID {application_id} 不存在",
        )
    return application


@router.post(
    "/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED
)
def create_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    """
    创建新应用
    """
    # 检查名称是否已存在
    existing = (
        db.query(Application).filter(Application.name == application.name).first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"应用名称 '{application.name}' 已存在",
        )

    # 创建应用对象
    db_application = Application(**application.model_dump())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.patch("/{application_id}/", response_model=ApplicationResponse)
def update_application(
    application_id: int, application: ApplicationUpdate, db: Session = Depends(get_db)
):
    """
    更新应用信息
    """
    db_application = (
        db.query(Application).filter(Application.id == application_id).first()
    )
    if not db_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"应用ID {application_id} 不存在",
        )

    # 如果更新名称，检查是否与其他应用冲突
    update_data = application.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = (
            db.query(Application)
            .filter(
                Application.name == update_data["name"],
                Application.id != application_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"应用名称 '{update_data['name']}' 已存在",
            )

    # 更新字段
    for field, value in update_data.items():
        setattr(db_application, field, value)

    db.commit()
    db.refresh(db_application)
    return db_application


@router.delete("/{application_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db)):
    """
    删除应用
    """
    db_application = (
        db.query(Application).filter(Application.id == application_id).first()
    )
    if not db_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"应用ID {application_id} 不存在",
        )

    db.delete(db_application)
    db.commit()
    return None


@router.post("/{application_id}/test/", response_model=ApplicationTestResponse)
async def test_application(
    application_id: int,
    test_request: Optional[ApplicationTestRequest] = Body(None),
    db: Session = Depends(get_db),
):
    """
    测试应用连接
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"应用ID {application_id} 不存在",
        )

    if not application.is_active:
        return ApplicationTestResponse(success=False, message="应用已禁用，无法测试")

    try:
        # 准备请求头
        headers = application.headers.copy() if application.headers else {}
        if application.request_format == "json":
            headers.setdefault("Content-Type", "application/json")

        # 准备请求数据
        test_data = (
            test_request.test_data if test_request and test_request.test_data else {}
        )

        # 构建请求
        timeout = httpx.Timeout(application.timeout or 300, connect=10)

        async with httpx.AsyncClient(timeout=timeout) as client:
            # 根据HTTP方法发送请求
            if application.api_method.upper() == "GET":
                response = await client.get(
                    application.api_endpoint, headers=headers, params=test_data
                )
            elif application.api_method.upper() == "POST":
                if application.request_format == "json":
                    response = await client.post(
                        application.api_endpoint, headers=headers, json=test_data
                    )
                elif application.request_format == "form-data":
                    response = await client.post(
                        application.api_endpoint, headers=headers, files=test_data
                    )
                else:  # x-www-form-urlencoded
                    response = await client.post(
                        application.api_endpoint, headers=headers, data=test_data
                    )
            elif application.api_method.upper() == "PUT":
                response = await client.put(
                    application.api_endpoint, headers=headers, json=test_data
                )
            elif application.api_method.upper() == "DELETE":
                response = await client.delete(
                    application.api_endpoint, headers=headers
                )
            else:
                return ApplicationTestResponse(
                    success=False, message=f"不支持的HTTP方法: {application.api_method}"
                )

            # 处理响应
            response_data = None
            if application.response_format == "json":
                try:
                    response_data = response.json()
                except:
                    response_data = {"text": response.text}
            else:
                response_data = {
                    "text": response.text,
                    "status_code": response.status_code,
                }

            # 判断是否成功（2xx状态码）
            if 200 <= response.status_code < 300:
                return ApplicationTestResponse(
                    success=True,
                    message=f"连接成功 (HTTP {response.status_code})",
                    data=response_data,
                )
            else:
                return ApplicationTestResponse(
                    success=False,
                    message=f"连接失败 (HTTP {response.status_code}): {response.text[:200]}",
                    data=response_data,
                )

    except httpx.TimeoutException:
        return ApplicationTestResponse(
            success=False, message=f"请求超时（超过 {application.timeout or 300} 秒）"
        )
    except httpx.ConnectError as e:
        return ApplicationTestResponse(success=False, message=f"连接错误: {str(e)}")
    except Exception as e:
        return ApplicationTestResponse(success=False, message=f"测试失败: {str(e)}")
