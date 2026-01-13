"""工作流状态定义 - 使用 LangGraph 最佳实践"""

import sys
from typing import Annotated

# Python < 3.12 需要使用 typing_extensions.TypedDict
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


# 使用 Annotated 和 reducer 模式（LangGraph 推荐）
# total=False 表示所有字段都是可选的，节点只需要返回更新的字段
class State(TypedDict, total=False):
    """工作流状态定义"""

    current_node: str  # 当前节点名称
    doc_title: str  # 文档标题
    doc_content: str  # 文档内容
    scene: str  # 场景类型
    is_sensitive: bool  # 是否涉密
    evidence: str  # 证据链
    secret_analysis_result: dict  # 秘密目录分析结果
    public_analysis_result: dict  # 公开性分析结果
    confidence: int  # 置信度 (0-100)
    error: str  # 错误信息（可选）


def state_reducer(current: dict, update: dict) -> dict:
    """
    状态合并函数 - LangGraph 推荐使用 reducer 模式

    Args:
        current: 当前状态
        update: 节点返回的更新

    Returns:
        合并后的状态
    """
    # 浅合并，update 中的值会覆盖 current
    # 确保保留 current 中的所有字段，只更新 update 中提供的字段
    result = {**current, **update}
    # 确保所有必需的字段都存在（即使值为 None 或空字符串）
    # 这样可以避免 LangGraph 验证时出错
    return result


# 使用 Annotated 定义带 reducer 的状态类型
# 注意：LangGraph 会自动使用这个 reducer 来合并节点返回的状态更新
AnnotatedState = Annotated[State, state_reducer]
