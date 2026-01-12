import json
import re


def format_to_json(text: str) -> str:
    """
    将包含JSON代码块的文本转换为纯JSON文本

    Args:
        text: 包含markdown代码块的文本，例如:
              ```json
              {
                "key": "value"
              }
              ```

    Returns:
        提取出的纯JSON文本字符串

    Examples:
        >>> text = "```json\\n{\\n  \"key\": \"value\"\\n}\\n```"
        >>> format_to_json(text)
        '{\\n  "key": "value"\\n}'
    """
    if not text or not isinstance(text, str):
        return ""

    # 去除首尾空白
    text = text.strip()

    # 方法1: 使用正则表达式匹配markdown代码块
    # 匹配 ```json ... ``` 或 ``` ... ``` 格式
    pattern = r"^```(?:json)?\s*\n(.*?)\n```\s*$"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        json_content = match.group(1)
        return json_content.strip()

    # 方法2: 如果没有匹配到代码块，尝试直接查找JSON对象/数组
    # 查找第一个 { 或 [ 到最后一个 } 或 ]
    json_pattern = r"\{.*\}|\[.*\]"
    match = re.search(json_pattern, text, re.DOTALL)

    if match:
        return match.group(0)

    # 如果都没有匹配到，返回原文本（可能是纯JSON）
    return text


def format_to_json_object(text: str) -> dict | list:
    """
    将包含JSON代码块的文本转换为Python对象（dict或list）

    Args:
        text: 包含markdown代码块的文本

    Returns:
        解析后的Python对象（dict或list）

    Raises:
        json.JSONDecodeError: 如果文本不是有效的JSON格式
    """
    json_text = format_to_json(text)
    return json.loads(json_text)


def format_to_json_pretty(
    text: str, indent: int = 2, ensure_ascii: bool = False
) -> str:
    """
    将包含JSON代码块的文本转换为格式化的JSON文本

    Args:
        text: 包含markdown代码块的文本
        indent: JSON缩进空格数，默认2
        ensure_ascii: 是否确保ASCII编码，默认False（保留中文）

    Returns:
        格式化的JSON文本字符串
    """
    json_obj = format_to_json_object(text)
    return json.dumps(json_obj, indent=indent, ensure_ascii=ensure_ascii)


if __name__ == "__main__":
    # 测试用例
    test_text = """```json
{
  "is_public": false,
  "confidence": 95,
  "evidence": "1. 文号与标识检索：待审文本中未发现"公报"、"公告"、"通知"、"第[X]号"等典型公开文号，也未发现"绝密"、"机密"、"秘密"或"内部资料"等字样。\\n2. 发布主体与渠道分析：待审文本未明确提及发布主体，且内容涉及特大暴力恐怖火灾事故，通常此类事故的详细处置情况总结不会直接向社会公开。\\n3. 内容敏感度评估：待审文本内容涉及特大暴力恐怖火灾事故的详细处置情况，包括暴恐分子的行动细节、救援难点分析以及现场群众的反应，这些信息属于敏感领域，不宜直接向社会公开。\\n4. 公开性推定：待审文本中未提及明确的执行日期或面向不特定公众的指令，且内容涉及未经授权的事故调查过程，因此倾向于判断为非公开文件。"
}
```"""

    print("原始文本:")
    print(test_text)
    print("\n" + "=" * 50 + "\n")

    json_text = format_to_json(test_text)
    print("提取的JSON文本:")
    print(json_text)
    print("\n" + "=" * 50 + "\n")

    json_obj = format_to_json_object(test_text)
    print("解析为Python对象:")
    print(json_obj)
    print("\n" + "=" * 50 + "\n")

    pretty_json = format_to_json_pretty(test_text)
    print("格式化的JSON:")
    print(pretty_json)
