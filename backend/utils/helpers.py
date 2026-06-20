import time


def current_timestamp() -> int:
    return int(time.time())


def format_window(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    else:
        return f"{seconds // 3600}h"
