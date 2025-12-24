from typing import TypedDict
from nodes import (
    start_node,
    hard_condition_node,
    secret_analysis_node,
    public_analysis_node,
    decision_review_node,
)
from langgraph.graph import StateGraph, END


# 定义工作流状态
class State(TypedDict):
    doc_title: str  # 文档标题
    doc_content: str  # 文档内容
    current_node: str  # 当前节点（用于路由）
    is_sensitive: bool  # 是否涉密
    evidence: str  # 证据链
    secret_analysis_result: dict  # 语义检测结果
    public_analysis_result: dict  # 非涉密证明结果
    confidence: int  # 置信度


# 如果关键词检测到涉密内容，直接进入决策节点；否则，继续语义检测
def route_after_hard_condition(state: State):
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
workflow.add_node("hard_condition_node", hard_condition_node)
workflow.add_node("agent_semantics", secret_analysis_node)
workflow.add_node("agent_non_secret_proof", public_analysis_node)
workflow.add_node("agent_decision", decision_review_node)

# 设定启动节点
workflow.set_entry_point("start_node")

# 第一步：硬条件检测（关键词、短语）
# 关键词检测：正则匹配
# 短语检测：语义相似度匹配
# 如果检测到关键词或短语，直接进入判定为涉密文件进入复查阶段
# 否则，进行深度分析
workflow.add_edge("start_node", "hard_condition_node")

# 第二步：关键词检测后的条件路由
workflow.add_conditional_edges(
    "hard_condition_node",
    route_after_hard_condition,
    {
        "agent_decision": "agent_decision",  # 如果检测到关键词，直接决策
        "agent_semantics": "agent_semantics",  # 否则继续语义检测
    },
)

workflow.add_edge("agent_semantics", "agent_non_secret_proof")
workflow.add_edge("agent_non_secret_proof", "agent_decision")
workflow.add_edge("agent_decision", END)

# 编译工作流
app = workflow.compile()
