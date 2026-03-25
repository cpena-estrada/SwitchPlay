# transfer.py

from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from ..database import get_connection
from ..utils import get_current_user_from_token


transfer_router = APIRouter()

#