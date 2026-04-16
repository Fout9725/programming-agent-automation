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
BACKEND_MODEL = 'deepseek/deepseek-v3.2-exp-alt'

SYSTEM_PROMPT = """Ты — senior Python-разработчик. Генерируй Cloud Functions для poehali.dev.

ФОРМАТ (строго):
- def handler(event, context) -> dict
- OPTIONS для CORS первым
- psycopg2 + os.environ['DATABASE_URL']
- isBase64Encoded: False всегда
- Auth: event.get('headers', {}).get('X-Authorization', '')

Верни СТРОГО JSON:
{"files": {"backend/api-name/index.py": "код", "backend/api-name/requirements.txt": "psycopg2-binary", "backend/api-name/tests.json": "тесты"}, "functions": ["api-name"]}"""


def handler(event, context):
    """Агент Backend — генерация Python Cloud Functions через AI"""
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

    endpoints = backend_spec.get('endpoints', [])
    if not endpoints:
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps({'files': {}, 'functions': []}), 'isBase64Encoded': False}

    api_key = os.environ.get('VSEGPT_API_KEY', '')
    if api_key:
        result = call_ai(SYSTEM_PROMPT, f"Endpoints:\n{json.dumps(backend_spec, ensure_ascii=False, indent=2)}\n\nDB:\n{json.dumps(db_spec, ensure_ascii=False, indent=2)}", api_key)
        if result:
            if 'functions' in result and isinstance(result['functions'], dict):
                all_files = {}
                func_names = []
                for fn, fd in result['functions'].items():
                    func_names.append(fn)
                    if isinstance(fd, dict):
                        for f, c in fd.items():
                            all_files[f'backend/{fn}/{f}'] = c
                result['files'] = all_files
                result['functions'] = func_names
            return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}

    result = generate_fallback(backend_spec, db_spec)
    return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}


def fix_code(body):
    files = body.get('files', {})
    issues = body.get('issues', [])
    api_key = os.environ.get('VSEGPT_API_KEY', '')
    if not files or not issues:
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps({'files': files}), 'isBase64Encoded': False}
    if api_key:
        result = call_ai('Исправь ошибки. Верни JSON: {"files": {"путь": "код"}}', f"Файлы:\n{json.dumps(files, ensure_ascii=False)}\nОшибки:\n{json.dumps(issues, ensure_ascii=False)}", api_key)
        if result and 'files' in result:
            return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}
    return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps({'files': files}), 'isBase64Encoded': False}


def call_ai(system_prompt, user_prompt, api_key):
    try:
        resp = requests.post(VSEGPT_URL, headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={'model': BACKEND_MODEL, 'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ], 'max_tokens': 16384, 'temperature': 0.3}, timeout=120)
        if resp.status_code != 200:
            return None
        content = resp.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        parsed = parse_json(content)
        if parsed and ('files' in parsed or 'functions' in parsed):
            parsed['ai_generated'] = True
            return parsed
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


def generate_fallback(backend_spec, db_spec):
    endpoints = backend_spec.get('endpoints', [])
    groups = {}
    for ep in endpoints:
        path = ep.get('path', '/api/data')
        parts = path.strip('/').split('/')
        gname = re.sub(r'[^a-zA-Z0-9]', '', parts[1] if len(parts) > 1 else parts[0])
        fn = f"api-{gname}"
        if fn not in groups:
            groups[fn] = []
        groups[fn].append(ep)

    files = {}
    func_names = []
    tables = [t.get('name', 'data') for t in db_spec.get('tables', [])]
    default_table = tables[0] if tables else 'data'

    for fn, eps in groups.items():
        func_names.append(fn)
        entity = fn.replace('api-', '')
        tbl = entity if entity in tables else default_table
        methods = list(set(ep.get('method', 'GET') for ep in eps))

        blocks = []
        if 'GET' in methods:
            blocks.append(f"""    if method == 'GET':
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM {tbl} ORDER BY created_at DESC LIMIT 100")
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            return respond(200, {{'items': rows, 'count': len(rows)}})
        except Exception:
            return respond(200, {{'items': [], 'count': 0}})
        finally:
            conn.close()""")
        if 'POST' in methods:
            blocks.append(f"""    if method == 'POST':
        body = json.loads(event.get('body', '{{}}'))
        conn = get_db()
        try:
            cur = conn.cursor()
            keys = [k for k in body.keys() if k != 'id']
            vals = [body[k] for k in keys]
            cur.execute(f"INSERT INTO {tbl} ({{', '.join(keys)}}) VALUES ({{', '.join(['%s']*len(keys))}}) RETURNING id", vals)
            new_id = cur.fetchone()[0]
            conn.commit()
            return respond(201, {{'id': new_id}})
        finally:
            conn.close()""")
        if 'PUT' in methods:
            blocks.append(f"""    if method == 'PUT':
        body = json.loads(event.get('body', '{{}}'))
        item_id = body.pop('id', None)
        if not item_id:
            return respond(400, {{'error': 'id required'}})
        conn = get_db()
        try:
            cur = conn.cursor()
            sets = ', '.join([f"{{k}} = %s" for k in body.keys()])
            cur.execute(f"UPDATE {tbl} SET {{sets}} WHERE id = %s", list(body.values()) + [item_id])
            conn.commit()
            return respond(200, {{'message': 'Updated'}})
        finally:
            conn.close()""")
        if 'DELETE' in methods:
            blocks.append(f"""    if method == 'DELETE':
        item_id = (params or {{}}).get('id')
        if not item_id:
            return respond(400, {{'error': 'id required'}})
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM {tbl} WHERE id = %s", (item_id,))
            conn.commit()
            return respond(200, {{'message': 'Deleted'}})
        finally:
            conn.close()""")

        code = f'''import json
import os
import psycopg2

CORS_HEADERS = {{
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Authorization',
    'Content-Type': 'application/json'
}}

def get_db():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def respond(code, body):
    return {{'statusCode': code, 'headers': CORS_HEADERS, 'body': json.dumps(body, default=str), 'isBase64Encoded': False}}

def handler(event, context):
    """API для {entity}"""
    if event.get('httpMethod') == 'OPTIONS':
        return {{'statusCode': 200, 'headers': CORS_HEADERS, 'body': '', 'isBase64Encoded': False}}

    method = event.get('httpMethod', 'GET')
    params = event.get('queryStringParameters', {{}}) or {{}}

{chr(10).join(blocks)}

    return respond(405, {{'error': 'Method not allowed'}})
'''
        files[f'backend/{fn}/index.py'] = code
        files[f'backend/{fn}/requirements.txt'] = 'psycopg2-binary\npydantic>=2.5.0'
        tests = [{'name': 'OPTIONS', 'method': 'OPTIONS', 'path': '/', 'expectedStatus': 200}]
        if 'GET' in methods:
            tests.append({'name': 'GET', 'method': 'GET', 'path': '/', 'expectedStatus': 200})
        files[f'backend/{fn}/tests.json'] = json.dumps({'tests': tests})

    return {'files': files, 'functions': func_names, 'ai_generated': False}
