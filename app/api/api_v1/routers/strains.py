from fastapi import APIRouter, Request, Depends, Response, encoders
import typing as t
from app.db.session import get_db
from app.db.crud import (
    get_strains,
)
from app.db.schemas import StrainBase

strains_router = r = APIRouter()


@r.get(
    "/strains",
    #response_model=t.List[StrainBase],
    response_model_exclude_none=True,
)
async def strains_list(
        response: Response,
        db=Depends(get_db)
):
    """Get all strains"""
    strains = get_strains(db)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    return strains
