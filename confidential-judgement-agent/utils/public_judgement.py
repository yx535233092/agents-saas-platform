from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os


def public_judgement(doc_content):
    llm = ChatOpenAI(
        model=os.getenv("MODEL"),
        base_url="https://api.siliconflow.cn/v1",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        temperature=0,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                # 角色
                你是一名资深的【政府信息公开核查员】及【保密安全审计专家】，擅长通过文本特征识别公文的密级与公开属性。

                # 背景
                我需要你审核一段文本内容，判断其是否属于“可直接向社会公开”的文件。原始数据可能来自内部数据库或抓取的零散文档，可能存在格式残缺。

                # 任务
                根据【待审文本】，严格按照思维链步骤，判定该文件是“公开文件”还是“非公开/内部/涉密文件”。

                # 推理步骤
                在给出结论前，请在内部按以下路径进行分析，并记录在 evidence 字段中：
                1. **文号与标识检索**：检查是否有“公报”、“公告”、“通知”、“第[X]号”等典型公开文号；检查是否有“绝密”、“机密”、“秘密”或“内部资料”等字样。
                2. **发布主体与渠道分析**：识别落款单位。该单位是否常态化向社会发布此类信息？文中是否提到“现予公布”、“欢迎监督”等面向公众的措辞？
                3. **内容敏感度评估**：内容是否涉及国家秘密、军事部署、未经授权的事故调查过程（非结果）、体制改革内情等敏感领域。
                4. **公开性推定**：如果文中包含明确的执行日期、面向不特定公众的指令、或已在政府公报刊登的引用，则倾向于判断为公开。

                # 约束
                - 必须识别隐晦特征（如：虽然没有密标，但涉及“不准外传”等要求的视为非公开）。
                - 输出必须是严格的 JSON 格式，方便后端程序解析。

                # 格式要求
                请以纯json文本格式输出，严格遵守格式,不要输出任何注释或额外字符,确保可解析
                {{
                  "is_public": true/false, // true 表示是公开文件，false 表示非公开或私密文件
                  "confidence": 0-100, // 置信度，范围 0-100
                  "evidence": "这里展示你的思维链推导过程，涵盖上述4个步骤的分析"
                }}

                # 变量注入
                - 待审内容：{doc_content}
                """,
            )
        ]
    )
    chain = prompt | llm
    response = chain.invoke({"doc_content": doc_content}).content
    return response
