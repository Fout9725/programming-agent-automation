import json
import os
import urllib.request
import urllib.parse
import urllib.error

def handler(event: dict, context) -> dict:
    '''GitHub OAuth интеграция - авторизация и получение репозиториев'''
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    params = event.get('queryStringParameters', {}) or {}
    action = params.get('action', '')
    
    if action == 'callback':
        code = params.get('code')
        if not code:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Код авторизации не получен'}),
                'isBase64Encoded': False
            }
        
        token_data = {
            'client_id': 'Ov23liCl4I7JbP2Bt2Ob',
            'client_secret': os.environ.get('GITHUB_CLIENT_SECRET', ''),
            'code': code
        }
        
        try:
            token_request = urllib.request.Request(
                'https://github.com/login/oauth/access_token',
                data=urllib.parse.urlencode(token_data).encode('utf-8'),
                headers={'Accept': 'application/json'}
            )
            
            with urllib.request.urlopen(token_request) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            if 'access_token' not in result:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': result.get('error_description', 'Не удалось получить токен')}),
                    'isBase64Encoded': False
                }
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'access_token': result['access_token']}),
                'isBase64Encoded': False
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Ошибка при получении токена: {str(e)}'}),
                'isBase64Encoded': False
            }
    
    elif action == 'repos':
        auth_header = event.get('headers', {}).get('X-Authorization', '')
        token = auth_header.replace('Bearer ', '').strip()
        
        if not token:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Токен авторизации не предоставлен'}),
                'isBase64Encoded': False
            }
        
        try:
            repos_request = urllib.request.Request(
                'https://api.github.com/user/repos?sort=updated&per_page=10',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/vnd.github+json',
                    'X-GitHub-Api-Version': '2022-11-28'
                }
            )
            
            with urllib.request.urlopen(repos_request) as response:
                repos_data = json.loads(response.read().decode('utf-8'))
            
            repositories = []
            for repo in repos_data:
                repositories.append({
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'url': repo['html_url'],
                    'description': repo.get('description', ''),
                    'language': repo.get('language', ''),
                    'stars': repo.get('stargazers_count', 0),
                    'updated_at': repo['updated_at'],
                    'default_branch': repo.get('default_branch', 'main')
                })
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'repositories': repositories}),
                'isBase64Encoded': False
            }
            
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            return {
                'statusCode': e.code,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'GitHub API ошибка: {error_msg}'}),
                'isBase64Encoded': False
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Ошибка при получении репозиториев: {str(e)}'}),
                'isBase64Encoded': False
            }
    
    return {
        'statusCode': 400,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Некорректный action параметр'}),
        'isBase64Encoded': False
    }
