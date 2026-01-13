"""输出工具函数"""

from colorama import Fore, Style


def output(node_name, state, is_first=False):
    """
    输出节点信息

    Args:
        node_name: 节点名称
        state: 工作流状态
        is_first: 是否为第一个节点
    """
    if is_first:
        print("-" * 20)
        doc_title = state.get("doc_title", "未知文件")
        print(
            f"{Fore.GREEN}{Style.BRIGHT}开始检测文件: {Fore.YELLOW}{Style.BRIGHT}{doc_title}{Style.RESET_ALL}"
        )
    else:
        print(
            f"{Fore.MAGENTA}{Style.BRIGHT}进入节点: {Fore.LIGHTCYAN_EX}{Style.BRIGHT}{node_name}{Style.RESET_ALL}"
        )

