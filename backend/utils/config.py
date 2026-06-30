from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    database_url: str = "sqlite+aiosqlite:///./ratelimiter.db"
    log_level: str = "INFO"
    log_format: str = "text"  # "text" or "json"
    use_redis: bool = True
    use_redis_cluster: bool = False
    redis_cluster_nodes: str = ""
    admin_api_key: str = ""
    cors_origins: str = "*"
    prometheus_enabled: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
# Re-read env for tests that set DATABASE_URL after initial import
def _reload_settings():
    global settings
    settings = Settings()
