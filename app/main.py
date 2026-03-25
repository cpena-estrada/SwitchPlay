from fastapi import FastAPI
from app.routes.users import users_router
from app.routes.auth import auth_router
from app.routes.spotify import spotify_router
from app.routes.transfer import transfer_router
from app.database import get_connection

app = FastAPI(
    title="SwitchPlay",
    description="API for transferring playlists between streaming platforms",
    version="0.1.0",
)

# set routers
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(spotify_router)
app.include_router(transfer_router)


@app.get("/")
def root():
    return {"message": "Welcome to SwitchPlay"}

"""
kill old server:
lsof -ti:8000 | xargs kill

starting it:
python3 -m uvicorn app.main:app --reload

http://127.0.0.1:8000/docs
"""
