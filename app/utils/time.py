from datetime import datetime, timezone


def get_current_unix_timestamp():
    return int(datetime.now(tz=timezone.utc).timestamp())

def unix_to_datetime(unix_timestamp):
    return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
