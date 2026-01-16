"""
测试 retrieve_secret_menu 节点
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from confidential_judgement_agent.workflow.nodes import retrieve_secret_menu
from confidential_judgement_agent.workflow.state import State


def test_retrieve_secret_menu():
    """测试检索秘密目录节点"""

    # 准备测试数据
    test_state: State = {
        "current_node": "retrieve_secret_menu",
        "doc_title": "测试文档",
        "doc_content": "涉及消防救援体制机制改革等重大事项的方针政策、工作部署",
        "scene": "测试场景",
    }

    print("=" * 60)
    print("开始测试 retrieve_secret_menu 节点")
    print("=" * 60)
    print(f"\n输入状态:")
    print(f"  - doc_title: {test_state.get('doc_title')}")
    print(f"  - doc_content: {test_state.get('doc_content')}")
    print(f"  - scene: {test_state.get('scene')}")
    print("\n" + "-" * 60)

    # 调用节点函数
    try:
        result = retrieve_secret_menu(test_state)

        print("\n输出结果:")
        print("-" * 60)
        print(f"  - current_node: {result.get('current_node')}")

        if "error" in result:
            print(f"  - error: {result.get('error')}")

        if "retrieval_result" in result:
            retrieval = result.get("retrieval_result", {})
            print(f"  - retrieval_result.success: {retrieval.get('success')}")

            if retrieval.get("success"):
                print(f"  - retrieval_result.code: {retrieval.get('code')}")
                print(f"  - retrieval_result.message: {retrieval.get('message')}")
                print(f"  - retrieval_result.total: {retrieval.get('total')}")
                print(
                    f"  - retrieval_result.chunks_count: {retrieval.get('chunks_count')}"
                )

                if retrieval.get("chunk_summary"):
                    print(f"\n  - chunk_summary:")
                    print(
                        "    "
                        + "\n    ".join(retrieval.get("chunk_summary", "").split("\n"))
                    )

                # 显示前3个chunk的详细信息
                chunks = retrieval.get("chunks", [])
                if chunks:
                    print(f"\n  前3个chunk详情:")
                    for i, chunk in enumerate(chunks[:3], 1):
                        print(f"    Chunk {i}:")
                        print(f"      - chunk_id: {chunk.get('chunk_id')}")
                        print(f"      - similarity: {chunk.get('similarity', 0):.4f}")
                        print(
                            f"      - content_with_weight: {chunk.get('content_with_weight', '')[:100]}..."
                        )
            else:
                print(f"  - retrieval_result.error: {retrieval.get('error')}")

        # 检查secret_menu字段（相似度最高的chunk）
        if "secret_menu" in result:
            secret_menu = result.get("secret_menu", {})
            print(f"\n  ✅ secret_menu字段（相似度最高的chunk）:")
            print(f"    - chunk_id: {secret_menu.get('chunk_id')}")
            print(f"    - similarity: {secret_menu.get('similarity', 0):.4f}")
            print(
                f"    - content_with_weight: {secret_menu.get('content_with_weight', '')[:150]}..."
            )
            print(f"    - highlight: {secret_menu.get('highlight', '')[:150]}...")
            print(f"    - doc_id: {secret_menu.get('doc_id')}")
            print(f"    - docnm_kwd: {secret_menu.get('docnm_kwd')}")
        else:
            print(f"\n  ⚠️  未找到secret_menu字段（可能没有检索到结果）")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)

        return result

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return None


def test_retrieve_secret_menu_empty_content():
    """测试空内容的情况"""

    print("\n" + "=" * 60)
    print("测试空内容情况")
    print("=" * 60)

    test_state: State = {
        "current_node": "retrieve_secret_menu",
        "doc_title": "空文档",
        "doc_content": "",  # 空内容
        "scene": "测试场景",
    }

    result = retrieve_secret_menu(test_state)

    if result.get("error"):
        print(f"✅ 正确处理空内容: {result.get('error')}")
    else:
        print(f"❌ 未正确处理空内容")

    return result


if __name__ == "__main__":
    # 运行测试
    print("\n🚀 开始测试 retrieve_secret_menu 节点\n")

    # 测试1: 正常情况
    result1 = test_retrieve_secret_menu()

    # 测试2: 空内容
    result2 = test_retrieve_secret_menu_empty_content()

    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)
