import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


@dataclass(frozen=True)
class Config:
    APP_HOST = os.getenv('APP_HOST')
    APP_PORT = os.getenv('APP_PORT')

    INTERFACE = os.getenv('INTERFACE', None)

    SERVICES_PORTS = os.getenv('SERVICES_PORTS').split(',')

    TRAFFIC_DUMP_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'dump', 'traffic_dump.pcap')
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'db.db')

    FLAG_REGEX = os.getenv('FLAG_REGEX', r'[A-Z0-9]{31}=')


def get_config() -> Config:
    return Config()


config = Config()
