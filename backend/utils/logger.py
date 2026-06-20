import logging
from backend.utils.config import settings


def setup_logger():
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger("rate_limiter")


logger = setup_logger()
