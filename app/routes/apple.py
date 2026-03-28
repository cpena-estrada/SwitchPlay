# apple.py

import os
import time
import requests
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from jose import jwt


apple_router = APIRouter()


def generate_apple_developer_token():
    """
    Generate a signed JWT developer token for Apple Music API.
    Uses the .p8 private key from Apple Developer portal.
    """
    load_dotenv()
    APPLE_KEY_ID = os.getenv('APPLE_KEY_ID')
    APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID')
    APPLE_PRIVATE_KEY_PATH = os.getenv('APPLE_PRIVATE_KEY_PATH')

    with open(APPLE_PRIVATE_KEY_PATH, 'r') as f:
        private_key = f.read()

    now = int(time.time())

    headers = {
        'alg': 'ES256',
        'kid': APPLE_KEY_ID
    }

    payload = {
        'iss': APPLE_TEAM_ID,
        'iat': now,
        'exp': now + (60 * 60 * 24 * 180)  # 180 days (max is 6 months)
    }

    token = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
    return token
