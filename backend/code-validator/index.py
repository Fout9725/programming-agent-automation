import os
import json
import re
from typing import Dict, List
from pydantic import BaseModel

class ValidationRequest(BaseModel):
    files: Dict[str, str]
    language: str

class ValidationError(BaseModel):
    file: str
    line: int
    severity: str
    message: str
    rule: str

def handler(event: dict, context) -> dict:
    """Валидатор и автофикс для сгенерированного кода"""
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        request = ValidationRequest(**body)
        
        errors = []
        warnings = []
        
        for filepath, code in request.files.items():
            file_errors = validate_file(filepath, code)
            errors.extend(file_errors['errors'])
            warnings.extend(file_errors['warnings'])
        
        security_issues = scan_security(request.files)
        errors.extend(security_issues)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'passed': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'security_score': calculate_security_score(security_issues)
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def validate_file(filepath: str, code: str) -> Dict:
    """Валидация отдельного файла"""
    errors = []
    warnings = []
    
    if filepath.endswith('.ts') or filepath.endswith('.tsx'):
        ts_errors = validate_typescript(code)
        errors.extend(ts_errors)
        
        react_errors = validate_react_patterns(code)
        errors.extend(react_errors)
    
    elif filepath.endswith('.py'):
        py_errors = validate_python(code)
        errors.extend(py_errors)
    
    elif filepath.endswith('.sql'):
        sql_errors = validate_sql(code)
        errors.extend(sql_errors)
    
    return {'errors': errors, 'warnings': warnings}

def validate_typescript(code: str) -> List[Dict]:
    """Валидация TypeScript кода"""
    errors = []
    
    if re.search(r':\s*any\b', code):
        errors.append({
            'file': 'current',
            'line': 0,
            'severity': 'error',
            'message': 'Использование типа any запрещено',
            'rule': 'no-any'
        })
    
    if 'var ' in code:
        errors.append({
            'file': 'current',
            'line': 0,
            'severity': 'error',
            'message': 'Использование var вместо const/let',
            'rule': 'no-var'
        })
    
    if re.search(r'console\.log', code) and 'src/' in code:
        errors.append({
            'file': 'current',
            'line': 0,
            'severity': 'warning',
            'message': 'console.log в production коде',
            'rule': 'no-console'
        })
    
    return errors

def validate_react_patterns(code: str) -> List[Dict]:
    """Валидация React паттернов"""
    errors = []
    
    if re.search(r'useState.*\(.*\)\s*{', code):
        errors.append({
            'file': 'current',
            'line': 0,
            'severity': 'error',
            'message': 'useState внутри цикла или условия',
            'rule': 'react-hooks/rules-of-hooks'
        })
    
    if 'dangerouslySetInnerHTML' in code:
        errors.append({
            'file': 'current',
            'line': 0,
            'severity': 'error',
            'message': 'Использование dangerouslySetInnerHTML без санитизации',
            'rule': 'react/no-danger'
        })
    
    return errors

def validate_python(code: str) -> List[Dict]:
    """Валидация Python кода"""
    errors = []
    
    dangerous_patterns = [
        (r'eval\(', 'Использование eval() запрещено'),
        (r'exec\(', 'Использование exec() запрещено'),
        (r'__import__\(', 'Динамический импорт опасен'),
        (r'os\.system', 'os.system создает уязвимость'),
    ]
    
    for pattern, message in dangerous_patterns:
        if re.search(pattern, code):
            errors.append({
                'file': 'current',
                'line': 0,
                'severity': 'error',
                'message': message,
                'rule': 'security'
            })
    
    return errors

def validate_sql(code: str) -> List[Dict]:
    """Валидация SQL кода"""
    errors = []
    
    if re.search(r'SELECT\s+\*', code, re.IGNORECASE):
        errors.append({
            'file': 'current',
            'line': 0,
            'severity': 'warning',
            'message': 'Избегайте SELECT *, указывайте конкретные поля',
            'rule': 'sql-best-practices'
        })
    
    if re.search(r"WHERE.*=.*\+", code):
        errors.append({
            'file': 'current',
            'line': 0,
            'severity': 'error',
            'message': 'Возможная SQL инъекция через конкатенацию',
            'rule': 'sql-injection'
        })
    
    return errors

def scan_security(files: Dict[str, str]) -> List[Dict]:
    """Сканирование на уязвимости"""
    issues = []
    
    all_code = '\n'.join(files.values())
    
    sensitive_patterns = [
        (r'password\s*=\s*["\'].*["\']', 'Хардкод пароля'),
        (r'api[_-]?key\s*=\s*["\'].*["\']', 'Хардкод API ключа'),
        (r'secret\s*=\s*["\'].*["\']', 'Хардкод секрета'),
    ]
    
    for pattern, message in sensitive_patterns:
        if re.search(pattern, all_code, re.IGNORECASE):
            issues.append({
                'file': 'multiple',
                'line': 0,
                'severity': 'critical',
                'message': message,
                'rule': 'no-secrets'
            })
    
    return issues

def calculate_security_score(issues: List[Dict]) -> int:
    """Рассчитывает оценку безопасности 0-100"""
    if not issues:
        return 100
    
    score = 100
    
    for issue in issues:
        if issue['severity'] == 'critical':
            score -= 30
        elif issue['severity'] == 'error':
            score -= 15
        elif issue['severity'] == 'warning':
            score -= 5
    
    return max(0, score)
