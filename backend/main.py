import sys
import json
from pathlib import Path
from typing import AsyncGenerator, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

# 添加 agents-langgraph 目录到 Python 路径
current_dir = Path(__file__).parent
agents_langgraph_dir = current_dir.parent / "agents-langgraph"
sys.path.insert(0, str(agents_langgraph_dir))

# 导入工作流节点
from nodes import (
    start_node,
    judgement_scene_node,
    judgement_secret_directory_node,
    judgement_public_content_node,
    decision_review_node,
)

# 加载环境变量
from dotenv import load_dotenv

load_dotenv()

# 导入应用管理模块
from applications import (
    load_applications,
    get_application,
    create_application,
    update_application,
    delete_application,
    get_public_applications,
)

app = FastAPI(title="智能体平台 API", version="1.0.0")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CheckRequest(BaseModel):
    doc_title: str
    doc_content: str


# 应用管理相关的 Pydantic 模型
class ApplicationInput(BaseModel):
    name: str
    description: Optional[str] = None
    app_type: str = "custom"  # 'secret_judgement' | 'custom'
    api_endpoint: str
    api_method: str = "POST"  # 'POST' | 'GET' | 'PUT' | 'DELETE'
    request_format: Optional[str] = (
        "json"  # 'json' | 'form-data' | 'x-www-form-urlencoded'
    )
    response_format: Optional[str] = "json"  # 'json' | 'sse' | 'stream'
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[int] = 300
    icon: Optional[str] = "bot"
    icon_color: Optional[str] = "text-blue-500"
    is_active: bool = True
    sort_order: int = 0


class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    app_type: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_method: Optional[str] = None
    request_format: Optional[str] = None
    response_format: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    icon: Optional[str] = None
    icon_color: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


async def generate_sse_stream(
    doc_title: str, doc_content: str
) -> AsyncGenerator[str, None]:
    """生成 SSE 流式响应"""
    try:
        # 初始化状态
        input_state = {
            "doc_title": doc_title,
            "doc_content": doc_content,
            "current_node": "start_node",
            "scene": "",
            "is_sensitive": False,
            "evidence": "",
            "secret_analysis_result": {},
            "public_analysis_result": {},
            "confidence": 0,
        }

        # 发送开始消息
        yield f"data: {json.dumps({'type': 'progress', 'node': 'start_node', 'data': {}}, ensure_ascii=False)}\n\n"

        # 执行 start_node
        try:
            state_after_start = start_node(input_state.copy())
            input_state.update(state_after_start)
            yield f"data: {json.dumps({'type': 'progress', 'node': 'start_node', 'data': {'status': 'completed'}}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'node': 'start_node', 'message': str(e)}, ensure_ascii=False)}\n\n"
            return

        # 执行 judgement_scene_node
        try:
            yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_scene_node', 'data': {'status': 'started'}}, ensure_ascii=False)}\n\n"
            state_after_scene = judgement_scene_node(input_state.copy())
            input_state.update(state_after_scene)
            yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_scene_node', 'data': {'scene': input_state.get('scene', '')}}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'node': 'judgement_scene_node', 'message': str(e)}, ensure_ascii=False)}\n\n"
            return

        # 执行 judgement_secret_directory_node
        try:
            yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_secret_directory_node', 'data': {'status': 'started'}}, ensure_ascii=False)}\n\n"
            state_after_secret = judgement_secret_directory_node(input_state.copy())
            input_state.update(state_after_secret)
            secret_result = input_state.get("secret_analysis_result", {})
            # 尝试解析 JSON 字符串
            if isinstance(secret_result, str):
                try:
                    secret_result = json.loads(secret_result)
                except:
                    pass
            yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_secret_directory_node', 'data': secret_result}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'node': 'judgement_secret_directory_node', 'message': str(e)}, ensure_ascii=False)}\n\n"
            return

        # 执行 judgement_public_content_node
        try:
            yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_public_content_node', 'data': {'status': 'started'}}, ensure_ascii=False)}\n\n"
            state_after_public = judgement_public_content_node(input_state.copy())
            input_state.update(state_after_public)
            public_result = input_state.get("public_analysis_result", {})
            # 尝试解析 JSON 字符串
            if isinstance(public_result, str):
                try:
                    public_result = json.loads(public_result)
                except:
                    pass
            yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_public_content_node', 'data': public_result}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'node': 'judgement_public_content_node', 'message': str(e)}, ensure_ascii=False)}\n\n"
            return

        # 执行 decision_review_node (决策评审)
        try:
            yield f"data: {json.dumps({'type': 'progress', 'node': 'agent_decision', 'data': {'status': 'started'}}, ensure_ascii=False)}\n\n"

            # 确保 secret_analysis_result 和 public_analysis_result 是字典格式
            # 如果它们是字符串，需要先解析
            secret_result = input_state.get("secret_analysis_result", {})
            if isinstance(secret_result, str):
                try:
                    secret_result = json.loads(secret_result)
                except:
                    pass

            public_result = input_state.get("public_analysis_result", {})
            if isinstance(public_result, str):
                try:
                    public_result = json.loads(public_result)
                except:
                    pass

            # 更新状态中的结果
            input_state["secret_analysis_result"] = secret_result
            input_state["public_analysis_result"] = public_result

            # 执行决策节点
            state_after_decision = decision_review_node(input_state.copy())
            input_state.update(state_after_decision)

            decision_result = {
                "is_sensitive": input_state.get("is_sensitive", False),
                "confidence": input_state.get("confidence", 0),
                "evidence": input_state.get("evidence", ""),
            }
            yield f"data: {json.dumps({'type': 'progress', 'node': 'agent_decision', 'data': decision_result}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'node': 'agent_decision', 'message': str(e)}, ensure_ascii=False)}\n\n"
            return

        # 发送最终结果
        final_data = {
            "type": "final",
            "data": {
                "doc_title": input_state.get("doc_title", ""),
                "is_sensitive": input_state.get("is_sensitive", False),
                "confidence": input_state.get("confidence", 0),
                "evidence": input_state.get("evidence", ""),
                "scene": input_state.get("scene", ""),
                "secret_analysis_result": input_state.get("secret_analysis_result", {}),
                "public_analysis_result": input_state.get("public_analysis_result", {}),
            },
        }
        yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"

    except Exception as e:
        error_data = {"type": "error", "message": f"处理过程中发生错误: {str(e)}"}
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"


@app.post("/check")
async def check_secret(request: CheckRequest):
    """
    涉密研判接口 - 使用 SSE 流式返回处理过程
    """
    return StreamingResponse(
        generate_sse_stream(request.doc_title, request.doc_content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "智能体平台 API"}


# ==================== 应用管理 API ====================


@app.get("/api/applications/")
async def list_applications():
    """获取应用列表（管理员接口）"""
    applications = load_applications()
    return applications


@app.get("/api/applications/public/")
async def list_public_applications():
    """获取公开的应用列表（前台接口，无需认证）"""
    applications = get_public_applications()
    return applications


@app.get("/api/applications/{app_id}/")
async def get_app(app_id: int):
    """获取单个应用详情"""
    app = get_application(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="应用不存在")
    return app


@app.post("/api/applications/")
async def create_app(application: ApplicationInput):
    """创建新应用"""
    app_data = application.dict(exclude_none=True)
    new_app = create_application(app_data)
    return new_app


@app.patch("/api/applications/{app_id}/")
async def update_app(app_id: int, application: ApplicationUpdate):
    """更新应用配置"""
    app_data = application.dict(exclude_none=True)
    updated_app = update_application(app_id, app_data)
    if not updated_app:
        raise HTTPException(status_code=404, detail="应用不存在")
    return updated_app


@app.delete("/api/applications/{app_id}/")
async def delete_app(app_id: int):
    """删除应用"""
    success = delete_application(app_id)
    if not success:
        raise HTTPException(status_code=404, detail="应用不存在")
    return {"message": "应用已删除"}


@app.post("/api/applications/{app_id}/test/")
async def test_app(app_id: int, test_data: Optional[Dict[str, Any]] = None):
    """测试应用连接"""
    app = get_application(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="应用不存在")

    try:
        # 根据应用类型准备测试数据
        if app.get("app_type") == "secret_judgement":
            test_payload = test_data or {
                "doc_title": "测试文档",
                "doc_content": "这是一段测试内容，用于验证涉密研判智能体的连接。",
            }
        else:
            test_payload = test_data or {"message": "test"}

        # 准备请求
        headers = app.get("headers", {}) or {}
        if app.get("request_format") == "json":
            headers["Content-Type"] = "application/json"

        # 发送测试请求
        async with httpx.AsyncClient(timeout=app.get("timeout", 300)) as client:
            method = app.get("api_method", "POST").upper()
            endpoint = app.get("api_endpoint")

            if method == "GET":
                response = await client.get(
                    endpoint, headers=headers, params=test_payload
                )
            elif method == "POST":
                response = await client.post(
                    endpoint, headers=headers, json=test_payload
                )
            elif method == "PUT":
                response = await client.put(
                    endpoint, headers=headers, json=test_payload
                )
            elif method == "DELETE":
                response = await client.delete(endpoint, headers=headers)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            if response.status_code < 400:
                return {
                    "success": True,
                    "message": f"连接成功 (状态码: {response.status_code})",
                    "data": response.text[:500] if response.text else None,
                }
            else:
                return {
                    "success": False,
                    "message": f"连接失败 (状态码: {response.status_code}): {response.text[:200]}",
                }
    except httpx.TimeoutException:
        return {
            "success": False,
            "message": f"请求超时（超时时间: {app.get('timeout', 300)}秒）",
        }
    except httpx.ConnectError:
        return {
            "success": False,
            "message": f"无法连接到 {app.get('api_endpoint')}，请检查端点地址是否正确",
        }
    except Exception as e:
        return {"success": False, "message": f"测试失败: {str(e)}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
