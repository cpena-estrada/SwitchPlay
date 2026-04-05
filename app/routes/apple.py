# apple.py

import os
import time
import requests
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from ..database import get_connection
from jose import jwt
from ..utils import get_current_user_from_token


apple_router = APIRouter()


def generate_apple_developer_token():
    """
    Generate a signed JWT developer token for Apple Music API.
    Uses the .p8 private key from Apple Developer portal.
    """
    load_dotenv()
    APPLE_KEY_ID = os.getenv('APPLE_KEY_ID')
    APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID')
    APPLE_PRIVATE_KEY = os.getenv('APPLE_PRIVATE_KEY')

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

    token = jwt.encode(payload, APPLE_PRIVATE_KEY, algorithm='ES256', headers=headers)
    return token


@apple_router.get('/auth/apple/developer-token')
def get_developer_token(token: str):
    """
    Returns the Apple Music developer token for the frontend to use with MusicKit JS.

    Frontend then will give then give us the apple music user acces token.
    Requires JWT so only logged-in users can access it.
    """
    get_current_user_from_token(token)  # just verifies the JWT is valid
    developer_token = generate_apple_developer_token()
    return {'developer_token': developer_token}


def get_apple_music_access_token(token: str):
    """
    Helper function to get Apple Music user token from platform_auth
    """
    user_id = get_current_user_from_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT access_token
            FROM platform_auth
            WHERE user_id = %s AND platform = 'apple_music'
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
        raise HTTPException(status_code=404, detail="Apple Music not connected")

    return result[0]

@apple_router.get('/apple/playlists')
def get_apple_music_playlists(token: str):
    """
    Get all apple music playlist for a given user
    """
    
    developer_token = generate_apple_developer_token()
    music_user_token = get_apple_music_access_token(token)

    response = requests.get(
        "https://api.music.apple.com/v1/me/library/playlists",
        headers= {
            'Authorization': f'Bearer {developer_token}',
            'Music-User-Token': music_user_token
        }
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail='Could not fetch users Apple Music playlsits')
    
    # get metadata of playlist
    apple_data = response.json()
    playlists = []
    for p in apple_data['data']:
        playlists.append({
            'id': p['id'],
            'name': p['attributes']['name'],
            'total_tracks': 'i dont know how many'  # Apple doesn't provide this in the response
        })

    return playlists


@apple_router.get('/apple/playlists/{playlist_id}')
def get_apple_music_playlist_tracks(token: str, playlist_id: str):

    developer_token = generate_apple_developer_token()
    music_user_token = get_apple_music_access_token(token)
    
    response = requests.get(
        f"https://api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks",
        headers= {
            'Authorization': f'Bearer {developer_token}',
            'Music-User-Token': music_user_token
        }
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail='Could not fetch tracks from playlist')
    
    apple_data = response.json()
    tracks = []

    for item in apple_data['data']:
        tracks.append({
            'name': item['attributes']['name'],
            'artist': item['attributes']['artistName'],
            'album': item['attributes']['albumName']
        })
    
    return tracks

def search_apple_music(items: list):
    """
    Search Apple Music catalog to find Apple Music song IDs for songs in a transfer request.

    *Searches a list of songs*
    """
    developer_token = generate_apple_developer_token()
    storefront = 'us' # we want us catalog

    matched_ids = []       # Apple Music song IDs
    matched_db_ids = []    # transfer_items IDs that were found
    not_found_ids = []     # transfer_items IDs that weren't found

    for item in items:
        item_id = item[0]
        song_name = item[1]
        artist_name = item[2]

        search_response = requests.get(
            f"https://api.music.apple.com/v1/catalog/{storefront}/search",
            headers={'Authorization': f'Bearer {developer_token}'},
            params={
                'term': f'{song_name} {artist_name}',
                'types': 'songs',
                'limit': 1
            }
        )

        if search_response.status_code != 200:
            not_found_ids.append(item_id)
            continue

        search_data = search_response.json()
        songs = search_data.get('results', {}).get('songs', {}).get('data', [])

        if len(songs) > 0:
            matched_ids.append(songs[0]['id'])
            matched_db_ids.append(item_id)
        else:
            not_found_ids.append(item_id)

    return matched_ids, matched_db_ids, not_found_ids
