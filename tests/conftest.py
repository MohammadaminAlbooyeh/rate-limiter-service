import os; os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_ratelimit.db"; os.environ["USE_REDIS"] = "false"; os.environ["USE_REDIS_CLUSTER"] = "false"
