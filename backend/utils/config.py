from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    database_url: str = "sqlite+aiosqlite:///./ratelimiter.db"
    log_level: str = "INFO"
    use_redis: bool = True
    prometheus_enabled: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
