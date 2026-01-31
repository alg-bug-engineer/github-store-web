# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.user_session import UserSession  # noqa
from app.models.repository import Repository  # noqa
from app.models.release import Release  # noqa
from app.models.release_asset import ReleaseAsset  # noqa
from app.models.readme_cache import ReadmeCache  # noqa
from app.models.user_favorite import UserFavorite  # noqa
from app.models.search_history import SearchHistory  # noqa
from app.models.recommendation import Recommendation  # noqa
from app.models.system_config import SystemConfig  # noqa
