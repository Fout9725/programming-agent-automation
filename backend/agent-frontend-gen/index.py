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
FRONTEND_MODEL = 'qwen/qwen3-coder-next'

SYSTEM_PROMPT = """Ты — senior React/TypeScript разработчик. Генерируй полноценное React приложение.

СТЕК (строго фиксированный):
- React 18 + TypeScript
- Tailwind CSS для стилизации
- shadcn/ui компоненты: import { Button } from '@/components/ui/button'; import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'; import { Input } from '@/components/ui/input'; import { Label } from '@/components/ui/label'; import { Badge } from '@/components/ui/badge'; import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
- Иконки: import Icon from '@/components/ui/icon'; <Icon name="Home" size={24} />
- Алиас: @/ -> src/
- Роутинг: React Router DOM v6 (useNavigate, useParams, Link)
- API: fetch() с async/await

КРИТИЧЕСКИЕ ПРАВИЛА:
1. КАЖДЫЙ файл ОБЯЗАН иметь default export
2. Используй функциональные компоненты с хуками (useState, useEffect)
3. НЕ используй any, указывай типы
4. Компоненты должны быть ПОЛНЫМИ и РАБОЧИМИ — не заглушки
5. Страницы должны содержать реальную UI логику: формы, списки, карточки
6. Используй Tailwind классы для красивого UI: rounded-lg, shadow, p-4, gap-4 и т.д.
7. Поддержка тёмной темы: dark: классы
8. Мобильная адаптация: grid-cols-1 md:grid-cols-2 lg:grid-cols-3
9. API вызовы через fetch, оборачивай в try/catch
10. Каждый компонент минимум 30 строк кода (НЕ заглушки)

Верни СТРОГО JSON без пояснений:
{
  "files": {"src/pages/Home.tsx": "полный код компонента", "src/components/List.tsx": "полный код"},
  "components": ["Home", "List"],
  "routes": [{"path": "/", "component": "Home", "import": "./pages/Home"}]
}"""

FIX_PROMPT = """Исправь ошибки в React/TypeScript коде. Верни СТРОГО JSON: {"files": {"путь": "исправленный код"}}"""


def handler(event, context):
    """Агент Frontend — генерация React страниц и компонентов через AI"""
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
    language = body.get('language', 'ru')
    api_key = os.environ.get('VSEGPT_API_KEY', '')

    user_prompt = f"""Создай ПОЛНОЕ React приложение по спецификации.

Frontend спецификация:
{json.dumps(frontend_spec, ensure_ascii=False, indent=2)}

Backend API endpoints (используй в fetch вызовах):
{json.dumps(backend_endpoints, ensure_ascii=False, indent=2)}

Язык интерфейса: {'русский' if language == 'ru' else 'английский'}

ВАЖНО: Создай ПОЛНЫЙ рабочий код для КАЖДОГО файла. Каждый компонент должен содержать реальную логику, состояния, обработчики событий. НЕ заглушки."""

    if api_key:
        result = call_ai(SYSTEM_PROMPT, user_prompt, api_key)
        if result:
            return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}

    result = generate_fallback(frontend_spec, backend_endpoints, language)
    return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}


def fix_code(body):
    files = body.get('files', {})
    issues = body.get('issues', [])
    api_key = os.environ.get('VSEGPT_API_KEY', '')
    if not files or not issues:
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps({'files': files}), 'isBase64Encoded': False}

    if api_key:
        result = call_ai(FIX_PROMPT, f"Файлы:\n{json.dumps(files, ensure_ascii=False)}\n\nОшибки:\n{json.dumps(issues, ensure_ascii=False)}", api_key)
        if result and 'files' in result:
            return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result), 'isBase64Encoded': False}
    return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps({'files': files}), 'isBase64Encoded': False}


def call_ai(system_prompt, user_prompt, api_key):
    try:
        resp = requests.post(VSEGPT_URL, headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={'model': FRONTEND_MODEL, 'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ], 'max_tokens': 16384, 'temperature': 0.3}, timeout=120)
        if resp.status_code != 200:
            return None
        content = resp.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        parsed = parse_json(content)
        if parsed and 'files' in parsed:
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


def generate_fallback(frontend_spec, backend_endpoints, language):
    pages = frontend_spec.get('pages', [{'path': '/', 'name': 'Home', 'components': []}])
    files = {}
    components = []
    routes = []

    for page in pages:
        name = page.get('name', 'Home')
        path = page.get('path', '/')
        page_comps = page.get('components', [])
        components.append(name)
        routes.append({'path': path, 'component': name, 'import': f'./pages/{name}'})

        comp_imports = "\n".join([f"import {c} from '@/components/{c}';" for c in page_comps])
        comp_renders = "\n".join([f"          <{c} />" for c in page_comps]) or "          <p className=\"text-muted-foreground\">Содержимое страницы</p>"

        files[f'src/pages/{name}.tsx'] = f"""import {{ useState }} from 'react';
import {{ Card, CardContent, CardHeader, CardTitle }} from '@/components/ui/card';
import {{ Button }} from '@/components/ui/button';
import Icon from '@/components/ui/icon';
{comp_imports}

const {name} = () => {{
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">{name}</h1>
        </div>
      </header>
      <main className="container mx-auto px-4 py-6">
        <div className="space-y-6">
{comp_renders}
        </div>
      </main>
    </div>
  );
}};

export default {name};
"""

    for page in pages:
        for comp in page.get('components', []):
            if comp not in components:
                components.append(comp)
            desc = comp
            for c in frontend_spec.get('components', []):
                if c.get('name') == comp:
                    desc = c.get('description', comp)
                    break

            files[f'src/components/{comp}.tsx'] = f"""import {{ useState }} from 'react';
import {{ Card, CardContent, CardHeader, CardTitle }} from '@/components/ui/card';
import {{ Button }} from '@/components/ui/button';
import {{ Input }} from '@/components/ui/input';
import Icon from '@/components/ui/icon';

const {comp} = () => {{
  const [loading, setLoading] = useState(false);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Icon name="Layout" size={{20}} />
          {desc}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">{desc}</p>
          <Button onClick={{() => setLoading(!loading)}} variant="outline">
            {{loading ? 'Загрузка...' : 'Обновить'}}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}};

export default {comp};
"""

    if backend_endpoints:
        api_funcs = []
        for ep in backend_endpoints:
            method = ep.get('method', 'GET')
            ep_path = ep.get('path', '/')
            func_name = ep_path.replace('/api/', '').replace('/', '_').replace(':', '').strip('_') or 'data'
            if method == 'GET':
                api_funcs.append(f"export async function fetch_{func_name}() {{\n  const r = await fetch(API_BASE + '{ep_path}');\n  if (!r.ok) throw new Error('API error');\n  return r.json();\n}}")
            else:
                api_funcs.append(f"export async function {method.lower()}_{func_name}(data: Record<string, unknown>) {{\n  const r = await fetch(API_BASE + '{ep_path}', {{\n    method: '{method}',\n    headers: {{'Content-Type': 'application/json'}},\n    body: JSON.stringify(data)\n  }});\n  if (!r.ok) throw new Error('API error');\n  return r.json();\n}}")
        files['src/lib/api.ts'] = "const API_BASE = '';\n\n" + "\n\n".join(api_funcs) + "\n"

    return {'files': files, 'components': components, 'routes': routes, 'ai_generated': False}
