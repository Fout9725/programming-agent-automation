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

VSEGPT_URL = 'https://api.vsegpt.ru/v1/chat/completions'
DB_MODEL = 'deepseek/deepseek-chat-3.1-alt-fast'

SYSTEM_PROMPT = """Ты — senior PostgreSQL DBA. Генерируй SQL-миграции.

ПРАВИЛА:
- SERIAL для PRIMARY KEY
- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP к каждой таблице
- FOREIGN KEY inline через REFERENCES
- CREATE TABLE IF NOT EXISTS
- Индексы для FK полей
- Добавь INSERT INTO с 3-5 тестовыми строками на таблицу

Верни СТРОГО JSON:
{"migration_sql": "CREATE TABLE...; INSERT INTO...", "tables_created": ["table1"]}"""


def handler(event, context):
    """Агент БД — генерация SQL миграций и тестовых данных"""
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': '', 'isBase64Encoded': False}
    if event.get('httpMethod') != 'POST':
        return {'statusCode': 405, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Method not allowed'}), 'isBase64Encoded': False}

    body = json.loads(event.get('body', '{}'))
    if body.get('action') == 'generate':
        return generate_schema(body)
    return {'statusCode': 400, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Unknown action'}), 'isBase64Encoded': False}


def generate_schema(body):
    spec = body.get('spec', {})
    db_spec = spec.get('database', {})
    if not db_spec or not db_spec.get('tables'):
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps({'files': {}, 'tables_created': []}), 'isBase64Encoded': False}

    api_key = os.environ.get('VSEGPT_API_KEY', '')
    if api_key:
        result = call_ai(db_spec, spec, api_key)
        if result:
            return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}

    result = generate_fallback(db_spec)
    return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}


def call_ai(db_spec, full_spec, api_key):
    try:
        resp = requests.post(VSEGPT_URL, headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={'model': DB_MODEL, 'messages': [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': f'Спецификация:\n{json.dumps(db_spec, ensure_ascii=False, indent=2)}\nОписание: {full_spec.get("description", "")}'}
            ], 'max_tokens': 4096, 'temperature': 0.2}, timeout=90)
        if resp.status_code != 200:
            return None
        parsed = parse_json(resp.json().get('choices', [{}])[0].get('message', {}).get('content', ''))
        if parsed and 'migration_sql' in parsed:
            return {'files': {'migration.sql': parsed['migration_sql']}, 'tables_created': parsed.get('tables_created', []), 'ai_generated': True}
    except Exception:
        pass
    return None


def parse_json(text):
    text = text.strip()
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    s, e = text.find('{'), text.rfind('}')
    if s != -1 and e > s:
        try:
            return json.loads(text[s:e+1])
        except json.JSONDecodeError:
            pass
    return None


def generate_fallback(db_spec):
    tables = db_spec.get('tables', [])
    sql_parts = []
    names = []
    for t in tables:
        name = t.get('name', 'data')
        names.append(name)
        cols = [f"    {c.get('name','')} {c.get('type','TEXT')}" for c in t.get('columns', [])]
        if not any('created_at' in c.get('name','') for c in t.get('columns',[])):
            cols.append("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        sql_parts.append(f"CREATE TABLE IF NOT EXISTS {name} (\n" + ",\n".join(cols) + "\n);")
    for idx in db_spec.get('indexes', []):
        if idx.strip():
            sql_parts.append(idx.rstrip(';') + ';')
    return {'files': {'migration.sql': "\n\n".join(sql_parts)}, 'tables_created': names, 'ai_generated': False}
