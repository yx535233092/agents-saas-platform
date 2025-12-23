import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from colorama import Fore, Style
from dotenv import load_dotenv
import os
from utils.output import output

load_dotenv()
current_dir = os.path.dirname(os.path.abspath(__file__))


# 开始节点
def start_node(state):
    # 初始化参数
    state.update({"current_node": "start_node", "is_sensitive": False, "evidence": ""})
    # 去除换行符和空格
    content = state["doc_content"].replace("\n", " ").replace(" ", "")
    state.update({"doc_content": content})
    output("start_node", state, is_first=True)
    return state


# 硬条件检测节点
def hard_condition_node(state):
    output("Agent硬性条件检测(关键词、短语)", state)
    state.update({"current_node": "hard_condition_node"})
    # 1. 关键词正则匹配
    with open(
        os.path.join(current_dir, "static/keywords.json"), "r", encoding="utf-8"
    ) as f:
        keywords = json.load(f)
        for category in keywords:
            for keyword in keywords[category]:
                if re.search(rf"{keyword}", state["doc_content"]):
                    state.update({"is_sensitive": True})
                    state.update(
                        {
                            "evidence": f"节点{state['current_node']}证据：涉密关键词匹配成功，直接判定为涉密文件，关键词：{keyword}"
                        }
                    )
                    return state
                else:
                    continue

    # 2. 短语正则匹配分析
    with open(
        os.path.join(current_dir, "static/short_sentence.json"), "r", encoding="utf-8"
    ) as f:
        short_sentences = json.load(f)
        for category in short_sentences:
            for short_sentence in short_sentences[category]:
                if re.search(
                    rf"{short_sentence}",
                    state["doc_content"],
                ):
                    state.update({"is_sensitive": True})
                    state.update(
                        {
                            "evidence": f"节点{state['current_node']}证据：涉密短语匹配成功，直接判定为涉密文件，短语：{short_sentence}"
                        }
                    )
                    return state
                else:
                    continue
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


# 决策评审节点
def decision_review_node(state):
    output("Agent决策评审智能体", state)
    # 如果硬性条件检测成功，直接判定为涉密文件
    if state["is_sensitive"] and state["current_node"] == "hard_condition_node":
        result = {
            "is_sensitive": state["is_sensitive"],
            "confidence": 100,
            "evidence": state["evidence"],
        }
        result_json = json.dumps(result, ensure_ascii=False)
        print(result_json)
        return state
    # 更新当前节点为决策评审节点
    state.update({"current_node": "decision_review_node"})

    llm = ChatOpenAI(
        model=os.getenv("MODEL"),
        base_url="https://api.siliconflow.cn/v1",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        temperature=0,
    )
    public_analysis_result = state["public_analysis_result"]
    secret_analysis_result = state["secret_analysis_result"]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                *角色设定*:
                你是一名专业的涉密文件决策评审专家。

                *任务设定*:
                你的任务是根据关键词匹配、语义推断和非涉密证明的结果，结合预设的权重，执行加权平均计算和逻辑校验，最终给出关于文本是否涉密的聚合判断，输出证据链和置信度。
                
                *判断条件*
                1. 正向涉密研判为”涉密“且置信度大于90
                2. 反向非涉密研判为”非公开“且置信度大于90
                3. 正向涉密研判权重为70，反向涉密研判权重为30
                4. 根据正向与反向提供的证据链，总结输出判断依据和完整证据链

                *输入数据*
                {secret_analysis_result}
                {public_analysis_result}

                *输出格式*:
                输出必须严格为如下格式，严格以纯json格式输出,确保可解析，不允许输出任何注释或额外字符
                {{
                "is_sensitive": true | false,
                "evidence": "文本内容为\'超级国家组建方式：通过召集多个超级大脑任务\'，未发现任何与政务领域涉密、敏感或未公开信息相关的措辞或隐晦指代。文本内容较为抽象，不涉及具体的人事任免、高层会议讨论、政策草案、关键基础设施位置、网络安全应急响应流程、敏感调查对象身份、政府采购底价或未公开财政资金流向等敏感信息。同时，文本内容未发现任何直接或隐晦的涉密关键词，如\'涉密\'、\'机密\'、\'内部\'、\'底价\'、\'未公开\'、\'敏感人员\'等。文本内容较为抽象，没有具体指向任何敏感信息或内部事务。",
                "confidence": 0-100,
                }}
                """,
            )
        ]
    )

    chain = prompt | llm
    response = chain.invoke(state)
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


# 决策评审智能体（流式版本，用于 API）
def agent_decision_stream(state, stream_callback=None):
    """
    流式版本的决策评审智能体，支持回调函数实时输出 token
    stream_callback: 可选的回调函数，每次收到 token 时调用
    """
    print(
        f"{Fore.MAGENTA}{Style.BRIGHT}开始执行: Agent决策评审智能体（流式）{Style.RESET_ALL}"
    )

    # 关键词关联判断为true并且置信度大于90直接判定为涉密文件
    if (
        state.get("agent_keyword_result") == True
        and state.get("agent_keyword_confidence", 0) > 90
    ):
        result_detail = (
            "关键词检测结果为涉密，置信度为"
            + str(state["agent_keyword_confidence"])
            + "，最终判定为涉密"
        )
        result_confidence = state["agent_keyword_confidence"]

        # 如果提供了流式回调，分段发送结果
        if stream_callback:
            for char in result_detail:
                stream_callback(char)

        print(result_detail)

        return {
            "result": True,
            "result_detail": result_detail,
            "result_confidence": result_confidence,
            "current_node": "END",
        }
    else:
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
      你是一名高权限的信息安全决策模块。

      *任务设定*:
      你的任务是接收来自三个独立分析系统（系统一：关键词匹配；系统二：深层语义推断；系统三：非涉密证明）的详细报告。
      你必须根据报告中提供的结果、置信度、证据链，结合预设的权重，执行加权平均计算和逻辑校验，最终给出关于文本是否涉密的聚合判断。
      【聚合判断权重】:
      关键词匹配分析 (M1) 权重： 40%
      深层语义分析 (M2) 权重： 30%
      非涉密证明 (M3) 权重： 30%

      *输出格式*:
      严格以纯json格式输出,确保可解析，不允许输出任何注释或额外字符
      例子：
      {{
        "result": True | False, // 最终裁决结果 True为涉密，False为非涉密
        "result_confidence": [判断最终结果置信度]
        "result_detail": [评审结果分析报告]
      1. 关键词匹配分析：[分析报告]
      2. 语义推断分析：[分析报告]
      3. 非涉密证明分析：[分析报告]
      4. 最终裁决：
      [判断结果：涉密/非涉密]
      决策路径与依据：
      判定依据： [说明最终判定是满足了哪一条或哪几条规则（规则 1 / 规则 2 / 规则 3），或者三条规则均未满足。]
      规则 1 (关键词匹配) 检查结果： [满足/不满足]
      规则 2 (语义推断) 检查结果： [满足/不满足]
      规则 3 (非涉密证明) 检查结果： [满足/不满足]
      }}

      *输入数据*
      关键字匹配结果：{agent_keyword_result}
      关键字匹配置信度：{agent_keyword_confidence}
      关键字匹配证据：{agent_keyword_detail}
      语义推断结果：{agent_semantics_result}
      语义推断置信度：{agent_semantics_confidence}
      语义推断证据：{agent_semantics_detail}
      非涉密证明结果：{agent_non_secret_proof_result}
      非涉密证明置信度：{agent_non_secret_proof_confidence}
      非涉密证明证据：{agent_non_secret_proof_detail}
      """,
                )
            ]
        )

        chain = prompt | llm
        response = chain.stream(state)
        full_response = ""

        for event in response:
            token = event.content
            full_response += token
            print(token, end="", flush=True)

            # 如果提供了回调函数，调用它
            if stream_callback:
                stream_callback(token)

        print("\n")

        # 尝试解析 JSON
        try:
            # 清理响应内容
            content = full_response.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # 移除注释
            lines = content.split("\n")
            cleaned_lines = []
            for line in lines:
                if "//" in line:
                    comment_pos = line.find("//")
                    cleaned_lines.append(line[:comment_pos].rstrip())
                else:
                    cleaned_lines.append(line)
            content = "\n".join(cleaned_lines)

            response_json = json.loads(content)

            # 确保 result 是布尔值
            if isinstance(response_json.get("result"), str):
                response_json["result"] = response_json["result"].lower() in [
                    "true",
                    "yes",
                    "1",
                ]

            return {
                "result": response_json["result"],
                "result_detail": str(response_json.get("result_detail", "")),
                "result_confidence": int(response_json.get("result_confidence", 0)),
                "current_node": "END",
            }
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}JSON 解析失败: {str(e)}{Style.RESET_ALL}")
            return {
                "result": False,
                "result_detail": f"解析失败: {str(e)}\n原始响应: {full_response}",
                "result_confidence": 0,
                "current_node": "END",
            }
        except Exception as e:
            print(f"{Fore.RED}处理响应时出错: {str(e)}{Style.RESET_ALL}")
            return {
                "result": False,
                "result_detail": f"处理错误: {str(e)}",
                "result_confidence": 0,
                "current_node": "END",
            }
