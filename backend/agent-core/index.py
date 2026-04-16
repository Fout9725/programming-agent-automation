import json
import os
import re
import requests

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Authorization',
    'Content-Type': 'application/json'
}

VSEGPT_URL = 'https://api.vsegpt.ru/v1/chat/completions'
ARCHITECT_MODEL = 'deepseek/deepseek-v3.2-speciale-alt'

SYSTEM_PROMPT = """Ты — ведущий архитектор веб-приложений с 15-летним опытом. Твоя задача — проанализировать запрос пользователя и создать ПОЛНУЮ техническую спецификацию для веб-приложения.

СТЕК ТЕХНОЛОГИЙ (строго фиксированный):
- Frontend: React 18 + TypeScript + Tailwind CSS + shadcn/ui (компоненты: Button, Card, Input, Label, Badge, Dialog, Tabs, Table и др.)
- Backend: Python 3.11 Cloud Functions (формат: def handler(event, context) -> dict)
- Database: PostgreSQL (через psycopg2, Simple Query Protocol)
- Иконки: lucide-react через компонент <Icon name="IconName" size={24} />
- Роутинг: React Router DOM v6
- Стилизация: Tailwind CSS + CSS переменные для темизации

КРИТИЧЕСКИЕ ПРАВИЛА:
1. Каждое приложение ДОЛЖНО иметь минимум 2-3 страницы
2. Каждая страница ДОЛЖНА иметь минимум 2-3 компонента
3. Если приложение работает с данными — ОБЯЗАТЕЛЬНО нужна БД (таблицы, колонки)
4. Если есть БД — ОБЯЗАТЕЛЬНО нужны API endpoints (CRUD операции)
5. app_name — короткое латинское название через дефис (например: todo-app, chat-room)
6. Для каждой таблицы ОБЯЗАТЕЛЬНО указывай ВСЕ колонки с типами PostgreSQL
7. Для каждого endpoint указывай method, path и описание
8. features — реальные функции приложения

ОБЯЗАТЕЛЬНО верни ТОЛЬКО валидный JSON без каких-либо пояснений, без markdown:
{
  "spec": {
    "app_name": "todo-app",
    "description": "Приложение для управления задачами",
    "frontend": {
      "pages": [
        {"path": "/", "name": "Home", "components": ["TaskList", "AddTaskForm", "FilterBar"]},
        {"path": "/login", "name": "Login", "components": ["LoginForm", "RegisterLink"]}
      ],
      "components": [
        {"name": "TaskList", "description": "Список задач с фильтрацией и сортировкой"},
        {"name": "AddTaskForm", "description": "Форма добавления новой задачи"}
      ],
      "styling": "Tailwind CSS + shadcn/ui"
    },
    "backend": {
      "endpoints": [
        {"method": "GET", "path": "/api/tasks", "description": "Получить все задачи"},
        {"method": "POST", "path": "/api/tasks", "description": "Создать задачу"},
        {"method": "PUT", "path": "/api/tasks", "description": "Обновить задачу"},
        {"method": "DELETE", "path": "/api/tasks", "description": "Удалить задачу"}
      ],
      "auth_type": "JWT",
      "functions": ["api-tasks", "api-auth"]
    },
    "database": {
      "tables": [
        {
          "name": "users",
          "columns": [
            {"name": "id", "type": "SERIAL PRIMARY KEY"},
            {"name": "email", "type": "VARCHAR(255) UNIQUE NOT NULL"},
            {"name": "password_hash", "type": "TEXT NOT NULL"},
            {"name": "username", "type": "VARCHAR(100)"},
            {"name": "created_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"}
          ]
        },
        {
          "name": "tasks",
          "columns": [
            {"name": "id", "type": "SERIAL PRIMARY KEY"},
            {"name": "user_id", "type": "INTEGER REFERENCES users(id)"},
            {"name": "title", "type": "VARCHAR(255) NOT NULL"},
            {"name": "completed", "type": "BOOLEAN DEFAULT FALSE"},
            {"name": "created_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"}
          ]
        }
      ],
      "indexes": ["CREATE INDEX idx_tasks_user_id ON tasks(user_id)"]
    },
    "features": ["crud_tasks", "auth", "dark_theme", "responsive"]
  },
  "estimated_time": 45,
  "estimated_cost": 0.25
}"""


def handler(event, context):
    """Архитектор — анализ запроса и создание технической спецификации через AI"""
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': '', 'isBase64Encoded': False}

    if event.get('httpMethod') != 'POST':
        return {'statusCode': 405, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Method not allowed'}), 'isBase64Encoded': False}

    body = json.loads(event.get('body', '{}'))
    action = body.get('action', 'interpret')

    if action == 'interpret':
        return interpret_request(body)

    return {'statusCode': 400, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Invalid action'}), 'isBase64Encoded': False}


def interpret_request(body):
    user_query = body.get('user_query', '')
    if not user_query:
        return {'statusCode': 400, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'user_query обязателен'}), 'isBase64Encoded': False}

    language = body.get('language', 'ru')
    api_key = os.environ.get('VSEGPT_API_KEY', '')

    spec_data = None
    if api_key:
        spec_data = call_vsegpt(api_key, user_query, language)

    if not spec_data:
        spec_data = generate_fallback_spec(user_query)
        spec_data['ai_generated'] = False
    else:
        spec_data['ai_generated'] = True

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps(spec_data, ensure_ascii=False),
        'isBase64Encoded': False
    }


def call_vsegpt(api_key, user_query, language):
    lang_hint = '\nВсе описания пиши на русском языке.' if language == 'ru' else '\nUse English for descriptions.'

    try:
        response = requests.post(
            VSEGPT_URL,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': ARCHITECT_MODEL,
                'messages': [
                    {'role': 'system', 'content': SYSTEM_PROMPT + lang_hint},
                    {'role': 'user', 'content': f'Создай полную спецификацию для: {user_query}'}
                ],
                'max_tokens': 8192,
                'temperature': 0.3
            },
            timeout=120
        )

        if response.status_code != 200:
            return None

        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        if not content:
            return None

        parsed = parse_json(content)
        if not parsed or 'spec' not in parsed:
            return None

        spec = parsed['spec']
        if 'frontend' not in spec or not spec.get('frontend', {}).get('pages'):
            return None

        return parsed

    except Exception:
        return None


def parse_json(text):
    text = text.strip()
    if text.startswith('```'):
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return None


def generate_fallback_spec(user_query):
    q = user_query.lower()

    if any(w in q for w in ['магазин', 'shop', 'store', 'товар']):
        return fallback_store(user_query)
    elif any(w in q for w in ['чат', 'chat', 'мессенджер', 'сообщен']):
        return fallback_chat(user_query)
    elif any(w in q for w in ['todo', 'задач', 'task', 'список']):
        return fallback_todo(user_query)
    elif any(w in q for w in ['блог', 'blog', 'стать', 'пост']):
        return fallback_blog(user_query)
    elif any(w in q for w in ['crm', 'dashboard', 'панель', 'админ']):
        return fallback_crm(user_query)
    else:
        return fallback_generic(user_query)


def fallback_todo(q):
    return {
        'spec': {
            'app_name': 'todo-app',
            'description': q,
            'frontend': {
                'pages': [
                    {'path': '/', 'name': 'Home', 'components': ['TaskList', 'AddTaskForm', 'FilterBar']},
                    {'path': '/settings', 'name': 'Settings', 'components': ['ThemeToggle', 'ProfileForm']}
                ],
                'components': [
                    {'name': 'TaskList', 'description': 'Список задач с чекбоксами'},
                    {'name': 'AddTaskForm', 'description': 'Форма добавления задачи'},
                    {'name': 'FilterBar', 'description': 'Фильтр по статусу'},
                    {'name': 'ThemeToggle', 'description': 'Переключатель темы'},
                    {'name': 'ProfileForm', 'description': 'Настройки профиля'}
                ],
                'styling': 'Tailwind CSS + shadcn/ui'
            },
            'backend': {
                'endpoints': [
                    {'method': 'GET', 'path': '/api/tasks', 'description': 'Получить задачи'},
                    {'method': 'POST', 'path': '/api/tasks', 'description': 'Создать задачу'},
                    {'method': 'PUT', 'path': '/api/tasks', 'description': 'Обновить задачу'},
                    {'method': 'DELETE', 'path': '/api/tasks', 'description': 'Удалить задачу'}
                ],
                'auth_type': 'none',
                'functions': ['api-tasks']
            },
            'database': {
                'tables': [
                    {'name': 'tasks', 'columns': [
                        {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                        {'name': 'title', 'type': 'VARCHAR(255) NOT NULL'},
                        {'name': 'description', 'type': 'TEXT'},
                        {'name': 'completed', 'type': 'BOOLEAN DEFAULT FALSE'},
                        {'name': 'priority', 'type': 'VARCHAR(20) DEFAULT \'medium\''},
                        {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                    ]}
                ],
                'indexes': []
            },
            'features': ['crud_tasks', 'filters', 'dark_theme', 'responsive']
        },
        'estimated_time': 35,
        'estimated_cost': 0.15
    }


def fallback_store(q):
    return {
        'spec': {
            'app_name': 'web-store',
            'description': q,
            'frontend': {
                'pages': [
                    {'path': '/', 'name': 'Catalog', 'components': ['ProductGrid', 'SearchBar', 'CategoryFilter']},
                    {'path': '/cart', 'name': 'Cart', 'components': ['CartItems', 'OrderSummary', 'CheckoutButton']},
                    {'path': '/product/:id', 'name': 'ProductDetail', 'components': ['ProductInfo', 'AddToCartButton']}
                ],
                'components': [
                    {'name': 'ProductGrid', 'description': 'Сетка товаров с картинками и ценами'},
                    {'name': 'SearchBar', 'description': 'Поиск по товарам'},
                    {'name': 'CategoryFilter', 'description': 'Фильтр по категориям'},
                    {'name': 'CartItems', 'description': 'Список товаров в корзине'},
                    {'name': 'OrderSummary', 'description': 'Итого к оплате'},
                    {'name': 'ProductInfo', 'description': 'Детальная карточка товара'},
                    {'name': 'AddToCartButton', 'description': 'Кнопка добавления в корзину'},
                    {'name': 'CheckoutButton', 'description': 'Оформление заказа'}
                ],
                'styling': 'Tailwind CSS + shadcn/ui'
            },
            'backend': {
                'endpoints': [
                    {'method': 'GET', 'path': '/api/products', 'description': 'Список товаров'},
                    {'method': 'GET', 'path': '/api/products/:id', 'description': 'Один товар'},
                    {'method': 'POST', 'path': '/api/cart', 'description': 'Добавить в корзину'},
                    {'method': 'GET', 'path': '/api/cart', 'description': 'Получить корзину'},
                    {'method': 'POST', 'path': '/api/orders', 'description': 'Оформить заказ'}
                ],
                'auth_type': 'none',
                'functions': ['api-products', 'api-cart', 'api-orders']
            },
            'database': {
                'tables': [
                    {'name': 'products', 'columns': [
                        {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                        {'name': 'name', 'type': 'VARCHAR(255) NOT NULL'},
                        {'name': 'description', 'type': 'TEXT'},
                        {'name': 'price', 'type': 'NUMERIC(10,2) NOT NULL'},
                        {'name': 'image_url', 'type': 'VARCHAR(500)'},
                        {'name': 'category', 'type': 'VARCHAR(100)'},
                        {'name': 'in_stock', 'type': 'BOOLEAN DEFAULT TRUE'},
                        {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                    ]},
                    {'name': 'orders', 'columns': [
                        {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                        {'name': 'items', 'type': 'JSONB NOT NULL'},
                        {'name': 'total', 'type': 'NUMERIC(10,2) NOT NULL'},
                        {'name': 'status', 'type': 'VARCHAR(50) DEFAULT \'pending\''},
                        {'name': 'customer_name', 'type': 'VARCHAR(255)'},
                        {'name': 'customer_email', 'type': 'VARCHAR(255)'},
                        {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                    ]}
                ],
                'indexes': ['CREATE INDEX idx_products_category ON products(category)']
            },
            'features': ['catalog', 'cart', 'checkout', 'search', 'categories', 'responsive']
        },
        'estimated_time': 60,
        'estimated_cost': 0.35
    }


def fallback_chat(q):
    return {
        'spec': {
            'app_name': 'chat-app',
            'description': q,
            'frontend': {
                'pages': [
                    {'path': '/', 'name': 'ChatRooms', 'components': ['RoomList', 'CreateRoomForm', 'OnlineCount']},
                    {'path': '/room/:id', 'name': 'ChatRoom', 'components': ['MessageList', 'MessageInput', 'UserList']}
                ],
                'components': [
                    {'name': 'RoomList', 'description': 'Список чат-комнат'},
                    {'name': 'CreateRoomForm', 'description': 'Форма создания комнаты'},
                    {'name': 'OnlineCount', 'description': 'Количество онлайн'},
                    {'name': 'MessageList', 'description': 'Список сообщений'},
                    {'name': 'MessageInput', 'description': 'Поле ввода сообщения'},
                    {'name': 'UserList', 'description': 'Список участников комнаты'}
                ],
                'styling': 'Tailwind CSS + shadcn/ui'
            },
            'backend': {
                'endpoints': [
                    {'method': 'GET', 'path': '/api/rooms', 'description': 'Список комнат'},
                    {'method': 'POST', 'path': '/api/rooms', 'description': 'Создать комнату'},
                    {'method': 'GET', 'path': '/api/messages', 'description': 'Сообщения комнаты'},
                    {'method': 'POST', 'path': '/api/messages', 'description': 'Отправить сообщение'}
                ],
                'auth_type': 'none',
                'functions': ['api-rooms', 'api-messages']
            },
            'database': {
                'tables': [
                    {'name': 'rooms', 'columns': [
                        {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                        {'name': 'name', 'type': 'VARCHAR(200) NOT NULL'},
                        {'name': 'description', 'type': 'TEXT'},
                        {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                    ]},
                    {'name': 'messages', 'columns': [
                        {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                        {'name': 'room_id', 'type': 'INTEGER REFERENCES rooms(id)'},
                        {'name': 'username', 'type': 'VARCHAR(100) NOT NULL'},
                        {'name': 'content', 'type': 'TEXT NOT NULL'},
                        {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                    ]}
                ],
                'indexes': ['CREATE INDEX idx_messages_room_id ON messages(room_id)']
            },
            'features': ['chat_rooms', 'real_time_messages', 'room_creation', 'responsive']
        },
        'estimated_time': 50,
        'estimated_cost': 0.30
    }


def fallback_blog(q):
    return {
        'spec': {
            'app_name': 'blog-app',
            'description': q,
            'frontend': {
                'pages': [
                    {'path': '/', 'name': 'Home', 'components': ['PostList', 'SearchBar', 'TagCloud']},
                    {'path': '/post/:id', 'name': 'PostDetail', 'components': ['PostContent', 'CommentList', 'CommentForm']},
                    {'path': '/create', 'name': 'CreatePost', 'components': ['PostEditor', 'PreviewPanel']}
                ],
                'components': [
                    {'name': 'PostList', 'description': 'Список статей с превью'},
                    {'name': 'SearchBar', 'description': 'Поиск по статьям'},
                    {'name': 'TagCloud', 'description': 'Облако тегов'},
                    {'name': 'PostContent', 'description': 'Полный текст статьи'},
                    {'name': 'CommentList', 'description': 'Комментарии'},
                    {'name': 'CommentForm', 'description': 'Форма комментария'},
                    {'name': 'PostEditor', 'description': 'Редактор статьи'},
                    {'name': 'PreviewPanel', 'description': 'Превью статьи'}
                ],
                'styling': 'Tailwind CSS + shadcn/ui'
            },
            'backend': {
                'endpoints': [
                    {'method': 'GET', 'path': '/api/posts', 'description': 'Список статей'},
                    {'method': 'POST', 'path': '/api/posts', 'description': 'Создать статью'},
                    {'method': 'GET', 'path': '/api/posts/:id', 'description': 'Одна статья'},
                    {'method': 'POST', 'path': '/api/comments', 'description': 'Добавить комментарий'},
                    {'method': 'GET', 'path': '/api/comments', 'description': 'Комментарии к статье'}
                ],
                'auth_type': 'none',
                'functions': ['api-posts', 'api-comments']
            },
            'database': {
                'tables': [
                    {'name': 'posts', 'columns': [
                        {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                        {'name': 'title', 'type': 'VARCHAR(255) NOT NULL'},
                        {'name': 'content', 'type': 'TEXT NOT NULL'},
                        {'name': 'author', 'type': 'VARCHAR(100)'},
                        {'name': 'tags', 'type': 'JSONB DEFAULT \'[]\'::jsonb'},
                        {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                    ]},
                    {'name': 'comments', 'columns': [
                        {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                        {'name': 'post_id', 'type': 'INTEGER REFERENCES posts(id)'},
                        {'name': 'author', 'type': 'VARCHAR(100)'},
                        {'name': 'content', 'type': 'TEXT NOT NULL'},
                        {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                    ]}
                ],
                'indexes': ['CREATE INDEX idx_comments_post_id ON comments(post_id)']
            },
            'features': ['blog_posts', 'comments', 'tags', 'search', 'responsive']
        },
        'estimated_time': 50,
        'estimated_cost': 0.30
    }


def fallback_crm(q):
    return {
        'spec': {
            'app_name': 'admin-dashboard',
            'description': q,
            'frontend': {
                'pages': [
                    {'path': '/', 'name': 'Dashboard', 'components': ['StatsCards', 'RecentActivity', 'QuickActions']},
                    {'path': '/clients', 'name': 'Clients', 'components': ['ClientTable', 'AddClientForm', 'ClientSearch']},
                    {'path': '/deals', 'name': 'Deals', 'components': ['DealsPipeline', 'DealForm']}
                ],
                'components': [
                    {'name': 'StatsCards', 'description': 'Карточки статистики'},
                    {'name': 'RecentActivity', 'description': 'Последние действия'},
                    {'name': 'QuickActions', 'description': 'Быстрые действия'},
                    {'name': 'ClientTable', 'description': 'Таблица клиентов'},
                    {'name': 'AddClientForm', 'description': 'Форма добавления клиента'},
                    {'name': 'ClientSearch', 'description': 'Поиск клиентов'},
                    {'name': 'DealsPipeline', 'description': 'Воронка сделок'},
                    {'name': 'DealForm', 'description': 'Форма сделки'}
                ],
                'styling': 'Tailwind CSS + shadcn/ui'
            },
            'backend': {
                'endpoints': [
                    {'method': 'GET', 'path': '/api/clients', 'description': 'Список клиентов'},
                    {'method': 'POST', 'path': '/api/clients', 'description': 'Добавить клиента'},
                    {'method': 'GET', 'path': '/api/deals', 'description': 'Список сделок'},
                    {'method': 'POST', 'path': '/api/deals', 'description': 'Создать сделку'},
                    {'method': 'GET', 'path': '/api/stats', 'description': 'Статистика'}
                ],
                'auth_type': 'none',
                'functions': ['api-clients', 'api-deals', 'api-stats']
            },
            'database': {
                'tables': [
                    {'name': 'clients', 'columns': [
                        {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                        {'name': 'name', 'type': 'VARCHAR(255) NOT NULL'},
                        {'name': 'email', 'type': 'VARCHAR(255)'},
                        {'name': 'phone', 'type': 'VARCHAR(50)'},
                        {'name': 'company', 'type': 'VARCHAR(255)'},
                        {'name': 'status', 'type': 'VARCHAR(50) DEFAULT \'active\''},
                        {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                    ]},
                    {'name': 'deals', 'columns': [
                        {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                        {'name': 'client_id', 'type': 'INTEGER REFERENCES clients(id)'},
                        {'name': 'title', 'type': 'VARCHAR(255) NOT NULL'},
                        {'name': 'amount', 'type': 'NUMERIC(12,2)'},
                        {'name': 'stage', 'type': 'VARCHAR(50) DEFAULT \'new\''},
                        {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                    ]}
                ],
                'indexes': ['CREATE INDEX idx_deals_client_id ON deals(client_id)']
            },
            'features': ['clients_management', 'deals_pipeline', 'dashboard', 'statistics', 'responsive']
        },
        'estimated_time': 60,
        'estimated_cost': 0.35
    }


def fallback_generic(q):
    return {
        'spec': {
            'app_name': 'web-app',
            'description': q,
            'frontend': {
                'pages': [
                    {'path': '/', 'name': 'Home', 'components': ['Hero', 'FeatureCards', 'ContactForm']},
                    {'path': '/about', 'name': 'About', 'components': ['AboutContent', 'TeamSection']},
                    {'path': '/contact', 'name': 'Contact', 'components': ['ContactForm', 'MapSection']}
                ],
                'components': [
                    {'name': 'Hero', 'description': 'Главный баннер с заголовком и CTA'},
                    {'name': 'FeatureCards', 'description': 'Карточки возможностей'},
                    {'name': 'ContactForm', 'description': 'Форма обратной связи'},
                    {'name': 'AboutContent', 'description': 'Информация о проекте'},
                    {'name': 'TeamSection', 'description': 'Команда проекта'},
                    {'name': 'MapSection', 'description': 'Раздел с контактами'}
                ],
                'styling': 'Tailwind CSS + shadcn/ui'
            },
            'backend': {
                'endpoints': [
                    {'method': 'POST', 'path': '/api/contact', 'description': 'Отправить сообщение'},
                    {'method': 'GET', 'path': '/api/content', 'description': 'Получить контент страниц'}
                ],
                'auth_type': 'none',
                'functions': ['api-contact', 'api-content']
            },
            'database': {
                'tables': [
                    {'name': 'contacts', 'columns': [
                        {'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                        {'name': 'name', 'type': 'VARCHAR(255) NOT NULL'},
                        {'name': 'email', 'type': 'VARCHAR(255) NOT NULL'},
                        {'name': 'message', 'type': 'TEXT NOT NULL'},
                        {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                    ]}
                ],
                'indexes': []
            },
            'features': ['landing_page', 'contact_form', 'responsive', 'dark_theme']
        },
        'estimated_time': 30,
        'estimated_cost': 0.15
    }
