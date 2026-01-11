import json
import os
import psycopg2
from datetime import datetime

def handler(event: dict, context) -> dict:
    """
    API для управления проектами агента разработки.
    Поддерживает создание, получение, обновление проектов и версионирование изменений.
    """
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        if method == 'GET':
            project_id = event.get('queryStringParameters', {}).get('id')
            
            if project_id:
                cur.execute("""
                    SELECT id, name, description, project_type, technologies, 
                           github_url, status, created_at, updated_at
                    FROM projects WHERE id = %s
                """, (project_id,))
                row = cur.fetchone()
                
                if not row:
                    return create_response(404, {'error': 'Project not found'})
                
                project = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'project_type': row[3],
                    'technologies': row[4],
                    'github_url': row[5],
                    'status': row[6],
                    'created_at': row[7].isoformat() if row[7] else None,
                    'updated_at': row[8].isoformat() if row[8] else None
                }
                
                cur.execute("""
                    SELECT COUNT(*) FROM project_versions WHERE project_id = %s
                """, (project_id,))
                project['versions_count'] = cur.fetchone()[0]
                
                return create_response(200, project)
            else:
                cur.execute("""
                    SELECT id, name, description, project_type, status, created_at
                    FROM projects ORDER BY created_at DESC LIMIT 50
                """)
                projects = []
                for row in cur.fetchall():
                    projects.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'project_type': row[3],
                        'status': row[4],
                        'created_at': row[5].isoformat() if row[5] else None
                    })
                
                return create_response(200, {'projects': projects})
        
        elif method == 'POST':
            data = json.loads(event.get('body', '{}'))
            
            cur.execute("""
                INSERT INTO projects (name, description, project_type, technologies, github_url)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, name, created_at
            """, (
                data.get('name'),
                data.get('description'),
                data.get('project_type'),
                json.dumps(data.get('technologies', [])),
                data.get('github_url')
            ))
            
            row = cur.fetchone()
            conn.commit()
            
            project = {
                'id': row[0],
                'name': row[1],
                'created_at': row[2].isoformat() if row[2] else None,
                'message': 'Project created successfully'
            }
            
            return create_response(201, project)
        
        elif method == 'PUT':
            data = json.loads(event.get('body', '{}'))
            project_id = data.get('id')
            
            if not project_id:
                return create_response(400, {'error': 'Project ID required'})
            
            cur.execute("""
                UPDATE projects 
                SET name = %s, description = %s, github_url = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, name, updated_at
            """, (
                data.get('name'),
                data.get('description'),
                data.get('github_url'),
                project_id
            ))
            
            row = cur.fetchone()
            if not row:
                return create_response(404, {'error': 'Project not found'})
            
            conn.commit()
            
            return create_response(200, {
                'id': row[0],
                'name': row[1],
                'updated_at': row[2].isoformat() if row[2] else None,
                'message': 'Project updated successfully'
            })
        
        else:
            return create_response(405, {'error': 'Method not allowed'})
    
    except Exception as e:
        return create_response(500, {'error': str(e)})
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()


def create_response(status_code: int, body: dict) -> dict:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body),
        'isBase64Encoded': False
    }
