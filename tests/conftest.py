import os; os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_ratelimit.db"); os.environ.setdefault("USE_REDIS", "false"); os.environ.setdefault("USE_REDIS_CLUSTER", "false")
