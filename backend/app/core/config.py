from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "GitHub Releases Store"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    SECRET_KEY: str = "your-secret-key"
    # 7 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[PostgresDsn] = None

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try to parse it as JSON if it looks like a list
            if v.startswith('[') and v.endswith(']'):
                import json
                return json.loads(v)
            # Otherwise, treat it as a comma-separated list
            return [i.strip() for i in v.split(",")]
        raise ValueError(v)


    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_SERVER")
        db = values.get("POSTGRES_DB")
        
        return f"postgresql://{user}:{password}@{host}/{db}"


    # Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # GitHub
    GITHUB_TOKEN: str

    # Kimi AI
    KIMI_API_KEY: str
    KIMI_API_BASE: str = "https://api.moonshot.cn"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
