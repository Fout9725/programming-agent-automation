import json
import os
import re
import base64
import urllib.request
import urllib.error

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
}

GITHUB_API = 'https://api.github.com'


def handler(event, context):
    """Агент деплоя — коммит в GitHub и генерация ссылки на приложение"""
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': '', 'isBase64Encoded': False}

    if event.get('httpMethod') != 'POST':
        return {'statusCode': 405, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Method not allowed'}), 'isBase64Encoded': False}

    body = json.loads(event.get('body', '{}'))
    action = body.get('action', '')

    if action == 'deploy':
        return deploy_project(body)

    return {'statusCode': 400, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Unknown action'}), 'isBase64Encoded': False}


def deploy_project(body):
    files = body.get('files', {})
    project_name = body.get('project_name', 'generated-project')
    spec = body.get('spec', {})

    if not files:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Нет файлов для деплоя'}),
            'isBase64Encoded': False
        }

    token = os.environ.get('GITHUB_TOKEN', '')
    if not token:
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'app_url': '',
                'github_url': '',
                'files_committed': 0,
                'message': 'GITHUB_TOKEN не настроен'
            }),
            'isBase64Encoded': False
        }

    repo_name = sanitize_repo_name(project_name)

    try:
        owner = get_authenticated_user(token)
        ensure_repo_exists(token, owner, repo_name, spec.get('description', f'Generated: {project_name}'))
        base_sha = get_base_commit_sha(token, owner, repo_name)

        tree_items = []
        for file_path, content in files.items():
            blob_sha = create_blob(token, owner, repo_name, content)
            tree_items.append({
                'path': file_path,
                'mode': '100644',
                'type': 'blob',
                'sha': blob_sha
            })

        tree_sha = create_tree(token, owner, repo_name, tree_items, base_sha)
        commit_message = f'feat: auto-generated project "{project_name}"'
        parent_shas = [base_sha] if base_sha else []
        commit_sha = create_commit(token, owner, repo_name, commit_message, tree_sha, parent_shas)
        update_ref(token, owner, repo_name, commit_sha, base_sha is None)

        github_url = f'https://github.com/{owner}/{repo_name}'
        app_url = f'https://{owner}.github.io/{repo_name}'

        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'app_url': app_url,
                'github_url': github_url,
                'files_committed': len(files),
                'commit_sha': commit_sha
            }),
            'isBase64Encoded': False
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': f'Ошибка деплоя: {str(e)}'}),
            'isBase64Encoded': False
        }


def sanitize_repo_name(name):
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '-', name.lower())
    sanitized = re.sub(r'-+', '-', sanitized).strip('-')
    return sanitized or 'generated-project'


def github_request(token, method, path, data=None):
    url = f'{GITHUB_API}{path}'
    body_bytes = json.dumps(data).encode('utf-8') if data else None

    req = urllib.request.Request(url, data=body_bytes, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    if body_bytes:
        req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        if e.code == 404:
            return None
        if e.code == 422:
            return {'already_exists': True}
        raise Exception(f'GitHub API error {e.code}: {error_body[:200]}')


def get_authenticated_user(token):
    result = github_request(token, 'GET', '/user')
    if not result or 'login' not in result:
        raise Exception('Не удалось получить пользователя GitHub')
    return result['login']


def ensure_repo_exists(token, owner, repo_name, description):
    result = github_request(token, 'GET', f'/repos/{owner}/{repo_name}')
    if result and 'id' in result:
        return

    create_result = github_request(token, 'POST', '/user/repos', {
        'name': repo_name,
        'description': description,
        'private': False,
        'auto_init': True
    })

    if not create_result:
        raise Exception(f'Не удалось создать репозиторий {repo_name}')


def get_base_commit_sha(token, owner, repo_name):
    result = github_request(token, 'GET', f'/repos/{owner}/{repo_name}/git/ref/heads/main')
    if result and 'object' in result:
        return result['object']['sha']

    result = github_request(token, 'GET', f'/repos/{owner}/{repo_name}/git/ref/heads/master')
    if result and 'object' in result:
        return result['object']['sha']

    return None


def create_blob(token, owner, repo_name, content):
    result = github_request(token, 'POST', f'/repos/{owner}/{repo_name}/git/blobs', {
        'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        'encoding': 'base64'
    })
    if not result or 'sha' not in result:
        raise Exception('Не удалось создать blob')
    return result['sha']


def create_tree(token, owner, repo_name, tree_items, base_tree_sha=None):
    payload = {'tree': tree_items}
    if base_tree_sha:
        commit = github_request(token, 'GET', f'/repos/{owner}/{repo_name}/git/commits/{base_tree_sha}')
        if commit and 'tree' in commit:
            payload['base_tree'] = commit['tree']['sha']

    result = github_request(token, 'POST', f'/repos/{owner}/{repo_name}/git/trees', payload)
    if not result or 'sha' not in result:
        raise Exception('Не удалось создать tree')
    return result['sha']


def create_commit(token, owner, repo_name, message, tree_sha, parent_shas):
    payload = {'message': message, 'tree': tree_sha}
    if parent_shas:
        payload['parents'] = parent_shas

    result = github_request(token, 'POST', f'/repos/{owner}/{repo_name}/git/commits', payload)
    if not result or 'sha' not in result:
        raise Exception('Не удалось создать commit')
    return result['sha']


def update_ref(token, owner, repo_name, commit_sha, is_new=False):
    if is_new:
        github_request(token, 'POST', f'/repos/{owner}/{repo_name}/git/refs', {
            'ref': 'refs/heads/main',
            'sha': commit_sha
        })
    else:
        result = github_request(token, 'GET', f'/repos/{owner}/{repo_name}/git/ref/heads/main')
        if result and 'object' in result:
            github_request(token, 'PATCH', f'/repos/{owner}/{repo_name}/git/refs/heads/main', {
                'sha': commit_sha,
                'force': True
            })
        else:
            github_request(token, 'PATCH', f'/repos/{owner}/{repo_name}/git/refs/heads/master', {
                'sha': commit_sha,
                'force': True
            })
