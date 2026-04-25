import os
from uuid import UUID
from fastapi import HTTPException
import bcrypt
from jose import jwt
from datetime import datetime, timedelta

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def validate_uuid(id_string: str):
    """
    Check if a string is a valid UUID format.
    Raises 400 if not.
    """
    try:
        UUID(id_string)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")


# Auth Helper Functions
def create_token(user_id: str):
    """
    Creates a JWT token for the given user id

    Token is then used in all following API calls for auth
    """

    SECRET_KEY = os.getenv('SECRET_KEY')

    payload = {
        'user_id': user_id,
        'exp': datetime.now() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def get_current_user_from_token(token: str):
    """
    generate and return a JWT token for a user
    """
    SECRET_KEY = os.getenv('SECRET_KEY')

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except:
        raise HTTPException(status_code=401, detail='Invalid token')