"""
Category Service - 分类配置服务

从配置文件加载分类定义，支持动态配置分类和对应的 topics。
"""

import json
import os
import logging
from typing import Optional, List, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
CATEGORIES_FILE = os.path.join(CONFIG_DIR, "categories.json")


class CategoryService:
    """分类服务 - 管理仓库分类配置"""

    def __init__(self, config_path: str = CATEGORIES_FILE):
        self.config_path = config_path
        self._config: Optional[Dict[str, Any]] = None
        self._topic_to_category: Dict[str, str] = {}
        self._language_to_category: Dict[str, str] = {}
        self._load_config()

    def _load_config(self) -> None:
        """加载分类配置文件"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
            self._build_indexes()
            logger.info(f"Loaded {len(self.get_categories())} categories from {self.config_path}")
        except FileNotFoundError:
            logger.warning(f"Categories config not found: {self.config_path}, using defaults")
            self._config = self._get_default_config()
            self._build_indexes()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in categories config: {e}")
            self._config = self._get_default_config()
            self._build_indexes()

    def _build_indexes(self) -> None:
        """构建 topic -> category 和 language -> category 的索引"""
        self._topic_to_category = {}
        self._language_to_category = {}

        for cat in self._config.get("categories", []):
            cat_id = cat["id"]
            # 索引 topics
            for topic in cat.get("topics", []):
                self._topic_to_category[topic.lower()] = cat_id
            # 索引 languages
            for lang in cat.get("languages", []):
                self._language_to_category[lang.lower()] = cat_id

    def _get_default_config(self) -> Dict[str, Any]:
        """返回默认配置"""
        return {
            "categories": [
                {
                    "id": "developer_tools",
                    "label": "Dev Tools",
                    "label_zh": "开发工具",
                    "color": "blue",
                    "priority": 1,
                    "topics": ["cli", "terminal", "developer-tools", "devtools"]
                }
            ],
            "default_category": "developer_tools"
        }

    def reload(self) -> None:
        """重新加载配置"""
        self._load_config()

    def get_categories(self) -> List[Dict[str, Any]]:
        """获取所有分类"""
        return self._config.get("categories", [])

    def get_category_ids(self) -> List[str]:
        """获取所有分类 ID"""
        return [cat["id"] for cat in self.get_categories()]

    def get_category_by_id(self, category_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取分类详情"""
        for cat in self.get_categories():
            if cat["id"] == category_id:
                return cat
        return None

    def get_default_category(self) -> str:
        """获取默认分类"""
        return self._config.get("default_category", "developer_tools")

    def detect_category(self, repo_data: Dict[str, Any]) -> str:
        """
        根据仓库数据检测分类

        优先级：
        1. topics 匹配
        2. language 匹配
        3. name/description 模式匹配
        4. 默认分类
        """
        topics = [t.lower() for t in repo_data.get("topics", [])]
        language = (repo_data.get("language") or "").lower()
        name = (repo_data.get("name") or "").lower()
        description = (repo_data.get("description") or "").lower()

        # 1. 按优先级检查 topics 匹配
        category_scores: Dict[str, int] = {}

        for topic in topics:
            if topic in self._topic_to_category:
                cat_id = self._topic_to_category[topic]
                category_scores[cat_id] = category_scores.get(cat_id, 0) + 2

        # 2. language 匹配（权重较低）
        if language in self._language_to_category:
            cat_id = self._language_to_category[language]
            category_scores[cat_id] = category_scores.get(cat_id, 0) + 1

        # 3. name/description 模式匹配
        for cat in self.get_categories():
            cat_id = cat["id"]
            patterns = cat.get("name_patterns", [])
            for pattern in patterns:
                if pattern.lower() in name or pattern.lower() in description:
                    category_scores[cat_id] = category_scores.get(cat_id, 0) + 1

        # 4. 返回得分最高的分类
        if category_scores:
            # 按得分排序，得分相同时按优先级排序
            sorted_cats = sorted(
                category_scores.items(),
                key=lambda x: (x[1], -self._get_category_priority(x[0])),
                reverse=True
            )
            return sorted_cats[0][0]

        return self.get_default_category()

    def _get_category_priority(self, category_id: str) -> int:
        """获取分类优先级"""
        cat = self.get_category_by_id(category_id)
        return cat.get("priority", 999) if cat else 999

    def get_categories_for_api(self) -> List[Dict[str, Any]]:
        """获取用于 API 响应的分类列表（前端使用）"""
        return [
            {
                "id": cat["id"],
                "label": cat["label"],
                "label_zh": cat.get("label_zh", cat["label"]),
                "color": cat.get("color", "gray"),
                "icon": cat.get("icon", "folder"),
                "priority": cat.get("priority", 999)
            }
            for cat in sorted(self.get_categories(), key=lambda x: x.get("priority", 999))
        ]


# 全局单例
_category_service: Optional[CategoryService] = None


def get_category_service() -> CategoryService:
    """获取分类服务单例"""
    global _category_service
    if _category_service is None:
        _category_service = CategoryService()
    return _category_service


def detect_category(repo_data: Dict[str, Any]) -> str:
    """便捷函数：检测仓库分类"""
    return get_category_service().detect_category(repo_data)
