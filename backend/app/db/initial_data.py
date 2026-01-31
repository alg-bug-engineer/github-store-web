import json
from sqlalchemy.orm import Session

from app.crud.system_config import system_config
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate


def init_db(db: Session) -> None:
    # Create initial system configs
    search_filters_config = system_config.get_by_key(db, key="search_filters")
    if not search_filters_config:
        filters = {
            "android": "topic:android stars:>50 archived:false",
            "desktop": "topic:desktop stars:>50 archived:false",
            "popular": "stars:>500 archived:false",
        }
        system_config.create(
            db,
            obj_in=SystemConfigCreate(
                key="search_filters",
                value=filters,
                description="搜索过滤器配置",
            ),
        )

    github_token_config = system_config.get_by_key(db, key="github_token")
    if not github_token_config:
        system_config.create(
            db,
            obj_in=SystemConfigCreate(
                key="github_token",
                value={"token": "ghp_xxxxx"},
                description="GitHub API Token",
            ),
        )

    kimi_api_config = system_config.get_by_key(db, key="kimi_api")
    if not kimi_api_config:
        system_config.create(
            db,
            obj_in=SystemConfigCreate(
                key="kimi_api",
                value={"api_key": "xxx", "endpoint": "https://api.moonshot.cn"},
                description="Kimi API配置",
            ),
        )
