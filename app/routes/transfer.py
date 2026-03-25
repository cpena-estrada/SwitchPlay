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

    # generate a share code
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
