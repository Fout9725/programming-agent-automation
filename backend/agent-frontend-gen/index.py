import json
import os
import requests

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
}

SYSTEM_PROMPT = """Ты — senior React-разработчик. Генерируй код для poehali.dev платформы.

СТЕК:
- React 18 + TypeScript
- Tailwind CSS для стилизации
- shadcn/ui компоненты (Button, Card, Input, Label, Badge, Dialog и др.) из @/components/ui/
- React Router DOM v6 для навигации
- Импорт алиас: @/ -> src/
- Иконки: import Icon from '@/components/ui/icon'; <Icon name="Home" size={24} />
- Формы: используй useState для простых форм
- API: fetch() для вызова backend

ПРАВИЛА:
- Каждый файл должен иметь default export
- Используй функциональные компоненты с хуками
- Не используй any в TypeScript, указывай конкретные типы
- Не используй var, только const и let
- Добавляй адаптивные стили (mobile-first)
- Поддержка тёмной темы через CSS переменные (dark:)

Верни ТОЛЬКО валидный JSON: {"files": {"путь/к/файлу.tsx": "содержимое"}, "components": ["Component1"], "routes": [{"path": "/", "component": "Home", "import": "./pages/Home"}]}"""

FIX_PROMPT = """Ты — senior React-разработчик. Исправь ошибки в коде.

Для каждого файла с ошибками:
1. Прочитай текущий код
2. Прочитай список ошибок
3. Исправь все ошибки
4. Верни ПОЛНЫЙ исправленный файл

Верни ТОЛЬКО валидный JSON: {"files": {"путь/к/файлу.tsx": "исправленное содержимое"}}"""


def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': '', 'isBase64Encoded': False}
    
    if event.get('httpMethod') != 'POST':
        return {'statusCode': 405, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Method not allowed'}), 'isBase64Encoded': False}
    
    body = json.loads(event.get('body', '{}'))
    action = body.get('action', '')
    
    if action == 'generate':
        return generate_frontend(body)
    elif action == 'fix':
        return fix_code(body)
    
    return {'statusCode': 400, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Unknown action'}), 'isBase64Encoded': False}


def generate_frontend(body):
    spec = body.get('spec', {})
    frontend_spec = spec.get('frontend', {})
    backend_endpoints = body.get('backend_endpoints', spec.get('backend', {}).get('endpoints', []))
    ai_model = body.get('ai_model', 'anthropic/claude-sonnet-4')
    language = body.get('language', 'ru')
    
    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    
    user_prompt = f"""Создай React приложение по спецификации.

Спецификация Frontend:
{json.dumps(frontend_spec, ensure_ascii=False, indent=2)}

Backend API endpoints (для fetch вызовов):
{json.dumps(backend_endpoints, ensure_ascii=False, indent=2)}

Язык интерфейса: {'русский' if language == 'ru' else 'английский'}

Сгенерируй ВСЕ необходимые файлы:
- src/pages/*.tsx — страницы
- src/components/*.tsx — переиспользуемые компоненты
- src/hooks/*.ts — кастомные хуки (если нужно)
- src/lib/api.ts — API клиент с функциями для каждого endpoint"""

    if api_key:
        result = call_openrouter(SYSTEM_PROMPT, user_prompt, ai_model, api_key)
        if result:
            return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}
    
    result = generate_fallback(frontend_spec, backend_endpoints, language)
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

Список ошибок:
{json.dumps(issues, ensure_ascii=False, indent=2)}

Исправь ВСЕ ошибки и верни исправленные файлы."""

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
        
        if parsed and 'files' in parsed:
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


def generate_fallback(frontend_spec, backend_endpoints, language):
    pages = frontend_spec.get('pages', [{'path': '/', 'name': 'Home', 'components': []}])
    files = {}
    components = []
    routes = []
    
    for page in pages:
        name = page.get('name', 'Home')
        path = page.get('path', '/')
        components.append(name)
        routes.append({'path': path, 'component': name, 'import': f'./pages/{name}'})
        
        page_components = page.get('components', [])
        imports = "import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';\nimport { Button } from '@/components/ui/button';\nimport Icon from '@/components/ui/icon';\n"
        
        for comp in page_components:
            imports += f"import {comp} from '@/components/{comp}';\n"
        
        component_renders = '\n'.join([f'        <{c} />' for c in page_components]) if page_components else '        <p>Контент страницы</p>'
        
        files[f'src/pages/{name}.tsx'] = f"""{imports}
const {name} = () => {{
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">{name}</h1>
{component_renders}
    </div>
  );
}};

export default {name};
"""
    
    for page in pages:
        for comp in page.get('components', []):
            if comp not in components:
                components.append(comp)
            files[f'src/components/{comp}.tsx'] = f"""import {{ Card, CardContent }} from '@/components/ui/card';

const {comp} = () => {{
  return (
    <Card>
      <CardContent className="p-4">
        <p>{comp} component</p>
      </CardContent>
    </Card>
  );
}};

export default {comp};
"""
    
    if backend_endpoints:
        api_functions = []
        for ep in backend_endpoints:
            method = ep.get('method', 'GET')
            ep_path = ep.get('path', '/')
            func_name = ep_path.replace('/api/', '').replace('/', '_').strip('_')
            if not func_name:
                func_name = 'getData'
            
            if method == 'GET':
                api_functions.append(f"""export async function fetch_{func_name}() {{
  const response = await fetch(API_BASE + '{ep_path}');
  if (!response.ok) throw new Error('API error');
  return response.json();
}}""")
            else:
                api_functions.append(f"""export async function {method.lower()}_{func_name}(data: Record<string, unknown>) {{
  const response = await fetch(API_BASE + '{ep_path}', {{
    method: '{method}',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify(data)
  }});
  if (!response.ok) throw new Error('API error');
  return response.json();
}}""")
        
        files['src/lib/api.ts'] = f"""const API_BASE = '';\n\n""" + "\n\n".join(api_functions) + "\n"
    
    return {
        'files': files,
        'components': components,
        'routes': routes,
        'ai_generated': False
    }
