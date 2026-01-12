try:
    # Python < 3.12 需使用 typing_extensions.TypedDict 以兼容 Pydantic v2
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict
from nodes import (
    start_node,
    secret_analysis_node,
    public_analysis_node,
    decision_review_node,
    judgement_secretlogo_node,
    judgement_scene_node,
    judgement_secret_directory_node,
    judgement_public_content_node,
)
from langgraph.graph import StateGraph, END


# 定义工作流状态
class State(TypedDict):
    current_node: str  # 当前节点（用于路由）
    doc_title: str  # 文件名
    doc_content: str  # 摘要
    scene: str  # 场景
    is_sensitive: bool  # 是否涉密
    evidence: str  # 证据链
    secret_analysis_result: dict  # 秘密目录分析结果
    public_analysis_result: dict  # 公开文件分析结果
    confidence: int  # 置信度


# 如果关键词检测到涉密内容，直接进入决策节点；否则，继续语义检测
def route_after_secretlogo(state: State):
    is_sensitive = state.get("is_sensitive")
    # 如果涉密，直接进入决策节点
    if is_sensitive:
        return "agent_decision"
    # 否则，继续深度语义检测
    else:
        return "agent_semantics"


# 工作流
workflow = StateGraph(State)
workflow.add_node("start_node", start_node)
workflow.add_node("judgement_scene_node", judgement_scene_node)
workflow.add_node("judgement_secret_directory_node", judgement_secret_directory_node)
workflow.add_node("judgement_public_content_node", judgement_public_content_node)

workflow.add_node("agent_semantics", secret_analysis_node)
workflow.add_node("agent_non_secret_proof", public_analysis_node)
workflow.add_node("agent_decision", decision_review_node)
workflow.add_node("judgement_secretlogo_node", judgement_secretlogo_node)
# 设定启动节点
workflow.set_entry_point("start_node")

# 第一步：秘标检测
# workflow.add_edge("start_node", "judgement_secretlogo_node")
# # 第二步：秘标检测后的条件路由
# workflow.add_conditional_edges(
#     "judgement_secretlogo_node",
#     route_after_secretlogo,
#     {
#         "agent_decision": "agent_decision",  # 如果检测到秘标，直接决策
#         "agent_semantics": "agent_semantics",  # 否则继续深度语义检测
#     },
# )
# # 第三步：深度语义检测
# workflow.add_edge("agent_semantics", "agent_non_secret_proof")
# # 第四步：非涉密证明
# workflow.add_edge("agent_non_secret_proof", "agent_decision")
# # 第五步：决策评审
# workflow.add_edge("agent_decision", END)

workflow.add_edge("start_node", "judgement_scene_node")
workflow.add_edge("judgement_scene_node", "judgement_secret_directory_node")
workflow.add_edge("judgement_secret_directory_node", "judgement_public_content_node")
workflow.add_edge("judgement_public_content_node", "agent_decision")
workflow.add_edge("agent_decision", END)

# 编译工作流
app = workflow.compile()
