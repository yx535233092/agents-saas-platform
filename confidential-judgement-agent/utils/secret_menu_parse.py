from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os


# 秘密目录LLM判别
def secret_menu_parse(scene, doc_content):
    llm = ChatOpenAI(
        model=os.getenv("MODEL"),
        base_url="https://api.siliconflow.cn/v1",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        temperature=0,
    )

    scene_describe_detail = ""
    for item in scene:
        scene_describe_detail += (
            f"{item['secret_menu_name']}: {item['secret_menu_description']}\n"
        )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                ### 用户提供的文件内容
                {doc_content}
                ### 场景描述
                请根据以下场景描述，判断用户提供的文件内容是否属于下属场景之一：
                {scene_describe_detail}
                ### 推理逻辑（Chain of Thought）
                在给出最终判断前，请按以下步骤在内部进行逻辑推演：
                1. **关键词提取**：识别文件中的核心实体、动作、机构名称及特有术语。
                2. **场景映射**：对比文件内容与场景定义中的关键特征（如：是否涉及事故等级、是否包含特定行政部署、是否涉及特定技术参数）。
                3. **隐晦关联分析**：分析文本中是否存在代号、不公开的内部流程或对重大敏感事件的侧面描述。
                4. **风险定性**：基于上述分析，判断该内容泄露后是否符合场景描述中的风险特征。

                ### 输出要求
                请以纯json文本格式输出，严格遵守格式,不要输出任何注释或额外字符,确保可解析：
                {{
                    "result": 是否属于该场景(true/false),
                    "confidence": 判断置信度(0-100),
                    "evidence": 思维链
                }}
                """,
            )
        ]
    )
    chain = prompt | llm
    response = chain.invoke(
        {"doc_content": doc_content, "scene_describe_detail": scene_describe_detail}
    ).content
    return response
