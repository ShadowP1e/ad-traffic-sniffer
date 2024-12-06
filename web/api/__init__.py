from config import config
from modules.storage import Storage
from dependencies import verify_cookie_token

__all__ = [
    'storage',
    'verify_cookie_token',
]


storage = Storage(config.DATABASE_PATH)
