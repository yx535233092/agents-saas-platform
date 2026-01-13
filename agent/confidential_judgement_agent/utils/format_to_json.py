"""JSON 格式化工具"""

import json
import re
from typing import Union


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


def format_to_json_object(text: str) -> Union[dict, list]:
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

