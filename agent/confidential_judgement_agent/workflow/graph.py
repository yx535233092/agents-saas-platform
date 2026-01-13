"""工作流图定义"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from confidential_judgement_agent.workflow.state import AnnotatedState
from confidential_judgement_agent.workflow.nodes import (
    start_node,
    secret_analysis_node,
    public_analysis_node,
    decision_review_node,
    judgement_secretlogo_node,
    judgement_scene_node,
    judgement_secret_directory_node,
    judgement_public_content_node,
)


# ==================== 路由函数 ====================


def route_after_secretlogo(state: AnnotatedState) -> str:
    """
    秘标检测后的路由函数

    Args:
        state: 工作流状态

    Returns:
        下一个节点的名称
    """
    is_sensitive = state.get("is_sensitive", False)

    # 如果检测到秘标，直接进入决策节点
    if is_sensitive:
        return "agent_decision"

    # 否则，继续深度语义检测流程
    return "judgement_scene_node"


def route_after_semantics(state: AnnotatedState) -> str:
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


# ==================== 工作流图构建 ====================


def create_workflow(checkpoint: bool = False):
    """
    创建工作流图

    Args:
        checkpoint: 是否启用检查点（用于状态持久化和恢复）

    Returns:
        编译后的工作流应用
    """
    # 创建状态图
    workflow = StateGraph(AnnotatedState)

    # 添加节点
    workflow.add_node("start_node", start_node)
    workflow.add_node("judgement_secretlogo_node", judgement_secretlogo_node)
    workflow.add_node("judgement_scene_node", judgement_scene_node)
    workflow.add_node(
        "judgement_secret_directory_node", judgement_secret_directory_node
    )
    workflow.add_node("judgement_public_content_node", judgement_public_content_node)
    workflow.add_node("agent_semantics", secret_analysis_node)
    workflow.add_node("agent_non_secret_proof", public_analysis_node)
    workflow.add_node("agent_decision", decision_review_node)

    # 设置入口点
    workflow.set_entry_point("start_node")

    # 添加边（线性流程）
    workflow.add_edge("start_node", "judgement_secretlogo_node")

    # 条件边：根据秘标检测结果路由
    workflow.add_conditional_edges(
        "judgement_secretlogo_node",
        route_after_secretlogo,
        {
            "agent_decision": "agent_decision",  # 检测到秘标，直接决策
            "judgement_scene_node": "judgement_scene_node",  # 未检测到，继续流程
        },
    )

    # 继续正常流程
    workflow.add_edge("judgement_scene_node", "judgement_secret_directory_node")
    workflow.add_edge(
        "judgement_secret_directory_node", "judgement_public_content_node"
    )
    workflow.add_edge("judgement_public_content_node", "agent_decision")

    # 结束
    workflow.add_edge("agent_decision", END)

    # 编译工作流
    if checkpoint:
        # 启用检查点（用于生产环境的状态持久化）
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
    else:
        # 不使用检查点（用于简单场景）
        app = workflow.compile()

    return app


# 创建默认工作流实例（不启用检查点）
app = create_workflow(checkpoint=False)

# 如果需要启用检查点，可以这样创建：
# app_with_checkpoint = create_workflow(checkpoint=True)
