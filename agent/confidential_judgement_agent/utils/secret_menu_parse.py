"""秘密目录解析工具"""

import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from confidential_judgement_agent.config import get_settings

settings = get_settings()


def secret_menu_parse(secret_menu_chunk: dict, doc_content: str):
    """
    使用API检索返回的秘密目录内容对文本内容和秘密目录匹配度进行深度分析

    Args:
        secret_menu_chunk: 从检索接口返回的相似度最高的chunk（字典格式）
        doc_content: 文档内容

    Returns:
        判别结果（JSON字符串）
    """
    llm = ChatOpenAI(
        model=settings.MODEL,
        base_url=settings.LLM_BASE_URL,
        api_key=settings.SILICONFLOW_API_KEY,
        temperature=settings.LLM_TEMPERATURE,
    )

    # 从secret_menu chunk中提取相关内容
    # 优先使用 content_with_weight，其次使用 highlight，最后使用 content_ltks
    secret_menu_content = (
        secret_menu_chunk.get("content_with_weight", "")
        or secret_menu_chunk.get("highlight", "")
        or secret_menu_chunk.get("content_ltks", "")
    )

    # 移除HTML标签（如<em>标签）
    secret_menu_content_clean = re.sub(r"<[^>]+>", "", secret_menu_content)

    # 获取其他有用信息
    similarity = secret_menu_chunk.get("similarity", 0)
    chunk_id = secret_menu_chunk.get("chunk_id", "")
    doc_name = secret_menu_chunk.get("docnm_kwd", "")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                ### 用户提供的文件内容
                {doc_content}
                
                ### 检索到的秘密目录内容（相似度: {similarity:.4f}）
                这是从知识库中检索到的与文档内容最相关的秘密目录条目：
                {secret_menu_content}
                
                来源文档: {doc_name}
                Chunk ID: {chunk_id}
                
                ### 分析任务
                请对用户提供的文件内容与检索到的秘密目录内容进行深度匹配度分析。
                
                ### 推理逻辑（Chain of Thought）
                在给出最终判断前，请按以下步骤进行详细分析：
                
                1. **语义相似度分析**：
                   - 分析文档内容与秘密目录内容在语义层面的相似程度
                   - 识别共同的关键词、概念、主题
                   - 评估两者在业务领域、技术领域或政策领域的关联性
                
                2. **内容匹配度评估**：
                   - 对比文档内容是否涉及秘密目录中描述的具体事项
                   - 分析文档内容是否包含秘密目录中提到的关键信息点
                   - 评估文档内容与秘密目录内容的匹配程度（完全匹配/部分匹配/不匹配）
                
                3. **敏感度判断**：
                   - 基于匹配度分析，判断文档内容是否属于该秘密目录范畴
                   - 评估文档内容泄露后可能造成的风险等级
                   - 考虑内容的敏感性、重要性、影响范围等因素
                
                4. **证据链构建**：
                   - 详细说明匹配的关键点
                   - 指出文档内容与秘密目录内容的具体关联
                   - 提供判断依据和推理过程
                
                ### 输出要求
                请以纯json文本格式输出，严格遵守格式,不要输出任何注释或额外字符,确保可解析：
                {{
                    "result": 是否属于该秘密目录(true/false),
                    "confidence": 判断置信度(0-100),
                    "match_score": 内容匹配度评分(0-100),
                    "evidence": 详细的思维链和匹配分析过程,
                    "key_matches": ["匹配点1", "匹配点2", ...],
                    "risk_level": 风险等级(高/中/低)
                }}
                """,
            )
        ]
    )
    chain = prompt | llm
    response = chain.invoke(
        {
            "doc_content": doc_content,
            "secret_menu_content": secret_menu_content_clean,
            "similarity": similarity,
            "doc_name": doc_name,
            "chunk_id": chunk_id,
        }
    ).content
    return response
