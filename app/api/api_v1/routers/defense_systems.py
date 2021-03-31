from fastapi import APIRouter, Request, Depends, Response, encoders, Query
from app.db.session import get_db
from app.db.crud import (
    get_defense_systems_names
)

defense_systems_router = r = APIRouter()

# returns all of the defense systems


@r.get(
    "/",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_defense_systems(response: Response, db=Depends(get_db)):
    df = get_defense_systems_names(db)
    return df