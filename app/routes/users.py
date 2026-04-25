# users.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..database import get_connection
from ..utils import validate_uuid, hash_password

users_router = APIRouter()


def find_or_create_user(email: str, first_name: str, last_name: str) -> str:
    """
    Look up a user by email. If they don't exist, create them (no password — OAuth users (Google users)).
    Returns the user_id as a string.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()

        if existing:
            return str(existing[0])

        cursor.execute(
            """
            INSERT INTO users (first_name, last_name, email, password)
            VALUES (%s, %s, %s, NULL)
            RETURNING id
            """,
            (first_name, last_name, email)
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        return str(user_id)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str 


@users_router.post('/users')
def insert_user(user: UserCreate):
    """
    insert a user into users table
    """
    conn = get_connection()
    cursor = conn.cursor()

    try: 
        cursor.execute(
            """
            INSERT INTO users (first_name, last_name, email, password)
            VALUES (%s, %s, %s, %s)
            RETURNING id, first_name, last_name, email, created_at
            """,
            (user.first_name, user.last_name, user.email, hash_password(user.password))
        )
        new_user = cursor.fetchone()
        conn.commit()
        return {
            'id' : str(new_user[0]),
            'first_name': new_user[1],
            'last_name': new_user[2],
            'email': new_user[3],
            'created_at': str(new_user[4])
        }
    except Exception as e:
        conn.rollback() # undo failed insert
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@users_router.get('/users/{user_id}')
def get_user(user_id: str):
    validate_uuid(user_id)
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT 
                id,
                first_name,
                last_name,
                email
            FROM users
            WHERE id = %s
            """,
            (user_id,) # note it needs to be a tuple
        )
        user_data = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        'id' : str(user_data[0]),
        'first_name' : user_data[1],
        'last_name' : user_data[2],
        'email' : user_data[3]
    }


@users_router.get('/users')
def get_users():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT 
                id,
                first_name,
                last_name,
                email
            FROM users
            """
        )
        users = cursor.fetchall() # returns empty list if nothing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
    
    if not users:
        return [] # return empty list instead raising a 404
    
    users_data = []
    for user in users:
        users_data.append(
            {
                'id' : str(user[0]),
                'first_name' : user[1],
                'last_name' : user[2],
                'email' : user[3]
            }
        )
    return users_data

