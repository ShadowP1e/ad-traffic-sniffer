import re


def generate_code_for_chain(chain_requests):
    code = "import requests\n\nsession_data = {}\n\n"

    extracted_values = {}

    print(chain_requests)

    service_ip = chain_requests.get("service_ip", "127.0.0.1")
    service_port = chain_requests.get("service_port", "80")

    for i, log in enumerate(chain_requests['requests']):
        method = log.get("request", {}).get("method", "GET")
        uri = log.get("request", {}).get("uri", "/")

        url = f"http://{service_ip}:{service_port}{uri}"
        headers = log.get("request", {}).get("headers", {})
        body = log.get("request", {}).get("body", None)

        code += f"# Запрос {i + 1}\n"
        code += f"url = '{url}'\n"
        code += "headers = {}\n"

        for header_name, header_value in headers.items():
            dynamic_value = substitute_dynamic_value(header_value, extracted_values)
            code += f"headers['{header_name}'] = {dynamic_value}\n"

        if body and isinstance(body, dict):
            code += "data = {}\n"
            for key, value in body.items():
                dynamic_value = substitute_dynamic_value(value, extracted_values)
                code += f"data['{key}'] = {dynamic_value}\n"
        else:
            code += "data = None\n"

        code += f"response = requests.{method.lower()}(url, headers=headers, json=data)\n"
        code += f"print(f'Response {i + 1}:', response.status_code, response.text)\n\n"

        # Обработка ответа и сохранение значений в session_data
        code += "# Извлекаем значения из ответа для использования в следующем запросе\n"
        code += "try:\n"
        code += "    response_data = response.json()\n"
        code += "except ValueError:\n"
        code += "    response_data = None\n"

        if log.get("response"):
            potential_vars = extract_variables_from_response(log.get("response", {}).get("body", {}))
            for var_name, var_value in potential_vars.items():
                extracted_values[var_name] = var_value
                code += f"if response_data and '{var_name}' in response_data:\n"
                code += f"    session_data['{var_name}'] = response_data['{var_name}']\n"

    return code


def substitute_dynamic_value(value, extracted_values):
    if isinstance(value, str):
        for key, extracted_value in extracted_values.items():
            if extracted_value == value:
                return f"session_data['{key}']"
        return f"'''{value}'''"
    return value


def extract_variables_from_response(response_body):
    potential_vars = {}
    if isinstance(response_body, dict):
        for key, value in response_body.items():
            if isinstance(value, str) and re.match(r'^[A-Za-z0-9]{10,}$', value):
                potential_vars[key] = value
    return potential_vars


def generate_code_for_log(log_data):
    url = f"http://{log_data['service_ip']}:{log_data['service_port']}{log_data['request'].get('uri', '/')}"
    method = log_data['request'].get('method', 'GET')
    headers = log_data['request'].get('headers', {})
    body = log_data['request'].get('body')

    headers_code = "\n".join([f"    '{key}': '{value}'" for key, value in headers.items()])

    # Формируем тело запроса
    body_code = f", data='{body}'" if body else ""

    # Формируем код для запроса
    python_code = f"""import requests

url = "{url}"
headers = {{
{headers_code}
}}

response = requests.{method.lower()}(url, headers=headers{body_code})
print(response.status_code)
print(response.text)
"""
    return python_code
