#!/usr/bin/env python3
"""
快速验证接口连接
用于测试接口是否可用，以及请求格式是否正确
"""
import asyncio
import aiohttp
import json
from config import TEST_CONFIG
from test_data import TestDataLoader


async def verify_connection():
    """验证接口连接"""
    api_url = TEST_CONFIG["api_url"]
    use_langserve = TEST_CONFIG.get("use_langserve", True)
    
    print(f"测试接口: {api_url}")
    print(f"使用 LangServe 格式: {use_langserve}")
    print("-" * 60)
    
    # 加载测试数据
    loader = TestDataLoader()
    test_data = loader.get_random_data()
    
    print(f"测试文档: {test_data['doc_title']}")
    print(f"内容长度: {len(test_data['doc_content'])} 字符")
    print("-" * 60)
    
    # 准备请求数据
    if use_langserve:
        payload = {
            "input": {
                "doc_title": test_data["doc_title"],
                "doc_content": test_data["doc_content"],
                "current_node": "start_node",
                "is_sensitive": False,
                "scene": "",
                "evidence": "",
                "secret_analysis_result": {},
                "public_analysis_result": {},
                "confidence": 0
            }
        }
    else:
        payload = {
            "doc_title": test_data["doc_title"],
            "doc_content": test_data["doc_content"]
        }
    
    print(f"请求数据格式:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("-" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            print("发送请求...")
            
            async with session.post(
                api_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"HTTP 状态码: {response.status}")
                print(f"响应头: {dict(response.headers)}")
                print("-" * 60)
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ 请求失败!")
                    print(f"错误信息: {error_text[:500]}")
                    return False
                
                print("✅ 连接成功！开始接收流式数据...")
                print("-" * 60)
                
                # 接收前几行数据
                chunk_count = 0
                async for chunk in response.content.iter_any():
                    chunk_text = chunk.decode('utf-8', errors='ignore')
                    print(chunk_text[:200], end='', flush=True)
                    
                    chunk_count += 1
                    if chunk_count >= 5:  # 只显示前5个块
                        print("\n...")
                        break
                
                print("\n" + "-" * 60)
                print("✅ 接口验证成功！可以开始性能测试了。")
                return True
                
    except aiohttp.ClientConnectorError as e:
        print(f"❌ 连接失败: {str(e)}")
        print("请检查:")
        print("  1. 服务是否已启动？")
        print("  2. 端口是否正确（默认 5001）？")
        print("  3. 接口路径是否正确？")
        return False
    except asyncio.TimeoutError:
        print("❌ 请求超时")
        print("请检查服务是否正常运行")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(verify_connection())
    exit(0 if success else 1)

