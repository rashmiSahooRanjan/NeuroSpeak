"""
NeuroSpeak – Authentication Module
JWT-based login, registration, role-based access control.
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

SECRET_KEY = os.environ.get('SECRET_KEY', 'neurospeak-secret-key-2024')
TOKEN_EXPIRY_HOURS = 24

# ─── PASSWORD HASHING ────────────────────────────────────────────────────────

def hash_password(plain_text: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_text.encode(), salt).decode()

def verify_password(plain_text: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain_text.encode(), hashed.encode())


# ─── JWT ─────────────────────────────────────────────────────────────────────

def generate_token(user_id: str, email: str, role: str) -> str:
    payload = {
        'sub': user_id,
        'email': email,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])


# ─── DECORATORS ──────────────────────────────────────────────────────────────

def require_auth(f):
    """Decorator: require valid JWT in Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401
        token = auth.split(' ', 1)[1]
        try:
            payload = decode_token(token)
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': f'Invalid token: {e}'}), 401
        return f(*args, **kwargs)
    return decorated

def require_role(*roles):
    """Decorator: restrict to specific roles (doctor, admin, patient)."""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            user_role = getattr(request, 'user', {}).get('role', '')
            if user_role not in roles:
                return jsonify({'error': f'Access denied. Required: {roles}'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
