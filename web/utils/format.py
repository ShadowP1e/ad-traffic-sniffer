import json


def format_http_data(http_data: dict):
    http_data['request'] = json.loads(http_data['request'])
    http_data['response'] = json.loads(http_data['response'])
    return http_data
