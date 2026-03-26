# transfer.py

import random
import string
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .spotify import get_playlist_tracks, get_spotify_access_token
from ..database import get_connection
from ..utils import get_current_user_from_token


class TransferCreate(BaseModel):
    source_platform: str
    target_platform: str
    playlist_id: str
    title: str


transfer_router = APIRouter()


@transfer_router.post('/transfers')
def make_transfer_request(transfer: TransferCreate, token: str):
    user_id = get_current_user_from_token(token)

    source_platform = transfer.source_platform
    target_platform = transfer.target_platform
    playlist_id = transfer.playlist_id
    title = transfer.title

    # generate a random share code
    share_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # fetch tracks from source platform
    if source_platform == 'spotify':
        tracks = get_playlist_tracks(playlist_id, token)
    elif source_platform == 'apple_music':
        raise HTTPException(status_code=400, detail="Apple Music not supported yet")
    else:
        raise HTTPException(status_code=400, detail="Invalid source platform")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # create the transfer request
        cursor.execute(
            """
            INSERT INTO transfer_requests (share_code, title, source_platform, target_platform, sender_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (share_code, title, source_platform, target_platform, user_id)
        )
        transfer_request_id = cursor.fetchone()[0]

        # insert all tracks as transfer items
        cursor.executemany(
            """
            INSERT INTO transfer_items (song_name, artist_name, album, transfer_request_id)
            VALUES (%s, %s, %s, %s)
            """,
            [(t['name'], t['artist'], t['album'], transfer_request_id) for t in tracks]
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {
        'message': 'Transfer request created',
        'share_code': share_code,
        'total_tracks': len(tracks)
    }


@transfer_router.get('/transfers/{share_code}')
def get_transfer(share_code: str):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # find trasnfer request with given share code
        cursor.execute(
            """
            SELECT
                id,
                title,
                source_platform,
                target_platform,
                status
            FROM transfer_requests
            WHERE share_code = %s
            """,
            (share_code,)
        )

        transfer_data = cursor.fetchone()

        if transfer_data is None:
            raise HTTPException(status_code=404, detail="Transfer not found")

        transfer_request_id = transfer_data[0]

        # find transfer items from the found transfer request id
        cursor.execute(
            """
            SELECT
                song_name,
                artist_name,
                album
            FROM transfer_items
            WHERE transfer_request_id = %s
            """,
            (transfer_request_id,)
        )

        tracks = cursor.fetchall()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {
        'title': transfer_data[1],
        'source_platform': transfer_data[2],
        'target_platform': transfer_data[3],
        'status': transfer_data[4],
        'tracks': [
            {
                'song_name': t[0],
                'artist_name': t[1],
                'album': t[2]
            }
            for t in tracks
        ]
    }


@transfer_router.post('/transfers/{share_code}/accept')
def accept_transfer(share_code: str, token: str):
    """
    Receiver accepts a transfer request
    """
    user_id = get_current_user_from_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # find the transfer request
        cursor.execute(
            """
            SELECT 
                id,
                status,
                sender_id
            FROM transfer_requests
            WHERE share_code = %s
            """,
            (share_code,)
        )
        transfer = cursor.fetchone()

        if transfer is None:
            raise HTTPException(status_code=404, detail="Transfer not found")

        if transfer[1] != 'created':
            raise HTTPException(status_code=400, detail="Transfer has already been accepted")

        if transfer[2] == user_id:
            raise HTTPException(status_code=400, detail="You cannot accept your own transfer")

        # update the transfer with receiver_id and status
        cursor.execute(
            """
            UPDATE transfer_requests
            SET receiver_id = %s, status = 'accepted'
            WHERE id = %s
            """,
            (user_id, transfer[0])
        )
        conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {'message': 'Transfer accepted'}


def transfer_to_spotify(access_token: str, title: str, items: list):
    """
    Search for each song on Spotify, create a playlist, and add matched songs.
    Returns (playlist_id, matched_ids, not_found_ids)
    """
    matched_uris = []
    matched_ids = []
    not_found_ids = []

    # search for each song on spotify
    for item in items:
        item_id = item[0]
        song_name = item[1]
        artist_name = item[2]

        search_response = requests.get(
            "https://api.spotify.com/v1/search",
            headers={'Authorization': f'Bearer {access_token}'},
            params={
                'q': f'track:{song_name} artist:{artist_name}',
                'type': 'track',
                'limit': 1
            }
        )

        if search_response.status_code != 200:
            not_found_ids.append(item_id)
            continue

        search_data = search_response.json()
        tracks = search_data.get('tracks', {}).get('items', [])

        if len(tracks) > 0:
            matched_uris.append(tracks[0]['uri'])
            matched_ids.append(item_id)
        else:
            not_found_ids.append(item_id)

    # create a new playlist
    create_response = requests.post(
        "https://api.spotify.com/v1/me/playlists",
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        json={
            'name': title,
            'description': 'Transferred via SwitchPlay'
        }
    )

    print(f"Create playlist status: {create_response.status_code}")
    print(f"Create playlist response: {create_response.json()}")

    if create_response.status_code != 201:
        raise HTTPException(status_code=500, detail="Failed to create playlist on Spotify")

    new_playlist_id = create_response.json()['id']

    # add matched songs to the new playlist
    if len(matched_uris) > 0:
        add_response = requests.post(
            f"https://api.spotify.com/v1/playlists/{new_playlist_id}/items",
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            json={'uris': matched_uris}
        )

        if add_response.status_code != 201:
            raise HTTPException(status_code=500, detail="Failed to add songs to playlist")

    return new_playlist_id, matched_ids, not_found_ids


@transfer_router.post('/transfers/{share_code}/complete')
def complete_transfer(share_code: str, token: str):
    """
    Search for each song on the target platform, create a playlist, and add matched songs
    """
    user_id = get_current_user_from_token(token)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # find the transfer request
        cursor.execute(
            """
            SELECT id, title, status, receiver_id, target_platform
            FROM transfer_requests
            WHERE share_code = %s
            """,
            (share_code,)
        )
        transfer = cursor.fetchone()

        if transfer is None:
            raise HTTPException(status_code=404, detail="Transfer not found")

        if transfer[2] != 'accepted':
            raise HTTPException(status_code=400, detail="Transfer must be accepted before completing")

        if transfer[3] != user_id:
            raise HTTPException(status_code=403, detail="Only the receiver can complete the transfer")

        transfer_id = transfer[0]
        title = transfer[1]
        target_platform = transfer[4]

        # get all songs from transfer_items
        cursor.execute(
            """
            SELECT id, song_name, artist_name, album
            FROM transfer_items
            WHERE transfer_request_id = %s
            """,
            (transfer_id,)
        )
        items = cursor.fetchall()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    # route to the correct platform
    if target_platform == 'spotify':
        access_token = get_spotify_access_token(token)
        new_playlist_id, matched_ids, not_found_ids = transfer_to_spotify(access_token, title, items)
    elif target_platform == 'apple_music':
        raise HTTPException(status_code=400, detail="Apple Music not supported yet")
    else:
        raise HTTPException(status_code=400, detail="Unsupported target platform")

    # update match_status for each transfer item and mark transfer as completed
    conn = get_connection()
    cursor = conn.cursor()

    try:
        for item_id in matched_ids:
            cursor.execute(
                """
                UPDATE transfer_items
                SET match_status = 'matched'
                WHERE id = %s
                """,
                (item_id,)
            )

        for item_id in not_found_ids:
            cursor.execute(
                """
                UPDATE transfer_items
                SET match_status = 'not_found'
                WHERE id = %s
                """,
                (item_id,)
            )

        cursor.execute(
            """
            UPDATE transfer_requests
            SET status = 'completed'
            WHERE id = %s
            """,
            (transfer_id,)
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {
        'message': 'Transfer completed',
        'playlist_id': new_playlist_id,
        'matched': len(matched_ids),
        'not_found': len(not_found_ids)
    }