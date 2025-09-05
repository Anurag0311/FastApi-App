from fastapi import APIRouter
from DB.connection import db_dependency

import traceback


router = APIRouter()


@router.get("/get")
async def get_books(session: db_dependency):
    try:
        pass
    except Exception as e:
        traceback.print_exc()
