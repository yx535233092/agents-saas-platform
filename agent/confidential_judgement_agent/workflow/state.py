"""工作流状态定义 - 工程化版本"""

import sys
from typing import Dict, Any

# Python < 3.12 需要使用 typing_extensions.TypedDict
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


# 使用 TypedDict 定义状态，LangGraph 会自动处理状态合并
# total=False 表示所有字段都是可选的，节点只需要返回更新的字段
class State(TypedDict, total=False):
    """工作流状态定义

    所有字段都是可选的，节点只需要返回更新的字段。
    LangGraph 会自动合并状态更新。
    """

    # 基础字段
    current_node: str  # 当前节点名称
    doc_title: str  # 文档标题
    doc_content: str  # 文档内容（清洗后）

    # 分析结果
    scene: str  # 场景类型
    is_sensitive: bool  # 是否涉密
    confidence: int  # 置信度 (0-100)
    evidence: str  # 证据链

    # 分析结果（结构化）
    secret_analysis_result: Dict[str, Any]  # 秘密目录分析结果
    public_analysis_result: Dict[str, Any]  # 公开性分析结果
    retrieval_result: Dict[str, Any]  # 检索结果
    secret_menu: Dict[str, Any]  # 相似度最高的chunk（来自检索接口）

    # 错误信息
    error: str  # 错误信息（可选）


def create_initial_state(doc_title: str, doc_content: str, **kwargs) -> State:
    """
    创建初始状态

    Args:
        doc_title: 文档标题
        doc_content: 文档内容
        **kwargs: 其他初始字段

    Returns:
        初始状态字典
    """
    return State(
        current_node="start_node",
        doc_title=doc_title,
        doc_content=doc_content,
        scene="",
        is_sensitive=False,
        evidence="",
        confidence=0,
        secret_analysis_result={},
        public_analysis_result={},
        retrieval_result={},
        **kwargs,
    )


def merge_state_updates(base_state: State, updates: Dict[str, Any]) -> State:
    """
    合并状态更新（LangGraph 会自动处理，此函数用于手动合并）

    Args:
        base_state: 基础状态
        updates: 更新字典

    Returns:
        合并后的状态
    """
    merged = {**base_state, **updates}
    return State(**merged)
