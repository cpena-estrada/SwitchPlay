# spotify.py

import os
import requests
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from ..database import get_connection
from ..utils import get_current_user_from_token
from datetime import datetime, timedelta


spotify_router = APIRouter()


def refresh_spotify_token(user_id: str, refresh_token: str):
    """
    Use refresh token from a a spotify-signed-in user to update access token

    Call when current access token has expired
    """

    load_dotenv()
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
        }
    )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail='Failed to refresh Spotify token. Please reconnect.')

    new_token_data = response.json()
    new_access_token = new_token_data['access_token']
    new_expires_at = datetime.now() + timedelta(seconds=new_token_data['expires_in'])

    # update the token in the database
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE platform_auth
            SET 
                access_token = %s,
                expires_at = %s
            WHERE user_id = %s AND platform = 'spotify'
            """,
            (new_access_token, new_expires_at, user_id)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return new_access_token


def get_spotify_access_token(token: str):
    """
    Helper function to get spotify access token
    """
    
    user_id = get_current_user_from_token(token)

    conn = get_connection()
    cursor = conn.cursor() 

    try:
        cursor.execute(
            """
            SELECT
                access_token,
                refresh_token,
                expires_at
            FROM platform_auth
            WHERE user_id = %s AND platform = 'spotify'
            """,
            (user_id,)
        )
        result = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    if result is None:
        raise HTTPException(status_code=404, detail="Spotify not connected")
    
    access_token = result[0]
    refresh_token = result[1]
    expires_at = result [2]

    # refresh it if needed
    if datetime.now() > expires_at:
        access_token = refresh_spotify_token(user_id, refresh_token)

    return access_token


@spotify_router.get('/spotify/playlists')
def get_playlist(token: str):
    """
    Get a users access token and call spotify api to fetch all their playlists
    """
    access_token = get_spotify_access_token(token)

    response = requests.get(
        "https://api.spotify.com/v1/me/playlists",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail= 'Failed to fetch playlists from Spotify')
    
    # get user's playlist metadata
    spotify_data = response.json()
    playlists = []
    for p in spotify_data['items']:
        playlists.append({
            'id': p['id'],
            'name': p['name'],
            'total_tracks': p['tracks']['total']
        })
    
    return playlists

@spotify_router.get('/spotify/playlists/{playlist_id}')
def get_playlist_tracks(playlist_id: str, token: str):
    """
    Get all tracks from a specific Spotify playlist through its id
    """

    access_token = get_spotify_access_token(token)

    response = requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail='Failed to fetch tracks from Spotify')

    spotify_data = response.json()
    tracks = []
    for item in spotify_data['items']:
        track = item['track']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        tracks.append({
            'name': track['name'],
            'artist': artists,
            'album': track['album']['name']
        })

    return tracks