import json
import os
import uuid
import time
import psycopg2
import requests

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Authorization',
    'Content-Type': 'application/json'
}

AGENT_URLS = {
    'agent-core': 'https://functions.poehali.dev/9f6aa0df-0354-413d-8000-718edd1fd190',
    'agent-db': 'https://functions.poehali.dev/b5b1fae1-7449-4e58-a46a-d805f0a55fa6',
    'agent-backend': 'https://functions.poehali.dev/0c9ae86e-dc57-4359-bc02-6e42b56da19f',
    'agent-frontend': 'https://functions.poehali.dev/e4a9e5af-e475-41a6-a5cc-6cea1a5b0fca',
    'code-validator': '',
    'agent-deployer': 'https://functions.poehali.dev/16c1448a-d3e7-4d8d-b731-62233340ad12',
}

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': '', 'isBase64Encoded': False}
    
    method = event.get('httpMethod', 'GET')
    params = event.get('queryStringParameters', {}) or {}
    
    if method == 'GET':
        action = params.get('action', '')
        if action == 'status':
            return get_build_status(params.get('session_id'))
        return {'statusCode': 400, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Unknown action'}), 'isBase64Encoded': False}
    
    if method == 'POST':
        body = json.loads(event.get('body', '{}'))
        action = body.get('action', '')
        
        if action == 'create_project':
            return start_build_pipeline(body)
        
        return {'statusCode': 400, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Unknown action'}), 'isBase64Encoded': False}
    
    return {'statusCode': 405, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Method not allowed'}), 'isBase64Encoded': False}


def start_build_pipeline(body):
    user_query = body.get('user_query', '')
    project_name = body.get('project_name', 'new-project')
    ai_model = body.get('ai_model', 'anthropic/claude-sonnet-4')
    language = body.get('language', 'ru')
    
    if not user_query:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'user_query обязателен'}),
            'isBase64Encoded': False
        }
    
    session_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO projects (name, description, project_type, status) VALUES (%s, %s, %s, %s) RETURNING id",
            (project_name, user_query, 'ai-webapp', 'building')
        )
        project_id = cur.fetchone()[0]
        
        cur.execute(
            """INSERT INTO build_sessions 
            (id, project_id, user_query, project_name, status, current_step, ai_model_used) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (session_id, project_id, user_query, project_name, 'started', 'analyzing', ai_model)
        )
        conn.commit()
        
        pipeline_result = run_pipeline(session_id, project_id, user_query, project_name, ai_model, language, conn)
        
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(pipeline_result),
            'isBase64Encoded': False
        }
        
    except Exception as e:
        conn.rollback()
        update_session_error(conn, session_id, str(e))
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e), 'session_id': session_id}),
            'isBase64Encoded': False
        }
    finally:
        conn.close()


def run_pipeline(session_id, project_id, user_query, project_name, ai_model, language, conn):
    total_tokens = 0
    total_cost = 0.0
    generated_files = {}
    start_time = time.time()
    
    update_session_status(conn, session_id, 'analyzing', 'Анализ требований и создание спецификации')
    log_agent(conn, session_id, 'architect', 'interpret', f'Анализ запроса: {user_query[:100]}')
    
    spec = call_agent('agent-core', {
        'action': 'interpret',
        'user_query': user_query,
        'ai_model': ai_model,
        'language': language
    })
    
    if not spec or 'error' in spec:
        error_msg = spec.get('error', 'Архитектор не смог создать спецификацию') if spec else 'agent-core недоступен'
        update_session_error(conn, session_id, error_msg)
        log_agent(conn, session_id, 'architect', 'interpret', error_msg, status='error')
        return {'session_id': session_id, 'status': 'failed', 'error': error_msg}
    
    save_spec(conn, session_id, spec)
    log_agent(conn, session_id, 'architect', 'interpret', 
              f'Спецификация готова: {len(spec.get("spec", {}).get("frontend", {}).get("pages", []))} страниц', 
              status='success')
    
    update_session_status(conn, session_id, 'generating_db', 'Создание схемы базы данных')
    log_agent(conn, session_id, 'db', 'generate_schema', 'Генерация SQL миграций')
    
    db_result = call_agent('agent-db', {
        'action': 'generate',
        'spec': spec.get('spec', {}),
        'ai_model': ai_model
    })
    
    if db_result and 'files' in db_result:
        generated_files.update(db_result['files'])
        log_agent(conn, session_id, 'db', 'generate_schema', 
                  f'Создано {len(db_result.get("tables_created", []))} таблиц', status='success')
    else:
        log_agent(conn, session_id, 'db', 'generate_schema', 'Пропущено (нет требований к БД)', status='skipped')
    
    update_session_status(conn, session_id, 'generating_backend', 'Создание серверной логики')
    log_agent(conn, session_id, 'backend', 'generate_api', 'Генерация Cloud Functions')
    
    backend_result = call_agent('agent-backend', {
        'action': 'generate',
        'spec': spec.get('spec', {}),
        'ai_model': ai_model,
        'language': language
    })
    
    if backend_result and 'files' in backend_result:
        generated_files.update(backend_result['files'])
        functions_count = len(backend_result.get('functions', []))
        log_agent(conn, session_id, 'backend', 'generate_api', 
                  f'Создано {functions_count} Cloud Functions', status='success')
    else:
        log_agent(conn, session_id, 'backend', 'generate_api', 'Ошибка генерации backend', status='error')
    
    update_session_status(conn, session_id, 'generating_frontend', 'Создание интерфейса')
    log_agent(conn, session_id, 'frontend', 'generate_ui', 'Генерация React компонентов')
    
    frontend_result = call_agent('agent-frontend', {
        'action': 'generate',
        'spec': spec.get('spec', {}),
        'ai_model': ai_model,
        'language': language,
        'backend_endpoints': spec.get('spec', {}).get('backend', {}).get('endpoints', [])
    })
    
    if frontend_result and 'files' in frontend_result:
        generated_files.update(frontend_result['files'])
        components_count = len(frontend_result.get('components', []))
        log_agent(conn, session_id, 'frontend', 'generate_ui', 
                  f'Создано {components_count} компонентов', status='success')
    else:
        log_agent(conn, session_id, 'frontend', 'generate_ui', 'Ошибка генерации frontend', status='error')
    
    update_session_status(conn, session_id, 'validating', 'Проверка качества кода')
    log_agent(conn, session_id, 'validator', 'validate', 'Запуск проверки кода')
    
    validation_result = call_agent('code-validator', {
        'action': 'validate',
        'files': generated_files
    })
    
    issues = []
    if validation_result and 'issues' in validation_result:
        issues = [i for i in validation_result['issues'] if i.get('severity') == 'error']
    
    fix_iteration = 0
    while issues and fix_iteration < 3:
        fix_iteration += 1
        update_session_status(conn, session_id, 'fixing', f'Исправление ошибок (итерация {fix_iteration})')
        log_agent(conn, session_id, 'validator', 'fix', f'Найдено {len(issues)} ошибок, исправление...')
        
        frontend_issues = [i for i in issues if i.get('file', '').endswith(('.tsx', '.ts'))]
        backend_issues = [i for i in issues if i.get('file', '').endswith('.py')]
        
        if frontend_issues:
            fix_result = call_agent('agent-frontend', {
                'action': 'fix',
                'files': {i['file']: generated_files.get(i['file'], '') for i in frontend_issues},
                'issues': frontend_issues,
                'ai_model': ai_model
            })
            if fix_result and 'files' in fix_result:
                generated_files.update(fix_result['files'])
        
        if backend_issues:
            fix_result = call_agent('agent-backend', {
                'action': 'fix',
                'files': {i['file']: generated_files.get(i['file'], '') for i in backend_issues},
                'issues': backend_issues,
                'ai_model': ai_model
            })
            if fix_result and 'files' in fix_result:
                generated_files.update(fix_result['files'])
        
        validation_result = call_agent('code-validator', {
            'action': 'validate',
            'files': generated_files
        })
        issues = [i for i in (validation_result or {}).get('issues', []) if i.get('severity') == 'error']
    
    save_validation(conn, session_id, validation_result, fix_iteration)
    log_agent(conn, session_id, 'validator', 'validate', 
              f'Валидация завершена. Ошибок: {len(issues)}', status='success' if not issues else 'warning')
    
    update_session_status(conn, session_id, 'deploying', 'Развёртывание приложения')
    log_agent(conn, session_id, 'deployer', 'deploy', 'Коммит в GitHub и деплой')
    
    deploy_result = call_agent('agent-deployer', {
        'action': 'deploy',
        'project_name': project_name,
        'files': generated_files,
        'spec': spec.get('spec', {})
    })
    
    app_url = ''
    github_url = ''
    if deploy_result:
        app_url = deploy_result.get('app_url', '')
        github_url = deploy_result.get('github_url', '')
        log_agent(conn, session_id, 'deployer', 'deploy', f'Деплой завершен: {app_url}', status='success')
    else:
        log_agent(conn, session_id, 'deployer', 'deploy', 'Ошибка деплоя', status='error')
    
    build_time = int(time.time() - start_time)
    save_generated_files(conn, session_id, project_id, generated_files)
    finalize_session(conn, session_id, app_url, github_url, generated_files, total_tokens, total_cost)
    
    return {
        'session_id': session_id,
        'status': 'completed',
        'app_url': app_url,
        'github_url': github_url,
        'files_count': len(generated_files),
        'build_time_seconds': build_time,
        'spec': spec.get('spec', {}),
        'validation_warnings': [i for i in (validation_result or {}).get('issues', []) if i.get('severity') == 'warning']
    }


def call_agent(agent_name, payload):
    url = AGENT_URLS.get(agent_name, '')
    if not url:
        return None
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json()
        return {'error': f'{agent_name} вернул статус {response.status_code}: {response.text[:200]}'}
    except requests.Timeout:
        return {'error': f'{agent_name} превысил таймаут (120с)'}
    except Exception as e:
        return {'error': f'Ошибка вызова {agent_name}: {str(e)}'}


def get_build_status(session_id):
    if not session_id:
        return {'statusCode': 400, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'session_id обязателен'}), 'isBase64Encoded': False}
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, project_id, user_query, project_name, status, current_step, 
            spec, validation_issues, fix_iterations, error_message, app_url, github_url,
            ai_model_used, tokens_used, cost_usd, started_at, completed_at
            FROM build_sessions WHERE id = %s""",
            (session_id,)
        )
        row = cur.fetchone()
        if not row:
            return {'statusCode': 404, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Сессия не найдена'}), 'isBase64Encoded': False}
        
        cur.execute(
            """SELECT agent_role, action, output_summary, status, duration_ms, created_at 
            FROM agent_logs WHERE session_id = %s ORDER BY created_at ASC""",
            (session_id,)
        )
        logs = []
        for log_row in cur.fetchall():
            logs.append({
                'agent': log_row[0],
                'action': log_row[1],
                'message': log_row[2],
                'status': log_row[3],
                'duration_ms': log_row[4],
                'timestamp': log_row[5].isoformat() if log_row[5] else None
            })
        
        status = row[4]
        progress = calculate_progress(status)
        
        steps = get_steps_status(status)
        
        result = {
            'session_id': str(row[0]),
            'project_id': row[1],
            'user_query': row[2],
            'project_name': row[3],
            'status': status,
            'current_step': row[5],
            'progress': progress,
            'steps': steps,
            'spec': row[6],
            'validation_issues': row[7],
            'fix_iterations': row[8],
            'error_message': row[9],
            'app_url': row[10],
            'github_url': row[11],
            'ai_model_used': row[12],
            'tokens_used': row[13],
            'cost_usd': float(row[14]) if row[14] else 0,
            'started_at': row[15].isoformat() if row[15] else None,
            'completed_at': row[16].isoformat() if row[16] else None,
            'agent_logs': logs
        }
        
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(result, default=str), 'isBase64Encoded': False}
    finally:
        conn.close()


def calculate_progress(status):
    progress_map = {
        'started': 0.0,
        'analyzing': 0.1,
        'generating_db': 0.25,
        'generating_backend': 0.4,
        'generating_frontend': 0.6,
        'validating': 0.75,
        'fixing': 0.8,
        'deploying': 0.9,
        'completed': 1.0,
        'failed': 0.0
    }
    return progress_map.get(status, 0.0)


def get_steps_status(current_status):
    all_steps = ['analyzing', 'generating_db', 'generating_backend', 'generating_frontend', 'validating', 'deploying']
    step_labels = {
        'analyzing': 'Анализ требований',
        'generating_db': 'База данных',
        'generating_backend': 'Backend API',
        'generating_frontend': 'Интерфейс',
        'validating': 'Проверка кода',
        'deploying': 'Развёртывание'
    }
    
    if current_status == 'completed':
        return [{'key': s, 'label': step_labels[s], 'status': 'completed'} for s in all_steps]
    if current_status == 'failed':
        return [{'key': s, 'label': step_labels[s], 'status': 'failed'} for s in all_steps]
    
    steps = []
    found_current = False
    for s in all_steps:
        if s == current_status or (current_status == 'fixing' and s == 'validating'):
            steps.append({'key': s, 'label': step_labels[s], 'status': 'in_progress'})
            found_current = True
        elif not found_current:
            steps.append({'key': s, 'label': step_labels[s], 'status': 'completed'})
        else:
            steps.append({'key': s, 'label': step_labels[s], 'status': 'pending'})
    return steps


def update_session_status(conn, session_id, status, step_description):
    cur = conn.cursor()
    cur.execute("UPDATE build_sessions SET status = %s, current_step = %s WHERE id = %s", (status, step_description, session_id))
    conn.commit()


def update_session_error(conn, session_id, error_msg):
    try:
        cur = conn.cursor()
        cur.execute("UPDATE build_sessions SET status = 'failed', error_message = %s, completed_at = CURRENT_TIMESTAMP WHERE id = %s", (error_msg, session_id))
        conn.commit()
    except:
        pass


def save_spec(conn, session_id, spec):
    cur = conn.cursor()
    cur.execute("UPDATE build_sessions SET spec = %s WHERE id = %s", (json.dumps(spec), session_id))
    conn.commit()


def save_validation(conn, session_id, validation_result, fix_iterations):
    cur = conn.cursor()
    issues = json.dumps(validation_result.get('issues', []) if validation_result else [])
    cur.execute("UPDATE build_sessions SET validation_issues = %s, fix_iterations = %s WHERE id = %s", (issues, fix_iterations, session_id))
    conn.commit()


def save_generated_files(conn, session_id, project_id, files):
    cur = conn.cursor()
    for file_path, content in files.items():
        file_type = 'typescript'
        if file_path.endswith('.py'):
            file_type = 'python'
        elif file_path.endswith('.sql'):
            file_type = 'sql'
        elif file_path.endswith('.json'):
            file_type = 'json'
        elif file_path.endswith('.css'):
            file_type = 'css'
        
        cur.execute(
            """INSERT INTO project_files (project_id, file_path, content, file_type, size_bytes) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (project_id, file_path) DO UPDATE SET content = EXCLUDED.content, size_bytes = EXCLUDED.size_bytes, updated_at = CURRENT_TIMESTAMP""",
            (project_id, file_path, content, file_type, len(content.encode('utf-8')))
        )
    
    cur.execute("UPDATE build_sessions SET generated_files = %s WHERE id = %s", (json.dumps(list(files.keys())), session_id))
    conn.commit()


def log_agent(conn, session_id, agent_role, action, message, status='success', tokens_in=0, tokens_out=0, duration_ms=0):
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO agent_logs (session_id, agent_role, action, output_summary, status, tokens_in, tokens_out, duration_ms)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (session_id, agent_role, action, message, status, tokens_in, tokens_out, duration_ms)
        )
        conn.commit()
    except:
        pass


def finalize_session(conn, session_id, app_url, github_url, files, tokens, cost):
    cur = conn.cursor()
    cur.execute(
        """UPDATE build_sessions SET 
        status = 'completed', app_url = %s, github_url = %s, 
        tokens_used = %s, cost_usd = %s, completed_at = CURRENT_TIMESTAMP 
        WHERE id = %s""",
        (app_url, github_url, tokens, cost, session_id)
    )
    conn.commit()