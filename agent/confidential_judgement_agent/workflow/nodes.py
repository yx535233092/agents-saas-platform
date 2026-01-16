"""工作流节点定义 - 工程化版本"""

import json
import re
from typing import Optional, Callable, Dict, Any, Tuple
from colorama import Fore, Style
import httpx

from confidential_judgement_agent.config import get_settings
from confidential_judgement_agent.core.logger import logger
from confidential_judgement_agent.core.exceptions import (
    RetrievalError,
    LLMError,
)
from confidential_judgement_agent.core.decorators import (
    node_error_handler,
    log_execution_time,
    validate_state,
)
from confidential_judgement_agent.utils.output import output
from confidential_judgement_agent.utils.secret_menu_parse import secret_menu_parse
from confidential_judgement_agent.utils.public_judgement import public_judgement
from confidential_judgement_agent.workflow.state import State
from confidential_judgement_agent.workflow.utils import (
    safe_json_parse,
    update_evidence,
    is_secretlogo_match,
    create_error_state,
    clean_doc_content,
    extract_chunk_content,
)
from confidential_judgement_agent.workflow.prompts import (
    get_decision_review_prompt,
    get_secret_analysis_prompt,
    get_public_analysis_prompt,
)
from confidential_judgement_agent.workflow.llm_factory import get_llm
from confidential_judgement_agent.utils.scene_judgement import judgement_scene

settings = get_settings()


# ==================== LLM 处理工具函数 ====================


def _stream_llm_response(
    chain: Any,
    input_data: Dict[str, Any],
    token_callback: Optional[Callable[[str], None]] = None,
) -> Tuple[str, Optional[Exception]]:
    """
    流式处理 LLM 响应

    Args:
        chain: LangChain chain 对象
        input_data: 输入数据
        token_callback: 可选的 token 回调函数

    Returns:
        (完整响应, 异常对象)
    """
    full_response = ""
    try:
        for event in chain.stream(input_data):
            token = event.content
            full_response += token
            if token_callback:
                token_callback(token)
        return full_response, None
    except Exception as e:
        logger.error(f"LLM 流式处理失败: {str(e)}", exc_info=True)
        raise LLMError(str(e), details={"input_data_keys": list(input_data.keys())})


@log_execution_time
def _process_llm_node(
    state: State,
    node_name: str,
    prompt_template: Any,
    input_data: Dict[str, Any],
    default_result: Dict[str, Any],
    token_callback: Optional[Callable[[str], None]] = None,
    update_evidence: bool = False,
) -> Tuple[State, Dict[str, Any]]:
    """
    通用的 LLM 节点处理函数

    Args:
        state: 工作流状态
        node_name: 节点名称
        prompt_template: 提示词模板
        input_data: 输入数据
        default_result: 默认结果
        token_callback: 可选的 token 回调函数
        update_evidence: 是否更新证据链

    Returns:
        (更新后的状态, 原始响应JSON)
    """
    output(f"Agent{node_name}", state)

    try:
        llm = get_llm(streaming=True)
        chain = prompt_template | llm
        full_response, error = _stream_llm_response(chain, input_data, token_callback)

        if error:
            raise error

        print(full_response)
        response_json = safe_json_parse(full_response, default_result)
        result_state = {"current_node": node_name, **response_json}

        if update_evidence and "evidence" in response_json:
            result_state["evidence"] = update_evidence(
                state, node_name, response_json["evidence"]
            )

        return result_state, response_json
    except Exception as e:
        logger.error(f"LLM 节点处理失败: {node_name}", exc_info=True)
        return create_error_state(
            node_name, f"{node_name}失败: {str(e)}", default_result
        ), default_result


# ==================== 基础节点 ====================


@node_error_handler("start_node")
@validate_state(required_fields=["doc_content"])
def start_node(state: State) -> State:
    """
    开始节点：数据清洗和初始化

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    """
    开始节点：数据清洗和初始化

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    output("start_node", state, is_first=True)

    # 数据清洗
    content = clean_doc_content(state.get("doc_content", ""))

    return {
        "current_node": "start_node",
        "doc_title": state.get("doc_title", ""),
        "doc_content": content,
        "is_sensitive": False,
        "evidence": "",
        "error": "",
    }


@node_error_handler("judgement_secretlogo_node")
@log_execution_time
def judgement_secretlogo_node(state: State) -> State:
    """
    秘标识别节点：检测文档中的秘标标识

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    output("Agent秘标识别", state)

    doc_content = state.get("doc_content", "")
    pattern = r"(绝密|机密|秘密)\s*★\s*(\d+[年月]|长期|启封前|公开前)"
    match = re.search(pattern, doc_content)

    if match:
        evidence = f"秘标匹配成功，判定为涉密文件，秘标：{match.group()}"
        return {
            "current_node": "judgement_secretlogo_node",
            "is_sensitive": True,
            "evidence": update_evidence(state, "judgement_secretlogo_node", evidence),
        }

    return {
        "current_node": "judgement_secretlogo_node",
        "is_sensitive": False,
    }


def judgement_scene_node(state: State) -> State:
    """
    场景识别节点：识别文档所属场景

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    output("Agent场景识别", state)

    text = state.get("doc_content", "")
    scene = judgement_scene(text)

    logger.info(f"识别场景: {scene}")

    return {
        "current_node": "judgement_scene_node",
        "scene": scene,
    }


def _build_retrieval_request(doc_content: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    构建检索请求

    Args:
        doc_content: 文档内容

    Returns:
        (请求数据, 请求头)
    """
    request_data = {
        "kb_id": [settings.RETRIEVAL_KB_ID],
        "highlight": True,
        "question": f"文本内容： {doc_content}",
        "page": 1,
        "size": settings.RETRIEVAL_PAGE_SIZE,
        "search_id": settings.RETRIEVAL_SEARCH_ID,
        "tenant_id": None,
    }

    headers = {
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Authorization": settings.RETRIEVAL_AUTHORIZATION or "",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    }

    return request_data, headers


def _send_retrieval_request(
    request_data: Dict[str, Any], headers: Dict[str, str]
) -> Dict[str, Any]:
    """
    发送检索请求

    Args:
        request_data: 请求数据
        headers: 请求头

    Returns:
        响应结果

    Raises:
        httpx.HTTPStatusError: HTTP 状态错误
        httpx.RequestError: 请求错误
    """
    logger.info(f"调用检索接口: {settings.RETRIEVAL_API_URL}")
    logger.debug(f"请求数据: {json.dumps(request_data, ensure_ascii=False)}")

    with httpx.Client(timeout=30.0, verify=False) as client:
        response = client.post(
            settings.RETRIEVAL_API_URL,
            headers=headers,
            json=request_data,
        )
        response.raise_for_status()
        return response.json()


def _process_retrieval_result(
    result: Dict[str, Any], scene: str
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    处理检索结果

    Args:
        result: API 返回的原始结果
        scene: 场景类型

    Returns:
        (检索结果字典, 相似度最高的chunk)
    """
    code = result.get("code", -1)
    if code != 0:
        error_msg = f"检索接口返回错误: code={code}, message={result.get('message', '未知错误')}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
        }, None

    data = result.get("data", {})
    chunks = data.get("chunks", [])
    total = data.get("total", 0)
    doc_aggs = data.get("doc_aggs", [])

    retrieval_result = {
        "success": True,
        "code": code,
        "message": result.get("message", ""),
        "total": total,
        "chunks_count": len(chunks),
        "scene": scene,
        "chunks": chunks,
        "doc_aggs": doc_aggs,
    }

    # 提取前几个chunk的内容作为摘要
    if chunks:
        chunk_contents = []
        for chunk in chunks[:5]:
            content = extract_chunk_content(chunk)
            if content:
                chunk_contents.append(
                    f"[相似度: {chunk.get('similarity', 0):.3f}] {content[:200]}"
                )
        retrieval_result["chunk_summary"] = "\n\n".join(chunk_contents)

    # 找到相似度最高的chunk
    secret_menu_chunk = None
    if chunks:
        sorted_chunks = sorted(
            chunks, key=lambda x: x.get("similarity", 0), reverse=True
        )
        secret_menu_chunk = sorted_chunks[0]
        logger.info(
            f"找到相似度最高的chunk: similarity={secret_menu_chunk.get('similarity', 0):.4f}, "
            f"chunk_id={secret_menu_chunk.get('chunk_id')}"
        )

    return retrieval_result, secret_menu_chunk


@node_error_handler("retrieve_secret_menu")
@log_execution_time
@validate_state(required_fields=["doc_content"])
def retrieve_secret_menu(state: State) -> State:
    """
    检索秘密目录节点：调用检索接口获取相关信息

    Args:
        state: 工作流状态

    Returns:
        更新后的状态，包含检索结果
    """
    output("Agent检索秘密目录", state)

    doc_content = state.get("doc_content", "")
    scene = state.get("scene", "")

    if not doc_content:
        from confidential_judgement_agent.core.exceptions import ValidationError

        raise ValidationError(field="doc_content", message="文档内容为空，无法进行检索")

    request_data, headers = _build_retrieval_request(doc_content)
    result = _send_retrieval_request(request_data, headers)
    logger.info(f"检索接口返回结果: {json.dumps(result, ensure_ascii=False)[:500]}")

    retrieval_result, secret_menu_chunk = _process_retrieval_result(result, scene)

    if not retrieval_result.get("success"):
        raise RetrievalError(
            retrieval_result.get("error", "检索失败"),
            details={"retrieval_result": retrieval_result},
        )

    print(
        f"{Fore.GREEN}检索成功，返回 {retrieval_result.get('chunks_count', 0)} 条结果{Style.RESET_ALL}"
    )
    if secret_menu_chunk:
        print(
            f"{Fore.GREEN}相似度最高的chunk已保存到secret_menu字段，"
            f"相似度: {secret_menu_chunk.get('similarity', 0):.4f}{Style.RESET_ALL}"
        )

    return_state = {
        "current_node": "retrieve_secret_menu",
        "retrieval_result": retrieval_result,
    }

    if secret_menu_chunk:
        return_state["secret_menu"] = secret_menu_chunk

    return return_state


def judgement_secret_directory_node(state: State) -> State:
    """
    秘密目录判别节点：根据场景判断是否属于秘密目录

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    output("Agent秘密目录判别", state)

    secret_menu_chunk = state.get("secret_menu", {})
    doc_content = state.get("doc_content", "")

    try:
        if not secret_menu_chunk:
            logger.warning("未找到secret_menu chunk，无法进行秘密目录分析")
            secret_analysis_result = {
                "result": "未知",
                "confidence": 0,
                "evidence": "未找到检索到的秘密目录内容，无法进行匹配度分析",
            }
        else:
            logger.info(
                f"使用检索到的secret_menu chunk进行分析: chunk_id={secret_menu_chunk.get('chunk_id')}"
            )
            response = secret_menu_parse(secret_menu_chunk, doc_content)
            secret_analysis_result = response
            logger.info(f"秘密目录分析结果: {response}")
            print(response)

        return {
            "current_node": "judgement_secret_directory_node",
            "secret_analysis_result": secret_analysis_result,
        }

    except Exception as e:
        error_msg = f"秘密目录文件 JSON 解析失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return create_error_state(
            "judgement_secret_directory_node",
            error_msg,
            {
                "secret_analysis_result": {
                    "result": "错误",
                    "confidence": 0,
                    "evidence": error_msg,
                }
            },
        )


def judgement_public_content_node(state: State) -> State:
    """
    内容公开判别节点：判断内容是否可公开

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    output("Agent内容公开判别", state)

    doc_content = state.get("doc_content", "")

    try:
        response = public_judgement(doc_content)
        logger.info(f"公开性分析结果: {response}")
        print(response)

        return {
            "current_node": "judgement_public_content_node",
            "public_analysis_result": response,
        }
    except Exception as e:
        error_msg = f"公开性判别失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return create_error_state(
            "judgement_public_content_node",
            error_msg,
            {
                "public_analysis_result": {
                    "result": "错误",
                    "confidence": 0,
                    "evidence": error_msg,
                }
            },
        )


# ==================== LLM 节点（流式版本）====================


def decision_review_node(
    state: State, token_callback: Optional[Callable[[str], None]] = None
) -> State:
    """
    决策评审节点（流式版本）

    Args:
        state: 工作流状态
        token_callback: 可选的回调函数，用于处理每个 token

    Returns:
        更新后的状态
    """
    # 检查是否是秘标匹配的情况
    if is_secretlogo_match(state):
        logger.info(
            f"检测到秘标匹配，直接判定为涉密，跳过LLM分析。evidence: {state.get('evidence', '')[:100]}"
        )

        result = {
            "is_sensitive": True,
            "confidence": 100,
            "evidence": state.get("evidence", "检测到秘标，判定为涉密文件"),
        }
        result_json = json.dumps(result, ensure_ascii=False)

        print(f"{Fore.GREEN}✅ 秘标匹配成功，直接判定为涉密文件{Style.RESET_ALL}")
        print(result_json)

        if token_callback:
            for char in result_json:
                token_callback(char)

        return {
            "current_node": "decision_review_node",
            **result,
        }

    # 进行决策评审（LLM分析）
    secret_result = state.get("secret_analysis_result", {})
    public_result = state.get("public_analysis_result", {})

    secret_result_str = (
        json.dumps(secret_result, ensure_ascii=False)
        if isinstance(secret_result, dict)
        else str(secret_result)
    )
    public_result_str = (
        json.dumps(public_result, ensure_ascii=False)
        if isinstance(public_result, dict)
        else str(public_result)
    )

    result_state, _ = _process_llm_node(
        state=state,
        node_name="决策评审智能体",
        prompt_template=get_decision_review_prompt(),
        input_data={
            "secret_analysis_result": secret_result_str,
            "public_analysis_result": public_result_str,
        },
        default_result={
            "is_sensitive": False,
            "confidence": 0,
            "evidence": "决策评审解析失败",
        },
        token_callback=token_callback,
        update_evidence=False,
    )
    return result_state


def secret_analysis_node(
    state: State, token_callback: Optional[Callable[[str], None]] = None
) -> State:
    """
    正向涉密分析节点（流式版本）

    Args:
        state: 工作流状态
        token_callback: 可选的回调函数，用于处理每个 token

    Returns:
        更新后的状态
    """
    result_state, response_json = _process_llm_node(
        state=state,
        node_name="正向涉密分析",
        prompt_template=get_secret_analysis_prompt(),
        input_data=state,
        default_result={
            "result": "非涉密",
            "confidence": 0,
            "evidence": "JSON 解析失败",
        },
        token_callback=token_callback,
        update_evidence=True,
    )

    # 将结果包装到 secret_analysis_result 字段，使用原始响应中的 evidence
    result = response_json.get("result")
    if result is not None:
        result_state["secret_analysis_result"] = {
            "result": result,
            "confidence": response_json.get("confidence", 0),
            "evidence": response_json.get("evidence", ""),
        }
        # 移除临时字段
        result_state.pop("result", None)
        result_state.pop("confidence", None)
        # evidence 字段保留（已更新为证据链）

    return result_state


def public_analysis_node(
    state: State, token_callback: Optional[Callable[[str], None]] = None
) -> State:
    """
    反向非涉密分析节点（流式版本）

    Args:
        state: 工作流状态
        token_callback: 可选的回调函数，用于处理每个 token

    Returns:
        更新后的状态
    """
    result_state, response_json = _process_llm_node(
        state=state,
        node_name="反向非涉密分析",
        prompt_template=get_public_analysis_prompt(),
        input_data=state,
        default_result={
            "result": "非公开",
            "confidence": 0,
            "evidence": "JSON 解析失败",
        },
        token_callback=token_callback,
        update_evidence=True,
    )

    # 将结果包装到 public_analysis_result 字段，使用原始响应中的 evidence
    result = response_json.get("result")
    if result is not None:
        result_state["public_analysis_result"] = {
            "result": result,
            "confidence": response_json.get("confidence", 0),
            "evidence": response_json.get("evidence", ""),
        }
        # 移除临时字段
        result_state.pop("result", None)
        result_state.pop("confidence", None)
        # evidence 字段保留（已更新为证据链）

    return result_state
