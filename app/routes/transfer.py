# transfer.py

import random
import string
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .spotify import get_playlist_tracks
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