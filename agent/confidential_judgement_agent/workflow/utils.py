"""工作流工具函数模块"""

import json
import re
import logging
from typing import Dict, Any, Optional, Tuple
from colorama import Fore, Style

from confidential_judgement_agent.core.exceptions import AgentError
from confidential_judgement_agent.workflow.state import State

logger = logging.getLogger(__name__)


def safe_json_parse(json_str: str, default: Dict[str, Any]) -> Dict[str, Any]:
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


def update_evidence(state: State, node_name: str, evidence: str) -> str:
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


def is_secretlogo_match(state: State) -> bool:
    """
    检查是否是秘标匹配的情况

    Args:
        state: 工作流状态

    Returns:
        是否为秘标匹配
    """
    evidence = state.get("evidence", "")
    is_sensitive = state.get("is_sensitive", False)

    if not is_sensitive:
        return False

    secretlogo_indicators = ["秘标", "秘标匹配", "judgement_secretlogo_node", "秘标："]
    return any(indicator in evidence for indicator in secretlogo_indicators)


def create_error_state(
    node_name: str, error_msg: str, default_result: Optional[Dict[str, Any]] = None
) -> State:
    """
    创建错误状态

    Args:
        node_name: 节点名称
        error_msg: 错误信息
        default_result: 默认结果字典

    Returns:
        错误状态
    """
    state = {
        "current_node": node_name,
        "error": error_msg,
    }
    if default_result:
        state.update(default_result)
    return State(**state)


def clean_doc_content(content: str) -> str:
    """
    清洗文档内容

    Args:
        content: 原始文档内容

    Returns:
        清洗后的内容
    """
    # 去除换行符和多余空格
    content = content.replace("\n", " ").strip()
    # 合并多个连续空格为单个空格
    content = re.sub(r"\s+", " ", content)
    return content


def extract_chunk_content(chunk: Dict[str, Any]) -> str:
    """
    从 chunk 中提取内容

    Args:
        chunk: chunk 字典

    Returns:
        提取的内容
    """
    content = (
        chunk.get("content_with_weight", "")
        or chunk.get("highlight", "")
        or chunk.get("content_ltks", "")
    )
    if content:
        # 移除HTML标签
        content = re.sub(r"<[^>]+>", "", content)
    return content
