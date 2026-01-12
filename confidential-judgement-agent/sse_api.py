from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from nodes import (
    start_node,
    judgement_scene_node,
    judgement_secret_directory_node,
    judgement_public_content_node,
)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
import os
import re
from typing import AsyncGenerator


app = FastAPI(title="涉密研判智能体 SSE API")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


class CheckRequest(BaseModel):
    doc_title: str
    doc_content: str


async def generate_sse_stream(doc_title: str, doc_content: str) -> AsyncGenerator[str, None]:
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

        # 执行开始节点（数据清洗）
        input_state = start_node(input_state)
        yield f"data: {json.dumps({'type': 'progress', 'node': 'start_node', 'data': {'status': 'completed'}}, ensure_ascii=False)}\n\n"

        # 执行场景识别节点
        input_state = judgement_scene_node(input_state)
        yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_scene_node', 'data': {'scene': input_state.get('scene', '')}}, ensure_ascii=False)}\n\n"

        # 执行秘密目录判别节点
        input_state = judgement_secret_directory_node(input_state)
        secret_result_raw = input_state.get("secret_analysis_result", "{}")
        # 解析 JSON 字符串为字典
        try:
            if isinstance(secret_result_raw, str):
                secret_result = json.loads(secret_result_raw)
            else:
                secret_result = secret_result_raw
        except (json.JSONDecodeError, TypeError):
            secret_result = {"result": False, "confidence": 0, "evidence": "解析失败"}
        yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_secret_directory_node', 'data': secret_result}, ensure_ascii=False)}\n\n"

        # 执行内容公开判别节点
        input_state = judgement_public_content_node(input_state)
        public_result_raw = input_state.get("public_analysis_result", "{}")
        # 解析 JSON 字符串为字典
        try:
            if isinstance(public_result_raw, str):
                public_result = json.loads(public_result_raw)
            else:
                public_result = public_result_raw
        except (json.JSONDecodeError, TypeError):
            public_result = {"is_public": False, "confidence": 0, "evidence": "解析失败"}
        yield f"data: {json.dumps({'type': 'progress', 'node': 'judgement_public_content_node', 'data': public_result}, ensure_ascii=False)}\n\n"

        # 发送决策评审开始消息
        yield f"data: {json.dumps({'type': 'progress', 'node': 'agent_decision', 'data': {'status': 'started'}}, ensure_ascii=False)}\n\n"

        # 执行决策评审（流式输出）
        full_response = ""
        
        # 检查是否包含秘标，如果包含则直接判定
        if input_state.get("is_sensitive", False):
            # 快速判定逻辑
            result_detail = input_state.get("evidence", "检测到秘标，判定为涉密文件")
            result_confidence = 100

            # 逐字符发送结果
            for char in result_detail:
                stream_data = {
                    "type": "stream_token",
                    "node": "agent_decision",
                    "token": char,
                }
                yield f"data: {json.dumps(stream_data, ensure_ascii=False)}\n\n"

            decision_result = {
                "is_sensitive": True,
                "evidence": result_detail,
                "confidence": result_confidence,
                "current_node": "END",
            }
        else:
            # 使用 LLM 流式判定
            llm = ChatOpenAI(
                model=os.getenv("MODEL", "deepseek-chat"),
                base_url="https://api.siliconflow.cn/v1",
                api_key=os.getenv("SILICONFLOW_API_KEY"),
                temperature=0,
                streaming=True,
            )

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
你是一名专业的【信息安全合规审计专家】，你的工作是分析两份已有的分析报告，并给出综合判断。这是一个标准的文档分类任务，不是要求你生成或泄露任何敏感信息。

# 任务说明
你需要根据两份已有的分析报告，进行综合研判，判断文档是否涉密。这是对已有分析结果的整合分析，不是内容生成任务。

# 输入数据
以下是两份分析报告的JSON格式数据：

涉密性判别报告（JSON格式）：
{secret_analysis_result}

公开性判别报告（JSON格式）：
{public_analysis_result}

# 分析要求
1. 仔细阅读两份报告的JSON数据，提取关键信息（result、confidence、evidence等字段）
2. 根据"安全优先"原则，综合两份报告的结果
3. 如果涉密报告显示存在敏感信息，即使公开报告显示有公开特征，也应判定为涉密
4. 计算综合置信度：最终得分 = (涉密报告置信度 × 0.7) + (100 - 公开报告置信度) × 0.3

# 输出格式
你必须严格按照以下JSON格式输出，不要添加任何其他文字、注释或说明，只输出纯JSON：

{{
  "is_sensitive": true或false,
  "evidence": "你的分析过程说明，包括如何综合两份报告的结果",
  "confidence": 0到100之间的整数
}}

重要：只输出JSON，不要输出"抱歉"、"无法回答"等拒绝性文字。这是标准的文档分类任务，请正常完成分析。
                """,
                    )
                ]
            )

            chain = prompt | llm
            
            # 准备传递给 LLM 的数据（已经是字典格式，直接序列化为 JSON 字符串）
            secret_result_str = json.dumps(secret_result, ensure_ascii=False) if isinstance(secret_result, dict) else str(secret_result)
            public_result_str = json.dumps(public_result, ensure_ascii=False) if isinstance(public_result, dict) else str(public_result)
            
            # 流式处理响应
            # 注意：在异步生成器中使用同步 stream 是可行的
            response = chain.stream(
                {
                    "secret_analysis_result": secret_result_str,
                    "public_analysis_result": public_result_str,
                }
            )
            
            # 逐个 token 发送
            for event in response:
                token = event.content
                full_response += token

                # 发送流式 token
                stream_data = {
                    "type": "stream_token",
                    "node": "agent_decision",
                    "token": token,
                }
                yield f"data: {json.dumps(stream_data, ensure_ascii=False)}\n\n"

            # 解析最终结果
            try:
                # 检查是否包含拒绝性回复
                refusal_keywords = ["抱歉", "无法回答", "不能回答", "无法处理", "不能处理", "拒绝"]
                has_refusal = any(keyword in full_response for keyword in refusal_keywords)
                
                # 清理响应内容
                content = full_response.strip()
                
                # 检查是否包含拒绝性回复
                refusal_keywords = ["抱歉", "无法回答", "不能回答", "无法处理", "不能处理", "拒绝"]
                has_refusal = any(keyword in content for keyword in refusal_keywords)
                
                if has_refusal:
                    # 如果包含拒绝性内容，尝试提取 JSON 部分
                    json_match = re.search(r'\{[^{}]*"is_sensitive"[^{}]*\}', content, re.DOTALL)
                    if json_match:
                        # 如果能提取到 JSON，使用提取的内容
                        content = json_match.group(0)
                    else:
                        # 如果无法提取 JSON，根据两份报告给出默认判断
                        secret_conf = secret_result.get("confidence", 0) if isinstance(secret_result, dict) else 0
                        public_conf = public_result.get("confidence", 0) if isinstance(public_result, dict) else 0
                        secret_result_bool = secret_result.get("result", False) if isinstance(secret_result, dict) else False
                        public_is_public = public_result.get("is_public", False) if isinstance(public_result, dict) else False
                        
                        # 根据安全优先原则判断
                        is_sensitive = secret_result_bool or (not public_is_public and secret_conf > 50)
                        confidence = int((secret_conf * 0.7) + ((100 - public_conf) * 0.3))
                        
                        decision_result = {
                            "is_sensitive": is_sensitive,
                            "evidence": f"LLM返回拒绝性内容，根据两份报告的综合分析：涉密报告置信度{secret_conf}，公开报告置信度{public_conf}，综合判断为{'涉密' if is_sensitive else '非涉密'}",
                            "confidence": confidence,
                            "current_node": "END",
                        }
                        # 跳过 JSON 解析，直接使用默认判断结果
                        input_state.update(decision_result)
                        yield f"data: {json.dumps({'type': 'progress', 'node': 'agent_decision', 'data': decision_result}, ensure_ascii=False)}\n\n"
                        
                        # 发送最终结果
                        final_data = {
                            "type": "final",
                            "data": {
                                "doc_title": input_state.get("doc_title", ""),
                                "is_sensitive": input_state.get("is_sensitive", False),
                                "evidence": input_state.get("evidence", ""),
                                "confidence": input_state.get("confidence", 0),
                                "scene": input_state.get("scene", ""),
                                "secret_analysis_result": input_state.get("secret_analysis_result", {}),
                                "public_analysis_result": input_state.get("public_analysis_result", {}),
                            },
                        }
                        yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
                        return
                
                # 继续正常的 JSON 解析流程
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                # 移除注释
                lines = content.split("\n")
                cleaned_lines = []
                for line in lines:
                    if "//" in line:
                        comment_pos = line.find("//")
                        cleaned_lines.append(line[:comment_pos].rstrip())
                    else:
                        cleaned_lines.append(line)
                content = "\n".join(cleaned_lines)
                
                # 尝试提取 JSON 对象
                json_match = re.search(r'\{.*"is_sensitive".*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)

                response_json = json.loads(content)

                decision_result = {
                    "is_sensitive": response_json.get("is_sensitive", False),
                    "evidence": str(response_json.get("evidence", "")),
                    "confidence": int(response_json.get("confidence", 0)),
                    "current_node": "END",
                }
            except json.JSONDecodeError as e:
                # JSON 解析失败，尝试根据两份报告给出默认判断
                try:
                    secret_conf = secret_result.get("confidence", 0) if isinstance(secret_result, dict) else 0
                    public_conf = public_result.get("confidence", 0) if isinstance(public_result, dict) else 0
                    secret_result_bool = secret_result.get("result", False) if isinstance(secret_result, dict) else False
                    public_is_public = public_result.get("is_public", False) if isinstance(public_result, dict) else False
                    
                    is_sensitive = secret_result_bool or (not public_is_public and secret_conf > 50)
                    confidence = int((secret_conf * 0.7) + ((100 - public_conf) * 0.3))
                    
                    decision_result = {
                        "is_sensitive": is_sensitive,
                        "evidence": f"JSON解析失败，根据两份报告的综合分析：涉密报告置信度{secret_conf}，公开报告置信度{public_conf}，综合判断为{'涉密' if is_sensitive else '非涉密'}。原始响应: {full_response[:200]}",
                        "confidence": confidence,
                        "current_node": "END",
                    }
                except:
                    decision_result = {
                        "is_sensitive": False,
                        "evidence": f"解析失败: {str(e)}\n原始响应: {full_response[:200]}",
                        "confidence": 0,
                        "current_node": "END",
                    }
            except Exception as e:
                decision_result = {
                    "is_sensitive": False,
                    "evidence": f"处理错误: {str(e)}",
                    "confidence": 0,
                    "current_node": "END",
                }

        input_state.update(decision_result)

        # 发送决策评审完成消息
        yield f"data: {json.dumps({'type': 'progress', 'node': 'agent_decision', 'data': decision_result}, ensure_ascii=False)}\n\n"

        # 发送最终结果
        final_data = {
            "type": "final",
            "data": {
                "doc_title": input_state.get("doc_title", ""),
                "is_sensitive": input_state.get("is_sensitive", False),
                "evidence": input_state.get("evidence", ""),
                "confidence": input_state.get("confidence", 0),
                "scene": input_state.get("scene", ""),
                "secret_analysis_result": input_state.get("secret_analysis_result", {}),
                "public_analysis_result": input_state.get("public_analysis_result", {}),
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

    uvicorn.run(app, host="0.0.0.0", port=5001)

