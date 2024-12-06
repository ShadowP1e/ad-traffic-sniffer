import re
from config import config


def contains_pattern(data: dict) -> bool:
    pattern = re.compile(config.FLAG_REGEX)
    for key, value in data.items():
        if isinstance(value, str) and pattern.search(value):
            return True

        elif isinstance(value, dict) and contains_pattern(value):
            return True
    return False
