from fastapi import APIRouter, Query, Request, Depends, Response, encoders
from typing import List, Optional
from app.db.session import get_db
from app.db.crud import (
    get_genes,test
)
from app.db.schemas import GeneBase

cluster_router = r = APIRouter()

@r.get(
    "/cluster/{gene_id}",
    #response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def cluster_tree(
        response: Response,
        db=Depends(get_db)
):
    """Get all genes"""
    genes = get_genes(db)
    return genes

@r.get(
    "/test_genes",
    #response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def test_genes_list(
        response: Response,
        db=Depends(get_db),
        q: List[str] = Query(None)
):
    """Get all genes"""
    genes = test(db,q)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    return genes
