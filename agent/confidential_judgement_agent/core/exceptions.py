"""自定义异常类"""


class AgentError(Exception):
    """智能体基础异常类"""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NodeExecutionError(AgentError):
    """节点执行错误"""
    
    def __init__(self, node_name: str, message: str, details: dict = None):
        self.node_name = node_name
        super().__init__(f"节点 {node_name} 执行失败: {message}", details)


class LLMError(AgentError):
    """LLM 调用错误"""
    
    def __init__(self, message: str, model: str = None, details: dict = None):
        self.model = model
        super().__init__(f"LLM 调用失败: {message}", details)


class RetrievalError(AgentError):
    """检索服务错误"""
    
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        self.status_code = status_code
        super().__init__(f"检索服务失败: {message}", details)


class ValidationError(AgentError):
    """数据验证错误"""
    
    def __init__(self, field: str, message: str, details: dict = None):
        self.field = field
        super().__init__(f"字段 {field} 验证失败: {message}", details)

