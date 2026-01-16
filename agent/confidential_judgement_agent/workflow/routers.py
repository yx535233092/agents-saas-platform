"""工作流路由函数 - 工程化版本"""

from confidential_judgement_agent.workflow.state import State
from confidential_judgement_agent.core.logger import logger


def route_after_secretlogo(state: State) -> str:
    """
    秘标检测后的路由函数
    
    如果检测到秘标，直接进入决策节点；否则继续深度语义检测流程。

    Args:
        state: 工作流状态

    Returns:
        下一个节点的名称
    """
    is_sensitive = state.get("is_sensitive", False)

    if is_sensitive:
        logger.info("检测到秘标，直接进入决策节点")
        return "agent_decision"

    logger.info("未检测到秘标，继续深度语义检测流程")
    return "judgement_scene_node"


def route_after_semantics(state: State) -> str:
    """
    语义分析后的路由函数（可选，用于更复杂的路由逻辑）

    Args:
        state: 工作流状态

    Returns:
        下一个节点的名称
    """
    # 可以根据分析结果决定是否跳过某些节点
    # 当前实现：总是进入公开性分析
    return "judgement_public_content_node"

