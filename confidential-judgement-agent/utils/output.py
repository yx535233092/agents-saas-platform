from colorama import Fore, Style


def output(node_name, state, is_first=False):
    if is_first:
        print("-" * 20)
        print(
            f"{Fore.GREEN}{Style.BRIGHT}开始检测文件: {Fore.YELLOW}{Style.BRIGHT}{state['doc_title']}{Style.RESET_ALL}"
        )
    else:
        print(
            f"{Fore.MAGENTA}{Style.BRIGHT}进入节点: {Fore.LIGHTCYAN_EX}{Style.BRIGHT}{node_name}{Style.RESET_ALL}"
        )
