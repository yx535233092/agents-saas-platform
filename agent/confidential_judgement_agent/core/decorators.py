"""装饰器模块"""

import functools
import logging
from typing import Callable, Any
from time import time

from confidential_judgement_agent.core.exceptions import NodeExecutionError
from confidential_judgement_agent.workflow.state import State

logger = logging.getLogger(__name__)


def node_error_handler(node_name: str = None):
    """
    节点错误处理装饰器
    
    Args:
        node_name: 节点名称，如果不提供则从函数名获取
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(state: State, *args, **kwargs) -> State:
            name = node_name or func.__name__
            try:
                return func(state, *args, **kwargs)
            except Exception as e:
                logger.error(f"节点 {name} 执行失败: {str(e)}", exc_info=True)
                raise NodeExecutionError(
                    node_name=name,
                    message=str(e),
                    details={"error_type": type(e).__name__}
                )
        return wrapper
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """
    记录函数执行时间的装饰器
    
    Args:
        func: 要装饰的函数
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time()
        try:
            result = func(*args, **kwargs)
            execution_time = time() - start_time
            logger.debug(f"{func.__name__} 执行时间: {execution_time:.3f}秒")
            return result
        except Exception as e:
            execution_time = time() - start_time
            logger.error(f"{func.__name__} 执行失败 (耗时 {execution_time:.3f}秒): {str(e)}")
            raise
    return wrapper


def validate_state(required_fields: list = None):
    """
    验证状态的装饰器
    
    Args:
        required_fields: 必需的状态字段列表
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(state: State, *args, **kwargs) -> State:
            if required_fields:
                missing_fields = [field for field in required_fields if field not in state]
                if missing_fields:
                    from confidential_judgement_agent.core.exceptions import ValidationError
                    raise ValidationError(
                        field="state",
                        message=f"缺少必需字段: {', '.join(missing_fields)}"
                    )
            return func(state, *args, **kwargs)
        return wrapper
    return decorator

