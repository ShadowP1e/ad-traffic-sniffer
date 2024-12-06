import json
import logging
import re
from lib2to3.btm_utils import reduce_tree
from urllib.parse import parse_qs
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup


def normalize_request(request: dict) -> dict:
    skip_keys = ['', 'chat', 'cookie_pair', 'file_data', 'timestamp']

    headers = {}

    for key in request.keys():
        if key.startswith('_') or 'request' in key or key in skip_keys:
            continue

        if key == 'cookie':
            headers[key] = normalize_cookie(request[key])
        else:
            headers[key] = request[key]

    content_type = headers.get('content_type', None)
    body = normalize_body_request(request.get('file_data', None), content_type)

    return {
        'timestamp': request.get('timestamp', None),
        'method': request.get('request_method', None),
        'uri': request.get('request_uri', None),
        'version': request.get('request_version', None),
        'headers': headers,
        'body': body,
    }

def normalize_response(response: dict) -> dict:
    skip_keys = ['', 'chat', 'file_data', 'timestamp']
    headers = {}

    for key in response.keys():
        if key.startswith('_') or 'response' in key or key in skip_keys:
            continue

        if key == 'set-cookie':
            headers[key] = normalize_cookie(response[key])
        else:
            headers[key] = response[key]

    content_type = headers.get('content_type', None)
    body = normalize_body_response(response.get('file_data', None), content_type)

    return {
        'timestamp': response.get('timestamp', None),
        'version': response.get('response_version', None),
        'status_code': response.get('response_code', None),
        'status_code_desc': response.get('response_code_desc', None),
        'status_code_phrase': response.get('response_phrase', None),
        'uri': response.get('response_for_uri', None),
        'headers': headers,
        'body': body,
    }

def normalize_http_data(http_data: dict) -> dict:
    http_data['request'] = normalize_request(http_data['request'])
    http_data['response'] = normalize_response(http_data['response'])
    return http_data

def normalize_cookie(cookie: str) -> dict:
    return dict(item.split("=", 1) for item in cookie.split("; "))

import json
import re
from urllib.parse import parse_qs

def normalize_body_request(body: str, content_type: str | None = None) -> dict | str:
    if body is None:
        return body

    try:
        if content_type == "application/json":
            return json.loads(body)

        elif content_type == "application/x-www-form-urlencoded":
            if "=" in body:
                parsed_data = parse_qs(body)
                return {key: value[0] if len(value) == 1 else value for key, value in parsed_data.items()}
            return body

        elif content_type and "multipart/form-data" in content_type:
            boundary_match = re.search(r'(-+[\w\d]+)', body)
            if boundary_match:
                boundary = boundary_match.group(1)
                parts = body.split(boundary)
                form_data = {}
                for part in parts:
                    if 'Content-Disposition' in part:
                        name_match = re.search(r'name="([^"]+)"', part)
                        if name_match:
                            name = name_match.group(1)
                            _, _, value = part.partition(' ' * 4)
                            form_data[name] = value.strip().replace('--', '').strip()
                return form_data
            return body

        elif content_type == "text/plain":
            return body.strip()

    except Exception as e:
        logging.info("Парсинг сломался:", e)

    return body

def normalize_body_response(body: str, content_type: str | None = None) -> dict | str:
    if body is None:
        return body

    try:
        if 'application/json' in content_type:
            return json.loads(body)
        elif 'text/html' in content_type:
            soup = BeautifulSoup(body, "html.parser")
            return soup.prettify()
        elif 'application/xml' in content_type or 'text/xml' in content_type:
            root = ET.fromstring(body)
            return ET.tostring(root, encoding='unicode')
        elif 'text/plain' in content_type:
            return body.strip()
        else:
            return body
    except (json.JSONDecodeError, ET.ParseError, Exception):
        return body
