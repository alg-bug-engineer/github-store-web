from sqlalchemy.orm import Session

from app.crud.system_config import system_config
from app.schemas.system_config import SystemConfigCreate


def init_db(db: Session) -> None:
    """Initialize database with seed data."""
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
                description="Search filter configuration",
            ),
        )

    github_search_queries_config = system_config.get_by_key(db, key="github_search_queries")
    if not github_search_queries_config:
        queries = {
            "trending": "stars:>1000 sort:updated",
            "new": "created:>2024-01-01 stars:>100 sort:stars",
            "desktop_apps": "topic:desktop-app stars:>50 sort:updated",
            "electron": "topic:electron stars:>100 sort:updated",
            "android": "topic:android-app stars:>50 sort:updated",
            "cli_tools": "topic:cli stars:>200 sort:updated",
            "productivity": "topic:productivity stars:>100 sort:updated",
            "developer_tools": "topic:developer-tools stars:>100 sort:updated",
        }
        system_config.create(
            db,
            obj_in=SystemConfigCreate(
                key="github_search_queries",
                value=queries,
                description="GitHub search queries for repository discovery",
            ),
        )
