import json
import os
import re
import requests
from typing import Dict, List

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Authorization',
    'Content-Type': 'application/json'
}

OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
DEFAULT_MODEL = 'anthropic/claude-sonnet-4'

SYSTEM_PROMPT = """Ты — ведущий архитектор веб-приложений. Проанализируй запрос пользователя и создай детальную техническую спецификацию для веб-приложения.

Стек технологий:
- Frontend: React 18 + TypeScript + Tailwind CSS + shadcn/ui
- Backend: Python Cloud Functions (def handler(event, context) -> dict)
- Database: PostgreSQL
- Иконки: lucide-react через <Icon name="..." />
- Роутинг: React Router DOM v6

Верни ТОЛЬКО валидный JSON (без markdown) со структурой:
{
  "spec": {
    "app_name": "string",
    "description": "string",
    "frontend": {
      "pages": [{"path": "/", "name": "Home", "components": ["Component1"]}],
      "components": [{"name": "Component1", "description": "описание компонента"}],
      "styling": "Tailwind CSS + shadcn/ui"
    },
    "backend": {
      "endpoints": [{"method": "GET", "path": "/api/items", "description": "описание"}],
      "auth_type": "none или JWT",
      "functions": ["api-items"]
    },
    "database": {
      "tables": [{"name": "items", "columns": [{"name": "id", "type": "SERIAL PRIMARY KEY"}]}],
      "indexes": []
    },
    "features": ["dark_theme", "auth"]
  },
  "estimated_time": 30,
  "estimated_cost": 0.30
}

Правила:
- app_name должно быть короткое латинское название через дефис
- Каждая страница должна иметь минимум 1 компонент
- Каждый endpoint должен соответствовать Cloud Function
- estimated_time в секундах (обычно 20-120)
- estimated_cost в USD (обычно 0.05-1.00)
- features — массив ключевых фич приложения
- Если запрос простой (лендинг), не добавляй лишнюю БД и авторизацию
- Верни ТОЛЬКО JSON, без markdown-обёрток и пояснений"""


def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': '', 'isBase64Encoded': False}

    method = event.get('httpMethod', 'GET')

    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }

    body = json.loads(event.get('body', '{}'))
    action = body.get('action', 'interpret')

    if action == 'interpret':
        return interpret_request(body)
    elif action == 'generate':
        return generate_project(body)

    return {
        'statusCode': 400,
        'headers': CORS_HEADERS,
        'body': json.dumps({'error': 'Invalid action. Use: interpret or generate'}),
        'isBase64Encoded': False
    }


def interpret_request(body: dict) -> dict:
    user_query = body.get('user_query', '')
    if not user_query:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'user_query обязателен'}),
            'isBase64Encoded': False
        }

    ai_model = body.get('ai_model', DEFAULT_MODEL)
    language = body.get('language', 'ru')

    spec_data = None
    ai_used = False

    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    if api_key:
        spec_data = call_openrouter(api_key, ai_model, user_query, language)
        if spec_data:
            ai_used = True

    if not spec_data:
        spec_data = generate_fallback_spec(user_query)

    result = spec_data
    result['ai_generated'] = ai_used

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps(result, ensure_ascii=False),
        'isBase64Encoded': False
    }


def call_openrouter(api_key: str, model: str, user_query: str, language: str) -> dict:
    lang_hint = ''
    if language == 'ru':
        lang_hint = '\nОтвечай на русском языке в полях description.'
    elif language == 'en':
        lang_hint = '\nUse English for description fields.'

    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT + lang_hint},
        {'role': 'user', 'content': user_query}
    ]

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://poehali.dev',
        'X-Title': 'Poehali AI Builder'
    }

    payload = {
        'model': model,
        'messages': messages,
        'max_tokens': 4096,
        'temperature': 0.3,
        'response_format': {'type': 'json_object'}
    }

    try:
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=90)
        if response.status_code != 200:
            return None

        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        if not content:
            return None

        parsed = parse_ai_response(content)
        if not parsed:
            return None

        if 'spec' not in parsed:
            return None

        spec = parsed['spec']
        if 'frontend' not in spec or 'pages' not in spec.get('frontend', {}):
            return None

        return parsed

    except (requests.Timeout, requests.ConnectionError, requests.RequestException):
        return None
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        return None


def parse_ai_response(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    brace_start = content.find('{')
    brace_end = content.rfind('}')
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        try:
            return json.loads(content[brace_start:brace_end + 1])
        except json.JSONDecodeError:
            pass

    return None


def generate_fallback_spec(user_query: str) -> dict:
    query_lower = user_query.lower()

    app_name = 'new-app'
    if any(w in query_lower for w in ['магазин', 'shop', 'store']):
        app_name = 'web-store'
    elif any(w in query_lower for w in ['блог', 'blog']):
        app_name = 'blog-app'
    elif any(w in query_lower for w in ['чат', 'chat', 'мессенджер']):
        app_name = 'chat-app'
    elif any(w in query_lower for w in ['crm', 'dashboard', 'панель']):
        app_name = 'admin-dashboard'
    elif any(w in query_lower for w in ['лендинг', 'landing']):
        app_name = 'landing-page'

    pages = extract_pages(query_lower)
    components = extract_components(query_lower)
    endpoints = extract_endpoints(query_lower)
    tables = extract_tables(query_lower)
    features = extract_features(query_lower)
    auth_type = detect_auth(query_lower)
    functions = [e['path'].replace('/api/', 'api-').replace('/', '-').strip('-') for e in endpoints]

    spec = {
        'app_name': app_name,
        'description': user_query,
        'frontend': {
            'pages': pages,
            'components': components,
            'styling': 'Tailwind CSS + shadcn/ui'
        },
        'backend': {
            'endpoints': endpoints,
            'auth_type': auth_type,
            'functions': functions
        },
        'database': {
            'tables': tables,
            'indexes': []
        },
        'features': features
    }

    time_estimate = 20 + len(pages) * 10 + len(endpoints) * 5 + len(tables) * 5
    cost_estimate = round(0.05 + len(pages) * 0.03 + len(endpoints) * 0.02, 2)

    return {
        'spec': spec,
        'estimated_time': time_estimate,
        'estimated_cost': cost_estimate
    }


def extract_pages(q: str) -> List[Dict]:
    pages = [{'path': '/', 'name': 'Home', 'components': ['Hero', 'Features']}]

    if any(w in q for w in ['магазин', 'shop', 'store', 'товар', 'product']):
        pages = [
            {'path': '/', 'name': 'Catalog', 'components': ['ProductGrid', 'SearchBar', 'Filters']},
            {'path': '/product/:id', 'name': 'ProductDetail', 'components': ['ProductInfo', 'Gallery', 'AddToCart']}
        ]

    if any(w in q for w in ['корзин', 'cart']):
        pages.append({'path': '/cart', 'name': 'Cart', 'components': ['CartList', 'CartSummary']})

    if any(w in q for w in ['оплат', 'checkout', 'payment']):
        pages.append({'path': '/checkout', 'name': 'Checkout', 'components': ['CheckoutForm', 'OrderSummary']})

    if any(w in q for w in ['админ', 'admin', 'dashboard', 'панель']):
        pages.append({'path': '/admin', 'name': 'Admin', 'components': ['AdminSidebar', 'DataTable', 'Stats']})

    if any(w in q for w in ['профиль', 'account', 'кабинет']):
        pages.append({'path': '/profile', 'name': 'Profile', 'components': ['ProfileForm', 'OrderHistory']})

    if any(w in q for w in ['вход', 'login', 'регистр', 'signup', 'auth']):
        pages.append({'path': '/login', 'name': 'Login', 'components': ['LoginForm']})
        pages.append({'path': '/register', 'name': 'Register', 'components': ['RegisterForm']})

    if any(w in q for w in ['блог', 'blog', 'стать', 'article']):
        pages.append({'path': '/blog', 'name': 'Blog', 'components': ['PostList', 'PostCard']})
        pages.append({'path': '/blog/:id', 'name': 'BlogPost', 'components': ['PostContent', 'Comments']})

    if any(w in q for w in ['контакт', 'contact', 'обратн', 'feedback']):
        pages.append({'path': '/contact', 'name': 'Contact', 'components': ['ContactForm']})

    return pages


def extract_components(q: str) -> List[Dict]:
    components = [
        {'name': 'Header', 'description': 'Шапка сайта с навигацией'},
        {'name': 'Footer', 'description': 'Подвал сайта'}
    ]

    if any(w in q for w in ['магазин', 'shop', 'товар']):
        components.extend([
            {'name': 'ProductCard', 'description': 'Карточка товара'},
            {'name': 'ProductGrid', 'description': 'Сетка товаров'},
            {'name': 'SearchBar', 'description': 'Поиск по каталогу'},
            {'name': 'Filters', 'description': 'Фильтры каталога'}
        ])

    if any(w in q for w in ['корзин', 'cart']):
        components.extend([
            {'name': 'CartList', 'description': 'Список товаров в корзине'},
            {'name': 'CartSummary', 'description': 'Итого корзины'}
        ])

    if any(w in q for w in ['форм', 'form', 'контакт', 'обратн']):
        components.append({'name': 'ContactForm', 'description': 'Форма обратной связи'})

    if any(w in q for w in ['таблиц', 'table', 'данн']):
        components.append({'name': 'DataTable', 'description': 'Таблица данных с сортировкой'})

    return components


def extract_endpoints(q: str) -> List[Dict]:
    endpoints = []

    if any(w in q for w in ['магазин', 'shop', 'товар', 'product']):
        endpoints.extend([
            {'method': 'GET', 'path': '/api/products', 'description': 'Список товаров'},
            {'method': 'GET', 'path': '/api/products/:id', 'description': 'Детали товара'}
        ])

    if any(w in q for w in ['корзин', 'cart']):
        endpoints.extend([
            {'method': 'GET', 'path': '/api/cart', 'description': 'Получить корзину'},
            {'method': 'POST', 'path': '/api/cart', 'description': 'Добавить в корзину'}
        ])

    if any(w in q for w in ['заказ', 'order', 'оплат']):
        endpoints.append({'method': 'POST', 'path': '/api/orders', 'description': 'Создать заказ'})

    if any(w in q for w in ['контакт', 'contact', 'обратн', 'feedback']):
        endpoints.append({'method': 'POST', 'path': '/api/contact', 'description': 'Отправить сообщение'})

    if any(w in q for w in ['auth', 'вход', 'login', 'регистр']):
        endpoints.extend([
            {'method': 'POST', 'path': '/api/auth/login', 'description': 'Авторизация'},
            {'method': 'POST', 'path': '/api/auth/register', 'description': 'Регистрация'}
        ])

    if any(w in q for w in ['блог', 'blog', 'стать']):
        endpoints.extend([
            {'method': 'GET', 'path': '/api/posts', 'description': 'Список статей'},
            {'method': 'GET', 'path': '/api/posts/:id', 'description': 'Статья'}
        ])

    return endpoints


def extract_tables(q: str) -> List[Dict]:
    tables = []

    if any(w in q for w in ['auth', 'вход', 'login', 'регистр', 'пользовател', 'user']):
        tables.append({
            'name': 'users',
            'columns': [
                {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                {'name': 'email', 'type': 'VARCHAR(255) UNIQUE NOT NULL'},
                {'name': 'password_hash', 'type': 'VARCHAR(255) NOT NULL'},
                {'name': 'name', 'type': 'VARCHAR(255)'},
                {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
            ]
        })

    if any(w in q for w in ['магазин', 'shop', 'товар', 'product']):
        tables.append({
            'name': 'products',
            'columns': [
                {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                {'name': 'name', 'type': 'VARCHAR(255) NOT NULL'},
                {'name': 'description', 'type': 'TEXT'},
                {'name': 'price', 'type': 'DECIMAL(10,2) NOT NULL'},
                {'name': 'image_url', 'type': 'VARCHAR(500)'},
                {'name': 'stock', 'type': 'INTEGER DEFAULT 0'},
                {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
            ]
        })

    if any(w in q for w in ['заказ', 'order']):
        tables.append({
            'name': 'orders',
            'columns': [
                {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                {'name': 'user_id', 'type': 'INTEGER REFERENCES users(id)'},
                {'name': 'total_amount', 'type': 'DECIMAL(10,2) NOT NULL'},
                {'name': 'status', 'type': "VARCHAR(50) DEFAULT 'pending'"},
                {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
            ]
        })

    if any(w in q for w in ['блог', 'blog', 'стать', 'article']):
        tables.append({
            'name': 'posts',
            'columns': [
                {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                {'name': 'title', 'type': 'VARCHAR(255) NOT NULL'},
                {'name': 'content', 'type': 'TEXT NOT NULL'},
                {'name': 'author_id', 'type': 'INTEGER'},
                {'name': 'published_at', 'type': 'TIMESTAMP'},
                {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
            ]
        })

    if any(w in q for w in ['контакт', 'contact', 'обратн', 'feedback']):
        tables.append({
            'name': 'messages',
            'columns': [
                {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                {'name': 'name', 'type': 'VARCHAR(255)'},
                {'name': 'email', 'type': 'VARCHAR(255)'},
                {'name': 'message', 'type': 'TEXT NOT NULL'},
                {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
            ]
        })

    return tables


def extract_features(q: str) -> List[str]:
    features = ['responsive']

    if any(w in q for w in ['тёмн', 'темн', 'dark', 'theme']):
        features.append('dark_theme')

    if any(w in q for w in ['auth', 'вход', 'login', 'регистр']):
        features.append('auth')

    if any(w in q for w in ['поиск', 'search']):
        features.append('search')

    if any(w in q for w in ['фильтр', 'filter']):
        features.append('filters')

    if any(w in q for w in ['пагинац', 'pagination', 'страниц']):
        features.append('pagination')

    if any(w in q for w in ['корзин', 'cart']):
        features.append('cart')

    if any(w in q for w in ['оплат', 'payment']):
        features.append('payment')

    if any(w in q for w in ['уведомлен', 'notification']):
        features.append('notifications')

    return features


def detect_auth(q: str) -> str:
    if any(w in q for w in ['auth', 'вход', 'login', 'регистр', 'админ', 'admin', 'кабинет', 'профиль']):
        return 'JWT'
    return 'none'


def generate_project(body: dict) -> dict:
    spec = body.get('spec', {})
    project_id = body.get('project_id', '')

    if not spec or not project_id:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'spec and project_id are required'}),
            'isBase64Encoded': False
        }

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({
            'status': 'queued',
            'project_id': project_id,
            'message': 'Project generation started'
        }),
        'isBase64Encoded': False
    }
