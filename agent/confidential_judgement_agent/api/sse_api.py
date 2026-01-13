"""SSE API 服务"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator
import json

from confidential_judgement_agent.workflow import app as workflow_app
from confidential_judgement_agent.workflow.nodes import decision_review_node
from confidential_judgement_agent.config import get_settings

settings = get_settings()

app = FastAPI(title="涉密研判智能体 SSE API")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


class CheckRequest(BaseModel):
    """检查请求模型"""
    doc_title: str
    doc_content: str


async def generate_sse_stream(
    doc_title: str, doc_content: str
) -> AsyncGenerator[str, None]:
    """生成 SSE 流式响应 - 使用工作流 astream"""
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

        # 使用工作流的 astream 执行到决策节点之前的所有节点
        current_state = input_state.copy()
        secret_result = {}
        public_result = {}

        # 流式执行工作流，处理每个节点的输出
        async for event in workflow_app.astream(input_state):
            # event 是一个字典，key 是节点名，value 是节点更新后的状态
            for node_name, node_state in event.items():
                # 如果到达决策节点，跳过工作流的决策节点输出，稍后手动处理流式决策
                if node_name == "agent_decision":
                    # 更新状态但不发送进度消息，稍后手动处理流式输出
                    current_state.update(node_state)
                    continue

                # 更新当前状态
                current_state.update(node_state)

                # 根据节点类型发送不同的进度消息
                if node_name == "start_node":
                    yield f"data: {json.dumps({'type': 'progress', 'node': 'start_node', 'data': {'status': 'completed'}}, ensure_ascii=False)}\n\n"

                elif node_name == "judgement_scene_node":
                    scene = current_state.get("scene", "")
                    yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_scene_node', 'data': {'scene': scene}}, ensure_ascii=False)}\n\n"

                elif node_name == "judgement_secret_directory_node":
                    secret_result_raw = current_state.get(
                        "secret_analysis_result", "{}"
                    )
                    # 解析 JSON 字符串为字典
                    try:
                        if isinstance(secret_result_raw, str):
                            secret_result = json.loads(secret_result_raw)
                        else:
                            secret_result = secret_result_raw
                    except (json.JSONDecodeError, TypeError):
                        secret_result = {
                            "result": False,
                            "confidence": 0,
                            "evidence": "解析失败",
                        }
                    yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_secret_directory_node', 'data': secret_result}, ensure_ascii=False)}\n\n"

                elif node_name == "judgement_public_content_node":
                    public_result_raw = current_state.get(
                        "public_analysis_result", "{}"
                    )
                    # 解析 JSON 字符串为字典
                    try:
                        if isinstance(public_result_raw, str):
                            public_result = json.loads(public_result_raw)
                        else:
                            public_result = public_result_raw
                    except (json.JSONDecodeError, TypeError):
                        public_result = {
                            "is_public": False,
                            "confidence": 0,
                            "evidence": "解析失败",
                        }
                    yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_public_content_node', 'data': public_result}, ensure_ascii=False)}\n\n"

        # 发送决策评审开始消息
        yield f"data: {json.dumps({'type': 'progress', 'node': 'agent_decision', 'data': {'status': 'started'}}, ensure_ascii=False)}\n\n"

        # 执行决策评审（流式输出）
        # 使用 nodes.py 中的流式函数
        state_copy = current_state.copy()
        tokens = []  # 收集所有 token

        def token_callback(token):
            """收集 token 的回调函数"""
            tokens.append(token)

        # 调用决策评审节点（流式版本）
        updated_state = decision_review_node(state_copy, token_callback=token_callback)

        # 流式发送收集到的 token
        for token in tokens:
            stream_data = {
                "type": "stream_token",
                "node": "agent_decision",
                "token": token,
            }
            yield f"data: {json.dumps(stream_data, ensure_ascii=False)}\n\n"

        # 更新状态
        current_state.update(updated_state)

        decision_result = {
            "is_sensitive": current_state.get("is_sensitive", False),
            "evidence": current_state.get("evidence", ""),
            "confidence": current_state.get("confidence", 0),
            "current_node": "END",
        }

        # 发送决策评审完成消息
        yield f"data: {json.dumps({'type': 'progress', 'node': 'agent_decision', 'data': decision_result}, ensure_ascii=False)}\n\n"

        # 发送最终结果
        final_data = {
            "type": "final",
            "data": {
                "doc_title": current_state.get("doc_title", ""),
                "is_sensitive": current_state.get("is_sensitive", False),
                "evidence": current_state.get("evidence", ""),
                "confidence": current_state.get("confidence", 0),
                "scene": current_state.get("scene", ""),
                "secret_analysis_result": current_state.get(
                    "secret_analysis_result", {}
                ),
                "public_analysis_result": current_state.get(
                    "public_analysis_result", {}
                ),
            },
        }
        yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"

    except Exception as e:
        # 发送错误消息
        error_data = {
            "type": "error",
            "message": str(e),
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"


@app.post("/api/check")
async def check_secret(request: CheckRequest):
    """
    涉密研判智能体 SSE 接口

    接收文档标题和内容，通过 SSE 流式返回研判过程及结果
    """
    return EventSourceResponse(
        generate_sse_stream(request.doc_title, request.doc_content)
    )


@app.get("/health")
async def health():
    """健康检查接口"""
    return {"status": "ok", "service": "涉密研判智能体 SSE API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)

