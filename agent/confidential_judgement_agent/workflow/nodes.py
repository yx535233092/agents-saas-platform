"""工作流节点定义"""

import json
import re
import logging
from typing import Optional, Callable, Dict, Any
from colorama import Fore, Style

from confidential_judgement_agent.config import get_settings
from confidential_judgement_agent.utils.output import output
from confidential_judgement_agent.utils.secret_menu_parse import secret_menu_parse
from confidential_judgement_agent.utils.public_judgement import public_judgement
from confidential_judgement_agent.workflow.state import State
from confidential_judgement_agent.workflow.prompts import (
    get_decision_review_prompt,
    get_secret_analysis_prompt,
    get_public_analysis_prompt,
)
from confidential_judgement_agent.workflow.llm_factory import get_llm

settings = get_settings()
logger = logging.getLogger(__name__)


def _safe_json_parse(json_str: str, default: Dict[str, Any]) -> Dict[str, Any]:
    """
    安全的 JSON 解析，带错误处理

    Args:
        json_str: JSON 字符串
        default: 解析失败时的默认值

    Returns:
        解析后的字典
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {str(e)}, 原始内容: {json_str[:200]}")
        print(f"{Fore.RED}JSON 解析失败: {str(e)}{Style.RESET_ALL}")
        return default


def _update_evidence(state: State, node_name: str, evidence: str) -> str:
    """
    更新证据链

    Args:
        state: 当前状态
        node_name: 节点名称
        evidence: 新证据

    Returns:
        更新后的证据链
    """
    existing_evidence = state.get("evidence", "")
    new_evidence = f"节点{node_name}证据：{evidence}"
    if existing_evidence:
        return f"{existing_evidence}\n{new_evidence}"
    return new_evidence


# ==================== 基础节点 ====================


def start_node(state: State) -> State:
    """
    开始节点：数据清洗和初始化

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    output("start_node", state, is_first=True)

    # 数据清洗：去除换行符和多余空格
    content = state.get("doc_content", "").replace("\n", " ").strip()
    # 合并多个连续空格为单个空格
    content = re.sub(r"\s+", " ", content)

    # 保留 doc_title 字段，确保后续节点可以访问
    return {
        "current_node": "start_node",
        "doc_title": state.get("doc_title", ""),  # 保留 doc_title
        "doc_content": content,
        "is_sensitive": False,
        "evidence": "",
        "error": "",
    }


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
            "evidence": _update_evidence(state, "judgement_secretlogo_node", evidence),
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

    # TODO: 实现真实的场景识别逻辑（可以使用 LLM 或规则引擎）
    # 当前为占位实现
    scene = "消防救援"  # 默认场景

    logger.info(f"识别场景: {scene}")
    print(f"当前场景: {scene}")

    return {
        "current_node": "judgement_scene_node",
        "scene": scene,
    }


def judgement_secret_directory_node(state: State) -> State:
    """
    秘密目录判别节点：根据场景判断是否属于秘密目录

    Args:
        state: 工作流状态

    Returns:
        更新后的状态
    """
    output("Agent秘密目录判别", state)

    scene = state.get("scene", "")
    doc_content = state.get("doc_content", "")
    secret_menu_path = settings.SECRET_MENU_PATH

    try:
        with open(secret_menu_path, "r", encoding="utf-8") as f:
            secret_menu = json.load(f)

        secret_analysis_result = {}
        scene_found = False

        for scene_item in secret_menu:
            if scene == scene_item.get("scene"):
                scene_found = True
                response = secret_menu_parse(
                    scene_item.get("secret_menu", []), doc_content
                )
                secret_analysis_result = response
                logger.info(f"秘密目录分析结果: {response}")
                print(response)
                break

        if not scene_found:
            logger.warning(f"未找到场景: {scene}")
            print("未找到场景")
            secret_analysis_result = {
                "result": "未知",
                "confidence": 0,
                "evidence": f"未找到场景 {scene} 对应的秘密目录配置",
            }

        return {
            "current_node": "judgement_secret_directory_node",
            "secret_analysis_result": secret_analysis_result,
        }

    except FileNotFoundError:
        error_msg = f"秘密目录文件不存在: {secret_menu_path}"
        logger.error(error_msg)
        return {
            "current_node": "judgement_secret_directory_node",
            "error": error_msg,
            "secret_analysis_result": {
                "result": "错误",
                "confidence": 0,
                "evidence": error_msg,
            },
        }
    except json.JSONDecodeError as e:
        error_msg = f"秘密目录文件 JSON 解析失败: {str(e)}"
        logger.error(error_msg)
        return {
            "current_node": "judgement_secret_directory_node",
            "error": error_msg,
            "secret_analysis_result": {
                "result": "错误",
                "confidence": 0,
                "evidence": error_msg,
            },
        }


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
        return {
            "current_node": "judgement_public_content_node",
            "error": error_msg,
            "public_analysis_result": {
                "result": "错误",
                "confidence": 0,
                "evidence": error_msg,
            },
        }


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
    output("Agent决策评审智能体", state)

    # 如果包含秘标，直接判定为涉密文件
    if (
        state.get("is_sensitive")
        and state.get("current_node") == "judgement_secretlogo_node"
    ):
        result = {
            "is_sensitive": True,
            "confidence": 100,
            "evidence": state.get("evidence", "检测到秘标，判定为涉密文件"),
        }
        result_json = json.dumps(result, ensure_ascii=False)
        print(result_json)

        if token_callback:
            for char in result_json:
                token_callback(char)

        return {
            "current_node": "decision_review_node",
            **result,
        }

    # 如果不包含秘标，则进行决策评审
    llm = get_llm(streaming=True)
    prompt = get_decision_review_prompt()
    chain = prompt | llm

    # 准备输入数据
    secret_result = state.get("secret_analysis_result", {})
    public_result = state.get("public_analysis_result", {})

    # 转换为 JSON 字符串（如果还不是字符串）
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

    # 流式处理响应
    full_response = ""
    try:
        for event in chain.stream(
            {
                "secret_analysis_result": secret_result_str,
                "public_analysis_result": public_result_str,
            }
        ):
            token = event.content
            full_response += token
            if token_callback:
                token_callback(token)

        print(full_response)

        # 解析响应
        default_result = {
            "is_sensitive": False,
            "confidence": 0,
            "evidence": "决策评审解析失败",
        }
        response_json = _safe_json_parse(full_response, default_result)

        return {
            "current_node": "decision_review_node",
            "is_sensitive": response_json.get("is_sensitive", False),
            "evidence": response_json.get("evidence", ""),
            "confidence": response_json.get("confidence", 0),
        }

    except Exception as e:
        error_msg = f"决策评审失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "current_node": "decision_review_node",
            "error": error_msg,
            "is_sensitive": False,
            "confidence": 0,
            "evidence": error_msg,
        }


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
    output("Agent正向涉密分析", state)

    llm = get_llm(streaming=True)
    prompt = get_secret_analysis_prompt()
    chain = prompt | llm

    full_response = ""
    try:
        # 流式处理响应
        for event in chain.stream(state):
            token = event.content
            full_response += token
            if token_callback:
                token_callback(token)

        # 解析响应
        default_result = {
            "result": "非涉密",
            "confidence": 0,
            "evidence": "JSON 解析失败",
        }
        response_json = _safe_json_parse(full_response, default_result)

        evidence = _update_evidence(
            state, "secret_analysis_node", response_json.get("evidence", "")
        )

        return {
            "current_node": "secret_analysis_node",
            "secret_analysis_result": response_json,
            "evidence": evidence,
        }

    except Exception as e:
        error_msg = f"正向涉密分析失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "current_node": "secret_analysis_node",
            "error": error_msg,
            "secret_analysis_result": {
                "result": "错误",
                "confidence": 0,
                "evidence": error_msg,
            },
        }


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
    output("Agent反向非涉密分析", state)

    llm = get_llm(streaming=True)
    prompt = get_public_analysis_prompt()
    chain = prompt | llm

    full_response = ""
    try:
        # 流式处理响应
        for event in chain.stream(state):
            token = event.content
            full_response += token
            if token_callback:
                token_callback(token)

        # 解析响应
        default_result = {
            "result": "非公开",
            "confidence": 0,
            "evidence": "JSON 解析失败",
        }
        response_json = _safe_json_parse(full_response, default_result)

        evidence = _update_evidence(
            state, "public_analysis_node", response_json.get("evidence", "")
        )

        return {
            "current_node": "public_analysis_node",
            "public_analysis_result": response_json,
            "evidence": evidence,
        }

    except Exception as e:
        error_msg = f"反向非涉密分析失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "current_node": "public_analysis_node",
            "error": error_msg,
            "public_analysis_result": {
                "result": "错误",
                "confidence": 0,
                "evidence": error_msg,
            },
        }
