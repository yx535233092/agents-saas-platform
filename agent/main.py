"""
涉密研判智能体入口文件

支持两种运行模式：
1. SSE API 模式：python main.py sse
2. LangServe API 模式：python main.py serve
"""

import sys
import uvicorn
from confidential_judgement_agent.config import get_settings
from confidential_judgement_agent.api import sse_app, serve_app

settings = get_settings()


def run_sse_api():
    """运行 SSE API 服务"""
    uvicorn.run(
        sse_app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )


def run_serve_api():
    """运行 LangServe API 服务"""
    uvicorn.run(
        serve_app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )


def main():
    """主函数"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "sse":
            run_sse_api()
        elif mode == "serve":
            run_serve_api()
        else:
            print(f"未知模式: {mode}")
            print("使用方法: python main.py [sse|serve]")
            sys.exit(1)
    else:
        # 默认运行 SSE API
        print("未指定模式，默认运行 SSE API")
        print("使用方法: python main.py [sse|serve]")
        run_sse_api()


if __name__ == "__main__":
    main()
