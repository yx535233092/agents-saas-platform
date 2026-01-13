"""LLM 工厂类 - 统一管理 LLM 实例，避免重复创建"""

from typing import Optional
from langchain_openai import ChatOpenAI
from confidential_judgement_agent.config import get_settings

_settings = get_settings()
_llm_instance: Optional[ChatOpenAI] = None


def get_llm(streaming: bool = True) -> ChatOpenAI:
    """
    获取 LLM 实例（单例模式）

    Args:
        streaming: 是否启用流式输出

    Returns:
        ChatOpenAI 实例
    """
    global _llm_instance

    # 如果已存在实例且 streaming 参数匹配，直接返回
    if _llm_instance is not None:
        # 注意：这里简化处理，实际可能需要根据 streaming 参数创建不同实例
        return _llm_instance

    _llm_instance = ChatOpenAI(
        model=_settings.MODEL,
        base_url=_settings.LLM_BASE_URL,
        api_key=_settings.SILICONFLOW_API_KEY,
        temperature=_settings.LLM_TEMPERATURE,
        streaming=streaming,
    )

    return _llm_instance


def reset_llm():
    """重置 LLM 实例（主要用于测试）"""
    global _llm_instance
    _llm_instance = None
