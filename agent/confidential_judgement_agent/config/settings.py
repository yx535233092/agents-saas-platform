"""配置管理模块"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取项目根目录
BASE_DIR = Path(__file__).parent.parent.parent


class Settings:
    """应用配置类"""

    # API 配置
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "5001"))

    # LLM 配置
    MODEL: str = os.getenv("MODEL", "deepseek-chat")
    SILICONFLOW_API_KEY: Optional[str] = os.getenv("SILICONFLOW_API_KEY")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0"))

    # 检索接口配置
    RETRIEVAL_API_URL: str = os.getenv("RETRIEVAL_API_URL", "http://119.45.162.155/v1/chunk/retrieval_test")
    RETRIEVAL_AUTHORIZATION: Optional[str] = os.getenv("RETRIEVAL_AUTHORIZATION", "IjQwZGQxNGY4ZTIyODExZjBiZDRlNTJlMzU3YWYyN2E0Ig.aU4yCA.AsCQmLk33K1PQFLb2XoF_Z9cobk")
    RETRIEVAL_KB_ID: str = os.getenv("RETRIEVAL_KB_ID", "08a864acf29f11f0bd4e52e357af27a4")
    RETRIEVAL_SEARCH_ID: str = os.getenv("RETRIEVAL_SEARCH_ID", "7c760ac2f2a111f0bd4e52e357af27a4")
    RETRIEVAL_PAGE_SIZE: int = int(os.getenv("RETRIEVAL_PAGE_SIZE", "50"))

    # 静态文件路径
    STATIC_DIR: Path = BASE_DIR / "static"
    SECRET_MENU_PATH: Path = STATIC_DIR / "secret_menu.json"
    KEYWORDS_PATH: Path = STATIC_DIR / "keywords.json"
    SHORT_SENTENCE_PATH: Path = STATIC_DIR / "short_sentence.json"

    # CORS 配置
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: Path = LOG_DIR / "app.log"

    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        cls.LOG_DIR.mkdir(exist_ok=True)
        cls.STATIC_DIR.mkdir(exist_ok=True)


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.ensure_directories()
    return _settings

