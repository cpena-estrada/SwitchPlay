# stats.py
#
# This file exists to satisfy class requirements (Phase 4 + 5).
# It calls views and stored procedures created in Supabase.
# The rest of the app does NOT depend on this file.
#
# To remove after the class:
#   1. Delete this file
#   2. Remove the import + include_router lines for stats_router in app/main.py
#   3. Remove StatsPage from the frontend
#   4. Drop the views/procedures from Supabase

from fastapi import APIRouter, HTTPException
from ..database import get_connection
from ..utils import get_current_user_from_token

stats_router = APIRouter()


@stats_router.get('/stats/users')
def stats_users(token: str):
    """Uses the user_transfer_summary VIEW."""
    get_current_user_from_token(token)  # require auth

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT user_id, first_name, last_name, email,
                   total_transfers, completed_transfers, created_at
            FROM user_transfer_summary
            ORDER BY total_transfers DESC
            """
        )
        rows = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return [
        {
            'user_id': str(r[0]),
            'first_name': r[1],
            'last_name': r[2],
            'email': r[3],
            'total_transfers': r[4],
            'completed_transfers': r[5],
            'created_at': str(r[6]),
        }
        for r in rows
    ]


@stats_router.get('/stats/platforms')
def stats_platforms(token: str):
    """Uses the transfer_platform_stats() stored PROCEDURE."""
    get_current_user_from_token(token)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM transfer_platform_stats()")
        rows = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return [
        {
            'source_platform': r[0],
            'target_platform': r[1],
            'total_transfers': r[2],
            'completed_transfers': r[3],
            'avg_tracks': float(r[4]) if r[4] is not None else 0,
        }
        for r in rows
    ]


@stats_router.get('/stats/my-connections')
def stats_my_connections(token: str):
    """Uses the platform_connection_status VIEW (scoped to current user)."""
    user_id = get_current_user_from_token(token)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT spotify_connected, apple_connected
            FROM platform_connection_status
            WHERE user_id = %s
            """,
            (user_id,)
        )
        row = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    if row is None:
        return {'spotify_connected': False, 'apple_connected': False}
    return {'spotify_connected': row[0], 'apple_connected': row[1]}
