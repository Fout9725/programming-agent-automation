# АВТОНОМНЫЙ AI-АГЕНТ ПО ПРОГРАММИРОВАНИЮ v2.0
## Технический документ архитектуры мультиагентной системы

**Версия:** 2.0  
**Дата:** 15.04.2026  
**Статус:** Утвержден к реализации  
**Платформа:** poehali.dev (React + Python Cloud Functions + PostgreSQL)

---

## 1. РЕЗЮМЕ

Система представляет собой полностью автономную мультиагентную платформу, которая принимает запрос пользователя на естественном языке (русском/английском), самостоятельно проектирует, разрабатывает, тестирует и разворачивает готовое веб-приложение. Пользователь получает ссылку на работающий проект и GitHub-репозиторий с исходным кодом.

**Ключевое отличие от v1.0:** текущая версия лишь генерирует код через OpenRouter и показывает его в интерфейсе. Новая версия v2.0 полностью автономно собирает, валидирует и деплоит приложение через координацию специализированных AI-агентов.

**Что будет реализовано:**
- Мультиагентный оркестратор с 6 специализированными ролями
- Параллельная генерация frontend/backend/БД через единую спецификацию
- Автоматическое тестирование и self-healing (самоисправление ошибок)
- Деплой на poehali.dev с генерацией публичной ссылки
- Real-time отображение прогресса разработки в UI
- Интеграция с GitHub для автоматического коммита кода

---

## 2. АРХИТЕКТУРА СИСТЕМЫ

### 2.1 Общая схема

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ПОЛЬЗОВАТЕЛЬ                                │
│  "Создай Todo-приложение с авторизацией и тёмной темой"             │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP POST
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React SPA)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │ ProjectForm  │  │ AgentConsole │  │ DeploymentStatus          │  │
│  │ (ввод запроса│  │ (real-time   │  │ (ссылка на результат)     │  │
│  │  + параметры)│  │  логи агентов│  │                           │  │
│  └──────┬───────┘  └──────▲───────┘  └───────────▲───────────────┘  │
│         │                 │ SSE/polling           │                  │
└─────────┼─────────────────┼──────────────────────┼──────────────────┘
          │                 │                      │
          ▼                 │                      │
┌─────────────────────────────────────────────────────────────────────┐
│              BACKEND CLOUD FUNCTIONS (Python 3.11)                   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                 agent-orchestrator                           │    │
│  │              (TEAM LEAD — координатор)                       │    │
│  │                                                             │    │
│  │  1. Принимает запрос                                        │    │
│  │  2. Вызывает agent-core (Архитектор) → spec                 │    │
│  │  3. Создает pipeline задач                                  │    │
│  │  4. Последовательно вызывает агентов                        │    │
│  │  5. Собирает результат                                      │    │
│  └───┬─────────┬──────────┬──────────┬──────────┬──────────┬───┘    │
│      │         │          │          │          │          │         │
│      ▼         ▼          ▼          ▼          ▼          ▼         │
│  ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌──────────┐    │
│  │agent-  ││agent-  ││agent-  ││agent-  ││code-   ││agent-    │    │
│  │core    ││frontend││backend ││db      ││validat.││deployer  │    │
│  │        ││        ││        ││        ││        ││          │    │
│  │Архи-   ││React   ││Python  ││SQL     ││Линтер  ││GitHub    │    │
│  │тектор  ││код     ││API     ││схемы   ││+тесты  ││+деплой   │    │
│  └────┬───┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘└────┬─────┘    │
│       │        │         │         │         │          │           │
│       ▼        ▼         ▼         ▼         ▼          ▼           │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              PostgreSQL (sessions, files, logs)              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              S3 Storage (сгенерированные файлы)              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              OpenRouter API (AI модели)                      │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Поток данных

```
ЗАПРОС → agent-orchestrator
         ├─ Шаг 1: agent-core (interpret) → spec.json
         ├─ Шаг 2: agent-db (generate schema) → migrations.sql
         ├─ Шаг 3: agent-backend (generate API) → backend files
         ├─ Шаг 4: agent-frontend (generate UI) → frontend files
         ├─ Шаг 5: code-validator (lint + test) → issues[]
         │         └─ если issues → возврат к Шагу 3/4 (self-healing)
         ├─ Шаг 6: agent-deployer (commit + deploy) → public URL
         └─ РЕЗУЛЬТАТ → { url, repo_url, spec, files }
```

---

## 3. СПЕЦИФИКАЦИЯ АГЕНТНОЙ КОМАНДЫ

### 3.1 Таблица ролей

| # | Роль | Функция (Cloud Function) | AI Модель | Обоснование модели | Обязанности |
|---|------|-------------------------|-----------|-------------------|-------------|
| 1 | **Team Lead** (Оркестратор) | `agent-orchestrator` | Не использует AI напрямую | Чистая логика координации | Принимает запрос, создает pipeline, вызывает агентов последовательно, собирает результат, управляет self-healing циклами |
| 2 | **Архитектор** | `agent-core` | Claude Opus 4 / GPT-5.2 | Глубокое планирование, декомпозиция | Анализ запроса → техническая спецификация (pages, API, DB schema, dependencies) |
| 3 | **Frontend-разработчик** | `agent-frontend` | Claude Sonnet 4 / GPT-5.1 | Исполнительская задача, оптимизация стоимости | Генерация React компонентов, страниц, стилей по спецификации |
| 4 | **Backend-разработчик** | `agent-backend` | Claude Sonnet 4 / GPT-5.1 | Исполнительская задача | Генерация Python Cloud Functions, API endpoints, бизнес-логики |
| 5 | **Специалист по БД** | `agent-db` | Claude Sonnet 4 / GPT-5.1 | Структурированные задачи | Генерация SQL миграций, схем, индексов, seed data |
| 6 | **Тестировщик + Валидатор** | `code-validator` (существует) | Claude Sonnet 4 | Анализ кода | Статический анализ, проверка паттернов, генерация тестов, обнаружение уязвимостей |
| 7 | **DevOps / Деплойер** | `agent-deployer` | Не использует AI | Чистая логика деплоя | Коммит в GitHub, создание PR, деплой на poehali.dev, генерация URL |

### 3.2 Принцип выбора модели

- **Opus (дорогая, мощная)** — только для задач, требующих глубокого анализа и планирования: архитектура, декомпозиция, разрешение конфликтов. Используется 1 раз за сессию (Архитектор).
- **Sonnet (дешевая, быстрая)** — для исполнительских задач с чёткими инструкциями: генерация кода по спецификации, написание тестов. Используется 3-4 раза за сессию.
- **Без AI** — оркестратор и деплойер работают на чистой логике Python без вызовов AI моделей.

### 3.3 Стоимость одной сессии (оценка)

| Агент | Токены (вход/выход) | Стоимость |
|-------|-------------------|-----------|
| Архитектор (Opus) | ~8K/4K | ~$0.18 |
| Frontend (Sonnet) | ~6K/8K | ~$0.06 |
| Backend (Sonnet) | ~6K/6K | ~$0.05 |
| DB (Sonnet) | ~3K/2K | ~$0.02 |
| Валидатор (Sonnet) | ~4K/2K | ~$0.02 |
| **ИТОГО** | | **~$0.33/проект** |

---

## 4. ДЕТАЛЬНОЕ ОПИСАНИЕ ЖИЗНЕННОГО ЦИКЛА

### 4.1 Этап 1: Приём запроса (agent-orchestrator)

**Вход:** POST запрос от frontend
```json
{
  "action": "create_project",
  "user_query": "Создай Todo-приложение с авторизацией и тёмной темой",
  "project_name": "my-todo-app",
  "ai_model_preference": "auto",
  "language": "ru"
}
```

**Логика оркестратора:**
1. Создает запись в таблице `build_sessions` со статусом `started`
2. Возвращает `session_id` клиенту для polling прогресса
3. Запускает pipeline обработки

### 4.2 Этап 2: Архитектурный анализ (agent-core)

**Промпт для Архитектора (Opus):**
```
Ты — ведущий архитектор веб-приложений. Проанализируй запрос пользователя 
и создай детальную техническую спецификацию.

ЗАПРОС: "{user_query}"

Верни JSON со следующей структурой:
{
  "app_name": "название приложения",
  "description": "краткое описание",
  "frontend": {
    "pages": [{"path": "/", "name": "Home", "components": ["TodoList", "AddTodo"]}],
    "components": [{"name": "TodoList", "props": {...}, "description": "..."}],
    "state_management": "useState + useReducer",
    "styling": "Tailwind CSS + shadcn/ui"
  },
  "backend": {
    "endpoints": [{"method": "GET", "path": "/api/todos", "description": "..."}],
    "auth_type": "JWT",
    "middleware": ["cors", "auth"]
  },
  "database": {
    "tables": [{"name": "users", "columns": [...]}],
    "indexes": [...],
    "seed_data": true
  },
  "features": ["dark_theme", "auth", "crud"],
  "estimated_files_count": 15
}
```

**Выход:** `spec.json` сохраняется в `build_sessions.spec`

### 4.3 Этап 3: Генерация базы данных (agent-db)

**Промпт для DB-агента (Sonnet):**
```
На основе спецификации сгенерируй SQL-миграцию для PostgreSQL.

СПЕЦИФИКАЦИЯ БД:
{spec.database}

ТРЕБОВАНИЯ:
- Используй SERIAL для PK
- Добавь created_at/updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- Создай все необходимые индексы
- Добавь FOREIGN KEY с ON DELETE CASCADE
- Если auth_type == "JWT", создай таблицу users с email, password_hash

Верни JSON:
{
  "migration_sql": "CREATE TABLE...",
  "seed_sql": "INSERT INTO...",
  "tables_created": ["users", "todos"]
}
```

### 4.4 Этап 4: Генерация backend (agent-backend)

**Промпт для Backend-агента (Sonnet):**
```
Сгенерируй Python Cloud Function для poehali.dev.

СПЕЦИФИКАЦИЯ API:
{spec.backend}

ФОРМАТ CLOUD FUNCTION:
- Entry point: def handler(event: dict, context) -> dict
- CORS: обязательно обрабатывай OPTIONS
- Парсинг body: json.loads(event.get('body', '{}'))
- Headers: event.get('headers', {})
- БД: psycopg2 + os.environ['DATABASE_URL'] (Simple Query Protocol)
- Auth header: читай X-Authorization (НЕ Authorization)

Для КАЖДОГО endpoint сгенерируй:
1. index.py с handler
2. requirements.txt
3. tests.json

Верни JSON:
{
  "functions": {
    "api-todos": {
      "index.py": "...",
      "requirements.txt": "...",
      "tests.json": "..."
    },
    "api-auth": {
      "index.py": "...",
      ...
    }
  }
}
```

### 4.5 Этап 5: Генерация frontend (agent-frontend)

**Промпт для Frontend-агента (Sonnet):**
```
Сгенерируй React + TypeScript приложение для poehali.dev.

СПЕЦИФИКАЦИЯ UI:
{spec.frontend}

СТЕК:
- React 18 + TypeScript
- Tailwind CSS + shadcn/ui компоненты (они уже установлены)
- React Router DOM v6
- Импорт алиас: @/ → src/
- Иконки: используй <Icon name="IconName" /> из @/components/ui/icon
- API вызовы: fetch() к URL из func2url.json

BACKEND API ENDPOINTS:
{spec.backend.endpoints}

FEATURES:
{spec.features}

Для КАЖДОГО файла верни:
{
  "files": {
    "src/pages/Home.tsx": "...",
    "src/components/TodoList.tsx": "...",
    "src/components/AddTodo.tsx": "...",
    "src/hooks/useTodos.ts": "...",
    "src/lib/api.ts": "..."
  },
  "app_tsx_routes": [
    {"path": "/", "component": "Home", "import": "./pages/Home"}
  ]
}
```

### 4.6 Этап 6: Валидация и Self-Healing (code-validator)

**Процесс:**
1. Валидатор получает ВСЕ сгенерированные файлы
2. Проверяет:
   - TypeScript: синтаксис, типы, отсутствие `any`, React паттерны
   - Python: безопасность (no eval/exec), структура handler
   - SQL: инъекции, best practices
   - Совместимость: API контракт frontend ↔ backend
3. Если найдены ошибки → возвращает список issues
4. Оркестратор отправляет issues обратно соответствующему агенту с промптом:

```
В сгенерированном коде найдены ошибки. Исправь их.

ФАЙЛ: {file_path}
ОШИБКИ:
{issues}

ТЕКУЩИЙ КОД:
{current_code}

Верни ПОЛНЫЙ исправленный файл.
```

5. Цикл повторяется максимум 3 раза. Если после 3 итераций ошибки остаются — помечает их как warnings и продолжает.

### 4.7 Этап 7: Деплой (agent-deployer)

**Процесс:**
1. Сохраняет все файлы в `project_files` в PostgreSQL
2. Коммитит в GitHub репозиторий через GitHub API:
   - Создает/обновляет репозиторий
   - Создает tree из всех файлов
   - Делает commit + push
3. Записывает URL функций в `func2url.json`
4. Формирует публичную ссылку на приложение
5. Обновляет `build_sessions` → статус `completed`

**Результат:**
```json
{
  "status": "completed",
  "app_url": "https://preview--my-todo-app.poehali.dev",
  "github_url": "https://github.com/user/my-todo-app",
  "files_count": 15,
  "build_time_seconds": 45,
  "spec": {...}
}
```

---

## 5. СХЕМА БАЗЫ ДАННЫХ (новые таблицы)

### 5.1 build_sessions — сессии сборки

```sql
CREATE TABLE build_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    user_query TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'started',
    -- started → analyzing → generating_db → generating_backend 
    -- → generating_frontend → validating → fixing → deploying → completed → failed
    current_step VARCHAR(100),
    spec JSONB,
    generated_files JSONB DEFAULT '{}'::jsonb,
    agent_logs JSONB DEFAULT '[]'::jsonb,
    validation_issues JSONB DEFAULT '[]'::jsonb,
    fix_iterations INTEGER DEFAULT 0,
    error_message TEXT,
    app_url VARCHAR(500),
    github_url VARCHAR(500),
    ai_model_used VARCHAR(100),
    tokens_used INTEGER DEFAULT 0,
    cost_usd NUMERIC(10,4) DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_build_sessions_project_id ON build_sessions(project_id);
CREATE INDEX idx_build_sessions_status ON build_sessions(status);
```

### 5.2 agent_logs — логи агентов

```sql
CREATE TABLE agent_logs (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES build_sessions(id) ON DELETE CASCADE,
    agent_role VARCHAR(50) NOT NULL,
    -- architect, frontend, backend, db, validator, deployer
    action VARCHAR(100) NOT NULL,
    input_summary TEXT,
    output_summary TEXT,
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_logs_session_id ON agent_logs(session_id);
```

---

## 6. ОБРАБОТКА ОШИБОК И SELF-HEALING

### 6.1 Уровни ошибок

| Уровень | Пример | Действие |
|---------|--------|----------|
| **error** (критическая) | Синтаксическая ошибка, отсутствует import | Обязательное исправление, до 3 итераций |
| **warning** (предупреждение) | console.log в production, SELECT * | Попытка исправления 1 раз, затем пропуск |
| **info** (рекомендация) | Можно оптимизировать | Игнорируется, логируется |

### 6.2 Алгоритм Self-Healing

```
1. Валидатор находит ошибки
2. Группирует по файлам и агентам:
   - .tsx/.ts ошибки → agent-frontend
   - .py ошибки → agent-backend
   - .sql ошибки → agent-db
3. Для каждой группы вызывает агента с промптом исправления
4. Получает исправленные файлы
5. Повторно валидирует ТОЛЬКО исправленные файлы
6. Если ошибки остались И iterations < 3 → goto 3
7. Если iterations >= 3 → логирует неисправленные ошибки, продолжает деплой
```

### 6.3 Cross-Validation (перекрёстная проверка)

Валидатор дополнительно проверяет **совместимость** между агентами:

```
1. Извлекает API контракт из backend файлов (endpoints, типы)
2. Извлекает API вызовы из frontend файлов (fetch URLs, типы)
3. Сравнивает:
   - Все ли frontend вызовы имеют соответствующий backend endpoint?
   - Совпадают ли HTTP методы?
   - Совпадают ли структуры request/response?
4. При несовпадении → исправляет frontend (он адаптивнее)
```

---

## 7. FRONTEND — ОБНОВЛЁННЫЙ ИНТЕРФЕЙС

### 7.1 Новые компоненты

```
src/
├── components/
│   ├── AgentConsole.tsx        # Real-time логи агентов
│   ├── BuildProgress.tsx       # Прогресс-бар этапов сборки
│   ├── ProjectResult.tsx       # Результат: ссылки, файлы, статистика
│   ├── SpecPreview.tsx         # Предпросмотр спецификации
│   └── AgentMessage.tsx        # Отдельное сообщение агента в логах
```

### 7.2 AgentConsole — консоль агентов

Отображает в реальном времени (polling каждые 2 секунды):

```
┌─────────────────────────────────────────────────────────────┐
│ 🏗 Сборка проекта "my-todo-app"                            │
│                                                             │
│ ████████████████░░░░░░░░░░░░░░  45%  Генерация frontend    │
│                                                             │
│ ✅ Архитектор: Спецификация готова (8 страниц, 12 API)     │
│ ✅ БД-специалист: Миграция создана (3 таблицы)              │
│ ✅ Backend: 4 Cloud Functions сгенерированы                 │
│ ⏳ Frontend: Генерация компонентов... (7/12)               │
│ ⏳ Тестировщик: Ожидание                                    │
│ ⏳ DevOps: Ожидание                                         │
│                                                             │
│ [Последнее сообщение]                                       │
│ Frontend-агент: Создаю компонент TodoList с поддержкой      │
│ drag-and-drop и фильтрацией по статусу...                   │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 BuildProgress — этапы сборки

```typescript
const BUILD_STEPS = [
  { key: 'analyzing',           label: 'Анализ запроса',        icon: 'Brain' },
  { key: 'generating_db',       label: 'База данных',           icon: 'Database' },
  { key: 'generating_backend',  label: 'Backend API',           icon: 'Server' },
  { key: 'generating_frontend', label: 'Интерфейс',            icon: 'Layout' },
  { key: 'validating',          label: 'Проверка кода',         icon: 'ShieldCheck' },
  { key: 'deploying',           label: 'Развёртывание',         icon: 'Rocket' },
  { key: 'completed',           label: 'Готово!',               icon: 'CheckCircle2' },
];
```

### 7.4 Обновлённая вкладка "Создание"

Вместо текущей формы с генерацией кода в textarea — полноценный wizard:

1. **Шаг 1: Описание** — textarea с запросом + выбор модели
2. **Шаг 2: Спецификация** — предпросмотр spec от Архитектора, возможность подправить
3. **Шаг 3: Сборка** — AgentConsole + BuildProgress в реальном времени
4. **Шаг 4: Результат** — ссылки на приложение и GitHub + статистика

---

## 8. ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ

### 8.1 Секреты (Environment Variables)

| Секрет | Назначение | Статус |
|--------|-----------|--------|
| `DATABASE_URL` | Подключение к PostgreSQL | ✅ Существует |
| `OPENROUTER_API_KEY` | Доступ к AI моделям | ✅ Существует |
| `GITHUB_TOKEN` | Автономная работа с GitHub | ✅ Существует |
| `GITHUB_CLIENT_SECRET` | OAuth для пользователей | ✅ Существует |
| `AWS_ACCESS_KEY_ID` | S3 хранилище | ✅ Существует |
| `AWS_SECRET_ACCESS_KEY` | S3 хранилище | ✅ Существует |

### 8.2 Зависимости Backend

```
pydantic>=2.5.0          # Валидация данных
psycopg2                 # PostgreSQL
requests>=2.31.0         # HTTP запросы к OpenRouter
```

### 8.3 Новые Cloud Functions

| Функция | Метод | Описание |
|---------|-------|----------|
| `agent-orchestrator` | POST | Главный координатор pipeline |
| `agent-frontend` | POST | Генерация React кода |
| `agent-backend` | POST | Генерация Python API |
| `agent-db` | POST | Генерация SQL миграций |
| `agent-deployer` | POST | Коммит в GitHub + деплой |
| `build-status` | GET | Polling статуса сборки |

### 8.4 API контракты

#### POST /agent-orchestrator
```json
// Request
{
  "action": "create_project",
  "user_query": "Создай Todo-приложение",
  "project_name": "my-todo-app",
  "ai_model": "auto",
  "language": "ru"
}

// Response (immediate)
{
  "session_id": "uuid",
  "status": "started",
  "message": "Проект принят в обработку"
}
```

#### GET /build-status?session_id=uuid
```json
// Response
{
  "session_id": "uuid",
  "status": "generating_frontend",
  "progress": 0.45,
  "current_step": "Генерация компонентов",
  "steps": [
    {"key": "analyzing", "status": "completed", "duration_ms": 3200},
    {"key": "generating_db", "status": "completed", "duration_ms": 2100},
    {"key": "generating_backend", "status": "completed", "duration_ms": 8400},
    {"key": "generating_frontend", "status": "in_progress", "progress": 0.6},
    {"key": "validating", "status": "pending"},
    {"key": "deploying", "status": "pending"}
  ],
  "agent_logs": [
    {"agent": "architect", "message": "Спецификация готова: 4 страницы, 8 API", "timestamp": "..."},
    {"agent": "frontend", "message": "Создаю TodoList компонент...", "timestamp": "..."}
  ]
}
```

#### Результат (status = completed)
```json
{
  "session_id": "uuid",
  "status": "completed",
  "app_url": "https://preview--my-todo-app.poehali.dev",
  "github_url": "https://github.com/user/my-todo-app",
  "spec": {...},
  "files_count": 15,
  "build_time_seconds": 42,
  "cost_usd": 0.31,
  "validation_warnings": []
}
```

---

## 9. ПЛАН РЕАЛИЗАЦИИ (Roadmap)

### Фаза 1: Фундамент (этот этап)
1. ✅ Миграция БД: таблицы `build_sessions`, `agent_logs`
2. `agent-orchestrator` — координатор pipeline
3. `build-status` — polling статуса
4. Обновлённый agent-core с OpenRouter интеграцией

### Фаза 2: Агенты-генераторы
5. `agent-db` — генерация SQL
6. `agent-backend` — генерация Python Cloud Functions
7. `agent-frontend` — генерация React компонентов
8. Интеграция с code-validator (self-healing)

### Фаза 3: Деплой и UI
9. `agent-deployer` — GitHub коммит + деплой
10. Обновлённый frontend: AgentConsole, BuildProgress, ProjectResult
11. Полный end-to-end pipeline

### Фаза 4: Полировка
12. Оптимизация промптов для каждого агента
13. Кэширование шаблонных решений
14. Аналитика и метрики сессий

---

## 10. ПРИМЕР СЦЕНАРИЯ

### Пользователь: "Создай простой чат на WebSocket с комнатами"

**Шаг 1: Запрос → agent-orchestrator**
- Создает build_session, status=started
- Возвращает session_id

**Шаг 2: agent-core (Архитектор)**
- Spec: 3 страницы (Login, Rooms, Chat)
- 5 компонентов (RoomList, ChatRoom, MessageBubble, UserInput, OnlineUsers)
- 4 API endpoints (POST /auth, GET /rooms, POST /rooms, WebSocket /ws/chat)
- 3 таблицы (users, rooms, messages)
- Auth: JWT
- Features: real-time messaging, rooms, online indicators

**Шаг 3: agent-db**
```sql
CREATE TABLE users (id SERIAL PK, username VARCHAR(100), password_hash TEXT, ...);
CREATE TABLE rooms (id SERIAL PK, name VARCHAR(200), created_by INT FK, ...);
CREATE TABLE messages (id SERIAL PK, room_id INT FK, user_id INT FK, content TEXT, ...);
```

**Шаг 4: agent-backend**
- `api-auth/index.py` — регистрация/логин с JWT
- `api-rooms/index.py` — CRUD комнат
- `api-messages/index.py` — получение/отправка сообщений (polling, т.к. Cloud Functions не поддерживают WebSocket)

**Шаг 5: agent-frontend**
- `src/pages/Login.tsx` — форма входа
- `src/pages/Rooms.tsx` — список комнат
- `src/pages/Chat.tsx` — чат с polling каждые 2 сек
- `src/components/MessageBubble.tsx`, `UserInput.tsx`, etc.
- `src/hooks/useAuth.ts`, `useMessages.ts`

**Шаг 6: code-validator**
- Найдена ошибка: frontend вызывает POST /api/messages, backend ожидает body.content, frontend отправляет body.message
- Self-healing: исправляет frontend (body.message → body.content)
- Повторная валидация: ✅ OK

**Шаг 7: agent-deployer**
- Коммит в GitHub: 15 файлов
- Backend функции деплоятся через sync_backend
- Frontend собирается через poehali.dev

**Результат:**
```
✅ Приложение готово!
🔗 https://preview--my-chat-app.poehali.dev
📦 https://github.com/user/my-chat-app
⏱ Время сборки: 38 секунд
💰 Стоимость: $0.29
```

---

## 11. БЕЗОПАСНОСТЬ И ИЗОЛЯЦИЯ

### 11.1 Ограничения агентов
- Агенты НЕ имеют доступа к файловой системе сервера
- Каждый агент — отдельная Cloud Function с изолированным окружением
- Секреты передаются только через os.environ, никогда в коде
- Генерируемый код проходит валидацию на отсутствие: eval(), exec(), os.system(), __import__()

### 11.2 Rate Limiting
- Максимум 5 параллельных build_sessions на проект
- Максимум 3 итерации self-healing
- Timeout на каждого агента: 60 секунд
- Общий timeout на pipeline: 300 секунд (5 минут)

### 11.3 Логирование
- Все действия агентов записываются в `agent_logs`
- Каждый вызов OpenRouter фиксирует tokens_in/tokens_out
- Ошибки логируются с полным контекстом для debug

---

## 12. ЗАКЛЮЧЕНИЕ

### Потенциал масштабирования
- **Горизонтальное:** Cloud Functions масштабируются автоматически
- **Новые агенты:** Модульная архитектура позволяет добавить агента (например, agent-mobile для React Native) без изменения оркестратора
- **Кэширование:** Типовые спецификации (Todo, CRM, Landing) можно кэшировать для мгновенной генерации
- **Шаблоны:** Библиотека готовых решений ускоряет генерацию в 3-5x

### Ограничения
- Cloud Functions не поддерживают WebSocket — для real-time используется polling
- Timeout функций (30-60 сек) ограничивает размер генерируемого кода за один вызов
- OpenRouter API может быть недоступен — нужен fallback
- Сгенерированный код требует ручной проверки для production-критичных приложений

### Следующие шаги
- Расширение до мобильных приложений (React Native)
- Интеграция с Figma для генерации по макету
- A/B тестирование промптов для улучшения качества кода
- Marketplace шаблонов от сообщества
