import os
import json
import asyncio
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ProjectSpec(BaseModel):
    frontend: Dict
    backend: Dict
    database: Dict
    infrastructure: Dict
    dependencies: List[str]

class InterpretRequest(BaseModel):
    user_query: str
    attachments: Optional[List[str]] = None
    project_id: Optional[str] = None

class GenerateRequest(BaseModel):
    spec: ProjectSpec
    project_id: str

def handler(event: dict, context) -> dict:
    """Ядро автономного ИИ-агента: интерпретация запросов и оркестрация генерации проектов"""
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Authorization'
            },
            'body': ''
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    body = json.loads(event.get('body', '{}'))
    action = body.get('action', 'interpret')
    
    if action == 'interpret':
        return interpret_request(body)
    elif action == 'generate':
        return generate_project(body)
    else:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid action. Use: interpret or generate'})
        }

def interpret_request(body: dict) -> dict:
    """Интерпретирует пользовательский запрос в техническую спецификацию"""
    try:
        request = InterpretRequest(**body)
        
        spec = {
            "frontend": {
                "framework": "React + TypeScript",
                "ui_library": "shadcn/ui + Tailwind CSS",
                "state_management": "Zustand",
                "routing": "React Router v6",
                "pages": extract_pages_from_query(request.user_query),
                "components": extract_components_from_query(request.user_query)
            },
            "backend": {
                "framework": "Python FastAPI",
                "endpoints": extract_endpoints_from_query(request.user_query),
                "auth": detect_auth_requirements(request.user_query),
                "integrations": detect_integrations(request.user_query)
            },
            "database": {
                "type": "PostgreSQL",
                "schema": generate_db_schema(request.user_query),
                "indexes": generate_indexes(request.user_query)
            },
            "infrastructure": {
                "frontend_host": "Vercel",
                "backend_host": "AWS Lambda",
                "database_host": "RDS PostgreSQL"
            },
            "dependencies": extract_dependencies(request.user_query)
        }
        
        conflicts = detect_conflicts(spec)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'spec': spec,
                'conflicts': conflicts,
                'estimated_time': estimate_generation_time(spec),
                'estimated_cost': estimate_monthly_cost(spec)
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def generate_project(body: dict) -> dict:
    """Генерирует полный проект на основе спецификации"""
    try:
        request = GenerateRequest(**body)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'status': 'queued',
                'project_id': request.project_id,
                'message': 'Project generation started. Check /api/projects/{id}/status for progress.'
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def extract_pages_from_query(query: str) -> List[Dict]:
    """Извлекает структуру страниц из запроса"""
    query_lower = query.lower()
    
    pages = []
    
    if any(word in query_lower for word in ['магазин', 'shop', 'store', 'товар', 'product']):
        pages.extend([
            {"route": "/", "component": "ProductList", "features": ["search", "filters", "pagination"]},
            {"route": "/product/:id", "component": "ProductDetail", "features": ["gallery", "add-to-cart"]},
        ])
    
    if any(word in query_lower for word in ['корзин', 'cart', 'basket']):
        pages.append({"route": "/cart", "component": "Cart", "features": ["quantity-edit", "remove-item"]})
    
    if any(word in query_lower for word in ['оплат', 'payment', 'checkout', 'купить']):
        pages.append({"route": "/checkout", "component": "Checkout", "features": ["payment-form", "shipping"]})
    
    if any(word in query_lower for word in ['админ', 'admin', 'управлен']):
        pages.append({"route": "/admin", "component": "AdminDashboard", "features": ["manage-products", "orders"]})
    
    if not pages:
        pages.append({"route": "/", "component": "HomePage", "features": ["hero", "features"]})
    
    return pages

def extract_endpoints_from_query(query: str) -> List[Dict]:
    """Генерирует необходимые API endpoints"""
    query_lower = query.lower()
    endpoints = []
    
    if any(word in query_lower for word in ['товар', 'product', 'магазин']):
        endpoints.extend([
            {"path": "/api/products", "method": "GET", "auth": False},
            {"path": "/api/products/:id", "method": "GET", "auth": False},
        ])
    
    if any(word in query_lower for word in ['корзин', 'cart']):
        endpoints.extend([
            {"path": "/api/cart", "method": "GET", "auth": True},
            {"path": "/api/cart", "method": "POST", "auth": True},
        ])
    
    if any(word in query_lower for word in ['оплат', 'payment', 'заказ', 'order']):
        endpoints.append({"path": "/api/orders", "method": "POST", "auth": True})
    
    return endpoints

def generate_db_schema(query: str) -> Dict:
    """Генерирует схему БД на основе запроса"""
    query_lower = query.lower()
    schema = {}
    
    schema['users'] = ['id SERIAL PRIMARY KEY', 'email VARCHAR(255) UNIQUE', 'password_hash VARCHAR(255)', 'created_at TIMESTAMP']
    
    if any(word in query_lower for word in ['товар', 'product', 'магазин']):
        schema['products'] = [
            'id SERIAL PRIMARY KEY',
            'name VARCHAR(255) NOT NULL',
            'description TEXT',
            'price DECIMAL(10,2) NOT NULL',
            'image_url VARCHAR(500)',
            'stock INTEGER DEFAULT 0',
            'created_at TIMESTAMP'
        ]
    
    if any(word in query_lower for word in ['заказ', 'order', 'оплат']):
        schema['orders'] = [
            'id SERIAL PRIMARY KEY',
            'user_id INTEGER REFERENCES users(id)',
            'total_amount DECIMAL(10,2) NOT NULL',
            'status VARCHAR(50) DEFAULT pending',
            'created_at TIMESTAMP'
        ]
        schema['order_items'] = [
            'id SERIAL PRIMARY KEY',
            'order_id INTEGER REFERENCES orders(id)',
            'product_id INTEGER REFERENCES products(id)',
            'quantity INTEGER NOT NULL',
            'price DECIMAL(10,2) NOT NULL'
        ]
    
    if any(word in query_lower for word in ['корзин', 'cart']):
        schema['cart_items'] = [
            'id SERIAL PRIMARY KEY',
            'user_id INTEGER REFERENCES users(id)',
            'product_id INTEGER REFERENCES products(id)',
            'quantity INTEGER NOT NULL'
        ]
    
    return schema

def generate_indexes(query: str) -> List[str]:
    """Генерирует необходимые индексы"""
    indexes = ['users(email)']
    
    query_lower = query.lower()
    
    if 'продукт' in query_lower or 'товар' in query_lower:
        indexes.extend(['products(name)', 'products(price)'])
    
    if 'заказ' in query_lower or 'order' in query_lower:
        indexes.append('orders(user_id, created_at)')
    
    return indexes

def detect_auth_requirements(query: str) -> str:
    """Определяет требования к авторизации"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['админ', 'admin', 'управлен']):
        return 'JWT + Role-Based Access Control'
    elif any(word in query_lower for word in ['личный кабинет', 'профиль', 'account']):
        return 'JWT + httpOnly cookies'
    elif any(word in query_lower for word in ['вход', 'регистр', 'login', 'signup']):
        return 'JWT'
    
    return 'none'

def detect_integrations(query: str) -> List[str]:
    """Определяет необходимые интеграции"""
    query_lower = query.lower()
    integrations = []
    
    if any(word in query_lower for word in ['оплат', 'payment', 'stripe', 'купить']):
        integrations.append('Stripe API')
    
    if any(word in query_lower for word in ['email', 'почт', 'уведомлен', 'notification']):
        integrations.append('SendGrid')
    
    if any(word in query_lower for word in ['telegram', 'тг', 'бот']):
        integrations.append('Telegram Bot API')
    
    if any(word in query_lower for word in ['s3', 'файл', 'загрузка', 'upload']):
        integrations.append('AWS S3')
    
    return integrations

def extract_dependencies(query: str) -> List[str]:
    """Извлекает зависимости на основе требований"""
    deps = ['react', 'typescript', 'vite', 'tailwindcss']
    query_lower = query.lower()
    
    if 'stripe' in query_lower or 'оплат' in query_lower:
        deps.append('@stripe/stripe-js')
    
    if 'chart' in query_lower or 'график' in query_lower:
        deps.append('recharts')
    
    if 'таблиц' in query_lower or 'table' in query_lower:
        deps.append('@tanstack/react-table')
    
    if 'форм' in query_lower or 'form' in query_lower:
        deps.append('react-hook-form')
    
    return deps

def detect_conflicts(spec: Dict) -> List[str]:
    """Выявляет конфликты в спецификации"""
    conflicts = []
    
    if spec['frontend']['state_management'] == 'Redux' and 'small' in str(spec):
        conflicts.append('Redux избыточен для маленького проекта, рекомендуется Zustand')
    
    if spec['database']['type'] == 'MongoDB' and 'transactions' in str(spec):
        conflicts.append('MongoDB не оптимален для транзакций, рекомендуется PostgreSQL')
    
    return conflicts

def estimate_generation_time(spec: Dict) -> int:
    """Оценивает время генерации в секундах"""
    base_time = 120
    
    pages_count = len(spec['frontend'].get('pages', []))
    endpoints_count = len(spec['backend'].get('endpoints', []))
    tables_count = len(spec['database'].get('schema', {}))
    
    return base_time + (pages_count * 30) + (endpoints_count * 20) + (tables_count * 15)

def estimate_monthly_cost(spec: Dict) -> float:
    """Оценивает ежемесячную стоимость инфраструктуры в USD"""
    cost = 0.0
    
    if spec['infrastructure']['frontend_host'] == 'Vercel':
        cost += 0
    elif spec['infrastructure']['frontend_host'] == 'AWS CloudFront':
        cost += 5
    
    endpoints_count = len(spec['backend'].get('endpoints', []))
    cost += endpoints_count * 2
    
    if spec['database']['type'] == 'PostgreSQL':
        cost += 15
    
    integrations = spec['backend'].get('integrations', [])
    if 'Stripe API' in integrations:
        cost += 0
    if 'SendGrid' in integrations:
        cost += 15
    
    return round(cost, 2)

def extract_components_from_query(query: str) -> List[str]:
    """Извлекает UI компоненты из запроса"""
    components = []
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['форм', 'form', 'ввод']):
        components.append('Form')
    
    if any(word in query_lower for word in ['таблиц', 'table', 'список']):
        components.append('DataTable')
    
    if any(word in query_lower for word in ['карточк', 'card']):
        components.append('ProductCard')
    
    if any(word in query_lower for word in ['модальн', 'modal', 'dialog']):
        components.append('Dialog')
    
    if any(word in query_lower for word in ['навигац', 'menu', 'header']):
        components.append('Navigation')
    
    return components