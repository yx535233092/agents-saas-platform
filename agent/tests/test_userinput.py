"""用户输入测试脚本"""

import os
import sys

# 将 agent 目录添加到 Python 路径中，以便能够导入 confidential_judgement_agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from confidential_judgement_agent.workflow import app


def main():
    """主函数"""

    # 构建输入数据
    input_data = {
        "doc_title": "未命名文档",
        "doc_content": "消防救援",
    }

    print("\n开始处理...")
    result = app.invoke(input_data)
    print("\n处理完成！")
    print(f"结果: {result}")


if __name__ == "__main__":
    main()
