import logging
import json
from backend.utils.config import settings


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logger():
    logger = logging.getLogger("rate_limiter")
    handler = logging.StreamHandler()
    if settings.log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False

    # Also configure the root logger with the same handler
    root_logger = logging.getLogger()
    root_handler = logging.StreamHandler()
    if settings.log_format == "json":
        root_handler.setFormatter(JsonFormatter())
    else:
        root_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
    root_logger.addHandler(root_handler)
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    return logger


logger = setup_logger()
