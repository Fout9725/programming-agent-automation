import json
import os
import re
import requests

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
}

SYSTEM_PROMPT = """Ты — senior Python-разработчик. Генерируй Cloud Functions для poehali.dev.

ФОРМАТ CLOUD FUNCTION:
- Entry point: def handler(event: dict, context) -> dict
- Обязательно обрабатывай OPTIONS для CORS
- CORS headers: {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type, X-Authorization'}
- Парсинг body: json.loads(event.get('body', '{}'))
- Auth header: event.get('headers', {}).get('X-Authorization', '')
- БД: psycopg2 + os.environ['DATABASE_URL']
- Всегда isBase64Encoded: False
- Docstring на русском

Верни ТОЛЬКО валидный JSON:
{
  "files": {
    "backend/api-items/index.py": "код handler",
    "backend/api-items/requirements.txt": "зависимости",
    "backend/api-items/tests.json": "JSON тестов"
  },
  "functions": ["api-items"]
}"""

FIX_PROMPT = """Ты — senior Python-разработчик. Исправь ошибки в Cloud Functions.
Верни ТОЛЬКО валидный JSON: {"files": {"путь": "исправленный код"}}"""


def handler(event, context):
    """Агент Backend — генерация Python Cloud Functions и API"""
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': '', 'isBase64Encoded': False}

    if event.get('httpMethod') != 'POST':
        return {'statusCode': 405, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Method not allowed'}), 'isBase64Encoded': False}

    body = json.loads(event.get('body', '{}'))
    action = body.get('action', '')

    if action == 'generate':
        return generate_backend(body)
    elif action == 'fix':
        return fix_code(body)

    return {'statusCode': 400, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Unknown action'}), 'isBase64Encoded': False}


def generate_backend(body):
    spec = body.get('spec', {})
    backend_spec = spec.get('backend', {})
    db_spec = spec.get('database', {})
    ai_model = body.get('ai_model', 'anthropic/claude-sonnet-4')
    language = body.get('language', 'ru')

    endpoints = backend_spec.get('endpoints', [])
    if not endpoints:
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'files': {}, 'functions': [], 'message': 'Нет API endpoints'}),
            'isBase64Encoded': False
        }

    api_key = os.environ.get('OPENROUTER_API_KEY', '')

    user_prompt = f"""Создай Cloud Functions по спецификации.

Backend спецификация:
{json.dumps(backend_spec, ensure_ascii=False, indent=2)}

Схема БД:
{json.dumps(db_spec, ensure_ascii=False, indent=2)}

Тип аутентификации: {backend_spec.get('auth_type', 'none')}
Язык: {'русский' if language == 'ru' else 'английский'}

Группируй endpoints по сущностям."""

    if api_key:
        result = call_openrouter(SYSTEM_PROMPT, user_prompt, ai_model, api_key)
        if result:
            return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}

    result = generate_fallback(backend_spec, db_spec, language)
    return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}


def fix_code(body):
    files = body.get('files', {})
    issues = body.get('issues', [])
    ai_model = body.get('ai_model', 'anthropic/claude-sonnet-4')
    api_key = os.environ.get('OPENROUTER_API_KEY', '')

    if not files or not issues:
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps({'files': files}), 'isBase64Encoded': False}

    user_prompt = f"""Файлы с ошибками:
{json.dumps(files, ensure_ascii=False, indent=2)}

Ошибки:
{json.dumps(issues, ensure_ascii=False, indent=2)}"""

    if api_key:
        result = call_openrouter(FIX_PROMPT, user_prompt, ai_model, api_key)
        if result and 'files' in result:
            return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}

    return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps({'files': files}), 'isBase64Encoded': False}


def call_openrouter(system_prompt, user_prompt, ai_model, api_key):
    try:
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': ai_model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 16000,
                'response_format': {'type': 'json_object'}
            },
            timeout=120
        )

        if response.status_code != 200:
            return None

        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        parsed = parse_json_response(content)

        if parsed:
            if 'functions' in parsed and isinstance(parsed['functions'], dict):
                all_files = {}
                func_names = []
                for func_name, func_data in parsed['functions'].items():
                    func_names.append(func_name)
                    if isinstance(func_data, dict):
                        for fname, fcontent in func_data.items():
                            all_files[f'backend/{func_name}/{fname}'] = fcontent
                parsed['files'] = all_files
                parsed['functions'] = func_names
            parsed['ai_generated'] = True
            return parsed
        return None
    except Exception:
        return None


def parse_json_response(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass
    return None


def generate_fallback(backend_spec, db_spec, language):
    endpoints = backend_spec.get('endpoints', [])
    functions_map = {}

    for ep in endpoints:
        path = ep.get('path', '/api/data')
        parts = path.strip('/').split('/')
        func_name = parts[1] if len(parts) > 1 else parts[0]
        func_name = f"api-{func_name}"

        if func_name not in functions_map:
            functions_map[func_name] = []
        functions_map[func_name].append(ep)

    files = {}
    func_names = []

    for func_name, eps in functions_map.items():
        func_names.append(func_name)

        handler_code = '''import json
import os

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Authorization',
    'Content-Type': 'application/json'
}

def handler(event, context):
    """API endpoint"""
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': '', 'isBase64Encoded': False}

    method = event.get('httpMethod', 'GET')

    if method == 'GET':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps({'items': [], 'message': 'OK'}), 'isBase64Encoded': False}

    if method == 'POST':
        body = json.loads(event.get('body', '{}'))
        return {'statusCode': 201, 'headers': CORS_HEADERS, 'body': json.dumps({'message': 'Created', 'data': body}), 'isBase64Encoded': False}

    return {'statusCode': 405, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Method not allowed'}), 'isBase64Encoded': False}
'''

        files[f'backend/{func_name}/index.py'] = handler_code
        files[f'backend/{func_name}/requirements.txt'] = 'psycopg2-binary\npydantic>=2.5.0'
        files[f'backend/{func_name}/tests.json'] = json.dumps({
            'tests': [
                {'name': 'OPTIONS CORS', 'method': 'OPTIONS', 'path': '/', 'expectedStatus': 200},
                {'name': f'GET {func_name}', 'method': 'GET', 'path': '/', 'expectedStatus': 200}
            ]
        }, indent=2)

    return {
        'files': files,
        'functions': func_names,
        'ai_generated': False
    }
