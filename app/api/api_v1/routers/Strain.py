from fastapi import APIRouter, Request, Depends, Response, encoders
import typing as t
from app.db.session import get_db
from app.db.crud import (
    get_genes,
)
from app.db.schemas import GeneBase

genes_router = r = APIRouter()


@r.get(
    "/genes",
    #response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def genes_list(
        response: Response,
        db=Depends(get_db)
):
    """Get all genes"""
    genes = get_genes(db)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    return genes
