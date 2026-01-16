"""工作流图定义 - 工程化版本"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from confidential_judgement_agent.core.logger import logger
from confidential_judgement_agent.workflow.state import State
from confidential_judgement_agent.workflow.routers import route_after_secretlogo
from confidential_judgement_agent.workflow.nodes import (
    start_node,
    secret_analysis_node,
    public_analysis_node,
    decision_review_node,
    judgement_secretlogo_node,
    judgement_scene_node,
    retrieve_secret_menu,
    judgement_secret_directory_node,
    judgement_public_content_node,
)


# ==================== 工作流图构建 ====================


def create_workflow(checkpoint: bool = False):
    """
    创建工作流图

    构建完整的涉密研判工作流，包括：
    1. 数据清洗和初始化
    2. 秘标识别
    3. 场景识别
    4. 秘密目录检索
    5. 秘密目录分析
    6. 公开性分析
    7. 决策评审

    Args:
        checkpoint: 是否启用检查点（用于状态持久化和恢复）

    Returns:
        编译后的工作流应用
    """
    logger.info("开始创建工作流图")

    # 创建状态图
    workflow = StateGraph(State)

    # 注册所有节点
    nodes = {
        "start_node": start_node,
        "judgement_secretlogo_node": judgement_secretlogo_node,
        "judgement_scene_node": judgement_scene_node,
        "retrieve_secret_menu": retrieve_secret_menu,
        "judgement_secret_directory_node": judgement_secret_directory_node,
        "judgement_public_content_node": judgement_public_content_node,
        "agent_semantics": secret_analysis_node,
        "agent_non_secret_proof": public_analysis_node,
        "agent_decision": decision_review_node,
    }

    for node_name, node_func in nodes.items():
        workflow.add_node(node_name, node_func)
        logger.debug(f"注册节点: {node_name}")

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
    workflow.add_edge("judgement_scene_node", "retrieve_secret_menu")
    workflow.add_edge("retrieve_secret_menu", "judgement_secret_directory_node")
    workflow.add_edge(
        "judgement_secret_directory_node", "judgement_public_content_node"
    )
    workflow.add_edge("judgement_public_content_node", "agent_decision")

    # 结束
    workflow.add_edge("agent_decision", END)

    # 编译工作流
    if checkpoint:
        logger.info("启用检查点模式")
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
    else:
        logger.info("使用无检查点模式")
        app = workflow.compile()

    logger.info("工作流图创建完成")
    return app


# 创建默认工作流实例（不启用检查点）
app = create_workflow(checkpoint=False)

# 如果需要启用检查点，可以这样创建：
# app_with_checkpoint = create_workflow(checkpoint=True)
