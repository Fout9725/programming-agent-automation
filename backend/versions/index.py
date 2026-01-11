import json
import os
import psycopg2
from datetime import datetime

def handler(event: dict, context) -> dict:
    """
    API для управления версиями проектов (версионирование изменений для отката).
    Позволяет создавать снапшоты изменений и откатывать их.
    """
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
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
            project_id = event.get('queryStringParameters', {}).get('project_id')
            
            if not project_id:
                return create_response(400, {'error': 'project_id required'})
            
            cur.execute("""
                SELECT id, version_number, change_type, change_description, 
                       files_changed, ai_model, created_at
                FROM project_versions 
                WHERE project_id = %s 
                ORDER BY version_number DESC
                LIMIT 50
            """, (project_id,))
            
            versions = []
            for row in cur.fetchall():
                versions.append({
                    'id': row[0],
                    'version_number': row[1],
                    'change_type': row[2],
                    'change_description': row[3],
                    'files_changed': row[4],
                    'ai_model': row[5],
                    'created_at': row[6].isoformat() if row[6] else None
                })
            
            return create_response(200, {'versions': versions})
        
        elif method == 'POST':
            data = json.loads(event.get('body', '{}'))
            project_id = data.get('project_id')
            
            if not project_id:
                return create_response(400, {'error': 'project_id required'})
            
            cur.execute("""
                SELECT COALESCE(MAX(version_number), 0) + 1 
                FROM project_versions 
                WHERE project_id = %s
            """, (project_id,))
            next_version = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO project_versions 
                (project_id, version_number, change_type, change_description, 
                 files_changed, diff_content, ai_model)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, version_number, created_at
            """, (
                project_id,
                next_version,
                data.get('change_type', 'modification'),
                data.get('change_description'),
                json.dumps(data.get('files_changed', [])),
                data.get('diff_content'),
                data.get('ai_model')
            ))
            
            row = cur.fetchone()
            conn.commit()
            
            return create_response(201, {
                'id': row[0],
                'version_number': row[1],
                'created_at': row[2].isoformat() if row[2] else None,
                'message': 'Version created successfully'
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
