"""
应用管理数据存储和操作
使用JSON文件存储应用配置（可以后续迁移到数据库）
"""

import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# 数据文件路径
DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "applications.json"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)


def load_applications() -> List[dict]:
    """加载应用列表"""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_applications(applications: List[dict]) -> None:
    """保存应用列表"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(applications, f, ensure_ascii=False, indent=2)


def get_next_id() -> int:
    """获取下一个ID"""
    applications = load_applications()
    if not applications:
        return 1
    return max(app.get("id", 0) for app in applications) + 1


def get_application(app_id: int) -> Optional[dict]:
    """获取单个应用"""
    applications = load_applications()
    for app in applications:
        if app.get("id") == app_id:
            return app
    return None


def create_application(app_data: dict) -> dict:
    """创建应用"""
    applications = load_applications()
    app_id = get_next_id()

    now = datetime.now().isoformat()
    new_app = {
        "id": app_id,
        **app_data,
        "created_at": now,
        "updated_at": now,
    }
    applications.append(new_app)
    save_applications(applications)
    return new_app


def update_application(app_id: int, app_data: dict) -> Optional[dict]:
    """更新应用"""
    applications = load_applications()
    for i, app in enumerate(applications):
        if app.get("id") == app_id:
            updated_app = {
                **app,
                **app_data,
                "id": app_id,  # 确保ID不被覆盖
                "updated_at": datetime.now().isoformat(),
            }
            applications[i] = updated_app
            save_applications(applications)
            return updated_app
    return None


def delete_application(app_id: int) -> bool:
    """删除应用"""
    applications = load_applications()
    original_count = len(applications)
    applications = [app for app in applications if app.get("id") != app_id]
    if len(applications) < original_count:
        save_applications(applications)
        return True
    return False


def get_public_applications() -> List[dict]:
    """获取公开的应用列表（只返回启用的应用）"""
    applications = load_applications()
    return [app for app in applications if app.get("is_active", False)]
