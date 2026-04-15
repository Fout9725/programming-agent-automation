import json
import os
import requests

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
}

def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': '', 'isBase64Encoded': False}
    
    if event.get('httpMethod') != 'POST':
        return {'statusCode': 405, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Method not allowed'}), 'isBase64Encoded': False}
    
    body = json.loads(event.get('body', '{}'))
    action = body.get('action', '')
    
    if action == 'generate':
        return generate_schema(body)
    
    return {'statusCode': 400, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Unknown action'}), 'isBase64Encoded': False}


def generate_schema(body):
    spec = body.get('spec', {})
    db_spec = spec.get('database', {})
    ai_model = body.get('ai_model', 'anthropic/claude-sonnet-4')
    
    if not db_spec or not db_spec.get('tables'):
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'files': {}, 'tables_created': [], 'message': 'Нет требований к БД'}),
            'isBase64Encoded': False
        }
    
    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    
    if api_key:
        result = call_openrouter(db_spec, spec, ai_model, api_key)
        if result:
            return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}
    
    result = generate_fallback(db_spec)
    return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}


def call_openrouter(db_spec, full_spec, ai_model, api_key):
    system_prompt = """Ты — специалист по базам данных PostgreSQL. 
Сгенерируй SQL-миграцию на основе спецификации.

Требования:
- Используй SERIAL для PRIMARY KEY
- Добавь created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP и updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP к каждой таблице
- Создай все FOREIGN KEY с ON DELETE CASCADE (используй ALTER TABLE для FK, а не inline)
- Создай индексы для часто запрашиваемых полей
- Если есть auth, создай таблицу users с: id, email (UNIQUE), password_hash, username, created_at, updated_at
- Используй IF NOT EXISTS

Верни ТОЛЬКО валидный JSON: {"migration_sql": "...", "tables_created": ["table1", "table2"]}"""

    user_prompt = f"Спецификация базы данных:\n{json.dumps(db_spec, ensure_ascii=False, indent=2)}\n\nПолная спецификация приложения:\n{json.dumps(full_spec, ensure_ascii=False, indent=2)}"

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
                'temperature': 0.2,
                'max_tokens': 4000,
                'response_format': {'type': 'json_object'}
            },
            timeout=90
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        parsed = parse_json_response(content)
        
        if parsed and 'migration_sql' in parsed:
            return {
                'files': {'migration.sql': parsed['migration_sql']},
                'tables_created': parsed.get('tables_created', []),
                'ai_generated': True
            }
        return None
    except Exception:
        return None


def parse_json_response(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    import re
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


def generate_fallback(db_spec):
    tables = db_spec.get('tables', [])
    sql_parts = []
    tables_created = []
    
    for table in tables:
        name = table.get('name', 'unknown')
        columns = table.get('columns', [])
        tables_created.append(name)
        
        col_defs = []
        for col in columns:
            col_name = col.get('name', '')
            col_type = col.get('type', 'TEXT')
            col_defs.append(f"    {col_name} {col_type}")
        
        if not any('created_at' in c.get('name', '') for c in columns):
            col_defs.append("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            col_defs.append("    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        sql = f"CREATE TABLE IF NOT EXISTS {name} (\n"
        sql += ",\n".join(col_defs)
        sql += "\n);"
        sql_parts.append(sql)
    
    for idx in db_spec.get('indexes', []):
        sql_parts.append(idx + ";")
    
    migration_sql = "\n\n".join(sql_parts)
    
    return {
        'files': {'migration.sql': migration_sql},
        'tables_created': tables_created,
        'ai_generated': False
    }
