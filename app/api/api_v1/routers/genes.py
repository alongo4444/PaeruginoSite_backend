from fastapi import APIRouter, Query, Request, Depends, Response, encoders
from typing import List, Optional


from app.db.session import get_db
from app.db.crud import (
    get_genes, get_genes_download, get_genes_by_defense, prepare_file
)
from app.db.schemas import GeneBase

genes_router = r = APIRouter()

@r.get(
    "/",
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

@r.get(
    "/download_genes",
    #response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def download_genes(
        response: Response,
        db=Depends(get_db),
        selectedC: List[str] = Query(None), # the selected columns to return
        selectedAS: List[str] = Query(None) # the strains that were selected by the user
):
    """Get all genes"""
    genes = get_genes_download(db, selectedC, selectedAS)

    return prepare_file(genes)

@r.get(
    "/genes_by_defense",
    #response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def genes_by_defense(
        response: Response,
        db=Depends(get_db),
        selectedC: List[str] = Query(None), # the selected columns to return
        selectedAS: List[str] = Query(None) # the strains that were selected by the user
):
    """Get all genes"""
    genes_by_defense = get_genes_by_defense(db, selectedC, selectedAS)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    return prepare_file(genes_by_defense)
