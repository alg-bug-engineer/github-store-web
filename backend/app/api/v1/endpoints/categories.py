"""
Categories API - 分类配置端点

提供分类列表和配置信息，供前端动态加载。
"""

import json
import os
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException

router = APIRouter()

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "config")
CATEGORIES_FILE = os.path.join(CONFIG_DIR, "categories.json")

# 缓存配置
_config_cache: Dict[str, Any] = {}


def load_categories_config() -> Dict[str, Any]:
    """加载分类配置文件"""
    global _config_cache

    if _config_cache:
        return _config_cache

    try:
        with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
            _config_cache = json.load(f)
        return _config_cache
    except FileNotFoundError:
        # 返回默认配置
        return {
            "categories": [
                {
                    "id": "developer_tools",
                    "label": "Dev Tools",
                    "label_zh": "开发工具",
                    "color": "blue",
                    "priority": 1
                },
                {
                    "id": "productivity",
                    "label": "Productivity",
                    "label_zh": "效率工具",
                    "color": "green",
                    "priority": 2
                },
                {
                    "id": "media",
                    "label": "Media",
                    "label_zh": "多媒体",
                    "color": "purple",
                    "priority": 3
                },
                {
                    "id": "utilities",
                    "label": "System",
                    "label_zh": "系统工具",
                    "color": "amber",
                    "priority": 4
                }
            ],
            "default_category": "developer_tools"
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid categories configuration")


@router.get("/")
async def get_categories() -> Dict[str, Any]:
    """
    获取所有分类配置

    返回:
    - categories: 分类列表，每个分类包含 id, label, label_zh, color, icon, priority
    - default_category: 默认分类 ID
    """
    config = load_categories_config()

    # 返回前端需要的精简格式
    categories = [
        {
            "id": cat["id"],
            "label": cat["label"],
            "label_zh": cat.get("label_zh", cat["label"]),
            "color": cat.get("color", "gray"),
            "icon": cat.get("icon", "folder"),
            "priority": cat.get("priority", 999)
        }
        for cat in sorted(config.get("categories", []), key=lambda x: x.get("priority", 999))
    ]

    return {
        "categories": categories,
        "default_category": config.get("default_category", "developer_tools")
    }


@router.get("/{category_id}")
async def get_category(category_id: str) -> Dict[str, Any]:
    """
    获取指定分类的详细信息

    参数:
    - category_id: 分类 ID

    返回:
    - 分类详情，包含 topics 等完整信息
    """
    config = load_categories_config()

    for cat in config.get("categories", []):
        if cat["id"] == category_id:
            return cat

    raise HTTPException(status_code=404, detail=f"Category '{category_id}' not found")


@router.post("/reload")
async def reload_categories() -> Dict[str, str]:
    """
    重新加载分类配置（清除缓存）

    用于在修改配置文件后刷新配置。
    """
    global _config_cache
    _config_cache = {}
    load_categories_config()
    return {"message": "Categories configuration reloaded"}
