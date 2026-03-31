# auth.py

import os
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from dotenv import load_dotenv
from ..database import get_connection
from ..utils import create_token, get_current_user_from_token
from datetime import datetime, timedelta


auth_router = APIRouter()


class AppleCallbackRequest(BaseModel):
    music_user_token: str

class LoginRequest(BaseModel):
    email: str
    password: str


@auth_router.post('/auth/login')
def login(body: LoginRequest):
    """
    Create a JWT token for the given user if an only if they exist in DB
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT
                id
            FROM users
            WHERE email = %s AND password = %s
            """,
            (body.email, body.password)
        )
        user_id = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    # found no match
    if user_id is None:
        raise HTTPException(status_code=401, detail='Invalid email or password')
        
    token = create_token(str(user_id[0])) # [0] because its a tuple
    return {'access_token': token}


@auth_router.get('/auth/spotify')
def spotify_login(token: str):
    """
    build URL to redirect user to spotifys login page

    Note: 
    use state parameter to store user_id, so it is available in the callback
    """
    load_dotenv()
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
    scope = 'playlist-read-private playlist-modify-private playlist-modify-public'
    user_id = get_current_user_from_token(token)

    params = urlencode({
        'client_id' : SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri' : SPOTIFY_REDIRECT_URI,
        'state' : user_id,
        'scope' : scope,
        'show_dialog': 'true' # remove so it remebers auth and doesnt take you to spotify login page everytime
    })

    url = f"https://accounts.spotify.com/authorize?{params}"
    
    return RedirectResponse(url=url)


@auth_router.get('/auth/callback')
def spotify_callback(code: str = None, error: str = None, state: str = None):
    """
    exchange spotify code for spotify access token, store in platform_auth table
    """

    load_dotenv()
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

    if code is None:
        raise HTTPException(status_code=400, detail=f'Spotify auth error: {error}')
    
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type' : 'authorization_code',
            'code' : code,
            'redirect_uri' : SPOTIFY_REDIRECT_URI,
            'client_id' : SPOTIFY_CLIENT_ID,
            'client_secret' : SPOTIFY_CLIENT_SECRET
        }
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail='unable to get spotify acces token')
    
    spotify_response = response.json()

    # this section could/should be its own function but oh well
    user_id = state
    access_token = spotify_response['access_token']
    refresh_token = spotify_response['refresh_token']
    expires_at = datetime.now() + timedelta(seconds=spotify_response['expires_in'])     # spotify returns seconds, in db its a TIMESTAMP. convert

    conn = get_connection()
    cursor = conn.cursor() 
 
    try:
        cursor.execute(
            """
            INSERT INTO platform_auth (user_id, platform, access_token, refresh_token, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, platform)
            DO UPDATE SET
                access_token = EXCLUDED.access_token,
                refresh_token = EXCLUDED.refresh_token,
                expires_at = EXCLUDED.expires_at
            """,
            (user_id, 'spotify', access_token, refresh_token, expires_at)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {
        'message': 'Spotify connected succsessfully',
        'user_id': user_id
    }


@auth_router.post('/auth/apple/callback')
def apple_callback(token: str, body: AppleCallbackRequest):
    """
    Save Apple Music user token to platform_auth.
    Called by the frontend after MusicKit JS authorization.
    """
    user_id = get_current_user_from_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO platform_auth (user_id, platform, access_token)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, platform)
            DO UPDATE SET access_token = EXCLUDED.access_token
            """,
            (user_id, 'apple_music', body.music_user_token)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {'message': 'Apple Music connected successfully'}

