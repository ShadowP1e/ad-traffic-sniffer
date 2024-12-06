import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


@dataclass(frozen=True)
class Config:
    APP_HOST = os.getenv('APP_HOST')
    APP_PORT = os.getenv('APP_PORT')

    SERVICES = list(item.split(':')[0] for item in os.getenv('SERVICES').split(','))

    VALID_USERNAME = os.getenv("APP_USERNAME", "admin")
    VALID_PASSWORD = os.getenv("APP_PASSWORD", "password")
    API_KEY_COOKIE_NAME = "session_token"
    API_KEY_COOKIE_VALUE = os.getenv(
        "SECRET_KEY",
        "FHBHBASDbhfabhfbsahHBbfhbHBhfbahkbfkabBbKHBKLbvhkBHKbhkvbdHVBHKBVHKbdvbh"
    )
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "FHBHBASDbhfabhfbsahHBbfhbHBhfbahkbfkabBbKHBKLbvhkBHKbhkvbdHVBHKBVHKbdvbh"
    )
    TRAFFIC_DUMP_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'dump', 'traffic_dump.pcap')
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'db.db')

    FLAG_REGEX = os.getenv('FLAG_REGEX', r'[A-Z0-9]{31}=')


def get_config() -> Config:
    return Config()


config = Config()
