import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from colorama import Fore, Style
from dotenv import load_dotenv
import os
from utils.output import output
from utils.secret_menu_parse import secret_menu_parse
from utils.public_judgement import public_judgement

load_dotenv()
current_dir = os.path.dirname(os.path.abspath(__file__))


# 开始节点（数据清洗）
def start_node(state):
    # 初始化参数
    state.update({"current_node": "start_node", "is_sensitive": False, "evidence": ""})
    # 去除换行符和空格
    content = state["doc_content"].replace("\n", " ").replace(" ", "")
    state.update({"doc_content": content})
    output("start_node", state, is_first=True)
    return state


# 秘标识别节点
def judgement_secretlogo_node(state):
    output("Agent秘标识别", state)
    # 更新节点
    state.update({"current_node": "judgement_secretlogo_node"})
    # 秘标识别
    pattern = r"(绝密|机密|秘密)\s*★\s*(\d+[年月]|长期|启封前|公开前)"
    match = re.search(pattern, state["doc_content"])
    if match:
        state.update(
            {
                "is_sensitive": True,
                "evidence": f"节点{state['current_node']}证据：秘标匹配成功，判定为涉密文件，秘标：{match.group()}",
            },
        )
    return state


# 场景识别节点
def judgement_scene_node(state):
    output("Agent场景识别", state)
    # 更新节点
    state.update({"current_node": "judgement_scene_node"})
    # TODO:场景识别
    state.update({"scene": "消防救援"})
    print("当前场景:", state["scene"])
    return state


# 秘密目录判别
def judgement_secret_directory_node(state):
    output("Agent秘密目录判别", state)
    # 更新节点
    state.update({"current_node": "judgement_secret_directory_node"})
    # 秘密目录判别
    secret_menu_path = os.path.join(current_dir, "static/secret_menu.json")
    with open(secret_menu_path, "r", encoding="utf-8") as f:
        secret_menu = json.load(f)
        for scene in secret_menu:
            if state["scene"] == scene["scene"]:
                response = secret_menu_parse(scene["secret_menu"], state["doc_content"])
                state.update({"secret_analysis_result": response})
                print(response)
            else:
                print("未找到场景")
    return state


# 内容公开判别
def judgement_public_content_node(state):
    output("Agent内容公开判别", state)
    # 更新节点
    state.update({"current_node": "judgement_public_content_node"})
    # 内容公开判别
    response = public_judgement(state["doc_content"])
    state.update({"public_analysis_result": response})
    print(response)
    return state


# 决策评审节点
def decision_review_node(state):
    output("Agent决策评审智能体", state)
    # 如果包含秘标，直接判定为涉密文件
    if state["is_sensitive"] and state["current_node"] == "judgement_secretlogo_node":
        result = {
            "is_sensitive": state["is_sensitive"],
            "confidence": 100,
            "evidence": state["evidence"],
        }
        result_json = json.dumps(result, ensure_ascii=False)
        print(result_json)
        return state
    # 如果不包含秘标，则进行决策评审
    state.update({"current_node": "decision_review_node"})

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
                # 角色设定:
                你是一名【首席安全合规审计官】，负责对下属提交的专项报告进行综合研判，并签署最终处理意见。

                # 背景
                现有两份关于同一份文件的分析报告：
                1. 《涉密性判别报告》：侧重于识别内容是否触及安全红线（权重 0.7）。
                2. 《公开性判别报告》：侧重于识别内容是否具备法律意义上的公开特征（权重 0.3）。

                # 任务
                请对比两份报告，解决其中的逻辑冲突，并根据“安全优先”原则给出最终结论。

                # 推理步骤
                1. **核对一致性**：两份报告在文件基本信息（如文号、主题）上是否指向同一实体？
                2. **冲突研判（核心）**：
                - 如果《涉密报告》指出存在核心敏感信息，而《公开报告》认为具备公开特征，必须分析是否为“违规公开”或“包含敏感附件的公开”。
                - **裁决准则**：只要涉及核心涉密点，公开特征一律视为无效或由于格式模仿导致的误判。
                3. **计算综合风险分**：
                - 最终得分 = (涉密报告分值 × 0.7) + (100 - 公开报告分值) × 0.3。
                4. **定性**：基于最终分值，判断该文件在系统中的分发级别。

                # 格式要求
                 输出必须严格为如下格式，严格以纯json格式输出,确保可解析，不允许输出任何注释或额外字符
                {{
                "is_sensitive": true | false,
                "evidence": "这里展示你的思维链推导过程，涵盖上述4个步骤的分析",
                "confidence": 0-100,
                }}

                # 变量注入
                - 涉密性判别报告：{secret_analysis_result}
                - 公开性判别报告：{public_analysis_result}
                """,
            )
        ]
    )

    chain = prompt | llm
    response = chain.invoke(
        {
            "secret_analysis_result": state["secret_analysis_result"],
            "public_analysis_result": state["public_analysis_result"],
        }
    )
    print(response.content)
    try:
        response_json = json.loads(response.content)
        state.update({"is_sensitive": response_json["is_sensitive"]})
        state.update({"evidence": response_json["evidence"]})
        state.update({"confidence": response_json["confidence"]})
        return state
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}JSON 解析失败: {str(e)}{Style.RESET_ALL}")
        return state


# 正向涉密分析节点
def secret_analysis_node(state):
    output("Agent正向涉密分析", state)
    # 大模型
    llm = ChatOpenAI(
        model=os.getenv("MODEL"),
        base_url="https://api.siliconflow.cn/v1",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        temperature=0,
    )
    # 提示词
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                *角色设定*:
                你是一名顶尖的信息安全与保密分析专家，专注于政务领域的文本分析。你的任务是根据完整的上下文语义、现有知识以及对政务工作流程的理解，深入分析用户提供的【待分析文本】。

                *任务设定*:
                1. 深度语义分析： 仔细阅读提供的文档摘要。
                2. 分析重点在于：
                该文本是否隐晦地或间接地提及了政务领域的涉密、敏感或未公开信息。
                评估文本中蕴含隐晦涉密信息的概率（Prevalence Probability）。
                对最终的涉密判断给出推断置信度（Inference Confidence）。
                3. 以纯json格式输出最终评定结果，严格遵守格式

                *敏感信息示例*
                【政务敏感信息知识库示例】:
                决策类： 尚未宣布的人事任免、高层会议的内部讨论意见、政策草案的具体条款。
                安全类： 关键基础设施的具体位置、网络安全应急响应的内部流程、敏感调查对象的身份。
                财务类： 政府采购或工程招投标的底价、未公开的财政资金流向。
                标识类： “内部参阅”、“机密文件”、“阅后即焚”、“非公开方案”等措辞。

                *格式设定*:
                1. json格式:
                请严格按照以下 JSON 格式 输出分析结果。所有数值（概率和置信度）都应为 0 到 100 之间的整数：
                {{ 
                result: 最终判断，必须是涉密或非涉密。
                confidence: 你对最终判断 (is_confidential) 的置信程度。（0-100）
                evidence: 具体的证据链。列出文本中的敏感措辞、隐晦指代以及推断依据（基于政务知识或常识）。
                }}
                2. *绝对*不允许出现```json ```这类输出，*必须*为纯JSON格式,必须*绝对*输出的结果是一个完整的、可解析的 JSON 对象。

                *待分析文本*: 
                {doc_content}

                *示例*
                {{
                "result": "涉密“,
                "confidence": 91,
                "evidence":  "'那个数字'——高度指代招投标中决定性的保密数字。'项目快要定了，等最后确认那个数字'——强烈暗示正在等待一个保密且关键的内部审批或底价确认。与【政务敏感信息知识库】中的'政府采购底价'高度关联。"
                }}
            """,
            )
        ]
    )

    chain = prompt | llm
    response = chain.invoke(state)
    try:
        response_json = json.loads(response.content)
        state.update({"secret_analysis_result": response_json})
        evidence = (
            state["evidence"]
            + f"节点{state['current_node']}证据：{response_json['evidence']}"
        )
        state.update({"evidence": evidence})
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}JSON 解析失败: {str(e)}{Style.RESET_ALL}")
        state.update(
            {
                "secret_analysis_result": {
                    "result": False,
                    "confidence": 0,
                    "evidence": "JSON 解析失败",
                }
            }
        )
    return state


# 反向非涉密分析节点
def public_analysis_node(state):
    output("Agent反向非涉密分析", state)
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
                    *角色设定*:
                    你是一名文件解密与公开审核专员。

                    *任务设定*:
                    你的核心任务是评估给定的【待分析文本】中不包含任何国家秘密、商业机密、敏感个人信息或任何需严格保密的政务信息的程度。
                    你的最终判断是文件是否应被标记为**“非涉密”或“公开”**。
                    你需要关注文本中是否存在任何与“涉密”、“机密”、“内部”、“底价”、“未公开”、“敏感人员”等关键词的直接关联或隐晦语义关联。

                    *输入内容*
                    {doc_content}

                    *输出格式*:
                    请严格按照以下 JSON 格式 输出分析结果，严格以纯json格式输出,确保可解析，不允许输出任何注释或额外字符：
                    result: 最终判断结果。必须是”公开“或”非公开“。
                    confidence: 你对最终判断 (is_non_confidential) 的置信程度。必须是 0 到 100 之间的整数。
                    evidence: 详细的证据链和分析过程。
                    如果结果为 ”公开“：列出支持非涉密判断的公开性特征（如：提及“已公开”、“征求意见”、“通用规范”等词汇），并说明未发现任何敏感关键词或隐晦涉密语义。
                    如果结果为 ”非公开“：列出导致文件不能被标记为非涉密的风险点（如：发现敏感关键词、检测到隐晦指代），并说明这些风险点如何影响文件公开性。

                    示例输出格式（结果为 ”公开“ - 确认非涉密）
                    {{
                    "result": "公开",
                    "confidence": 98,
                    "evidence": "文本多次提及 '公开征求意见' 和 '向社会公开'，明确表明其公开属性。内容聚焦于 '办事流程优化' 和 '服务时间延长'，属于常规的行政服务调整，不涉及高层决策或国家秘密。经敏感词库匹配和语义分析，未发现任何与'底价'、'机密'、'未宣布人事'或'内网地址'相关的直接或隐晦信息。"
                    }}

                    示例输出格式（结果为 ”非公开“ - 存在涉密风险）
                    {{
                    "result": "非公开",
                    "confidence": 85,
                    "evidence": "风险点：文本中出现了'内部参阅'的关键词，表明其在流转范围上有严格限制。语义风险：提到了'正在讨论的下一年度财政预算的数额'，虽然未给出确切的'草案'关键词，但其对未公开信息的提及具有潜在泄密风险。结论：由于存在明确的内部限定标识和对未公开经济数据的隐晦指代，该文件不能被确认为非涉密文件。"
                    }}
                """,
            )
        ]
    )

    chain = prompt | llm
    response = chain.invoke(state)
    try:
        response_json = json.loads(response.content)
        state.update({"public_analysis_result": response_json})
        evidence = (
            state["evidence"]
            + f"节点{state['current_node']}证据：{response_json['evidence']}"
        )
        state.update({"evidence": evidence})
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}JSON 解析失败: {str(e)}{Style.RESET_ALL}")
        state.update(
            {
                "public_analysis_result": {
                    "result": False,
                    "confidence": 0,
                    "evidence": "JSON 解析失败",
                }
            }
        )
    return state
