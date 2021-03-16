from fastapi import APIRouter, Query, Request, Depends, Response, encoders
from typing import List, Optional
from app.db.session import get_db
from app.db.crud import (
    get_genes, test, get_strains_cluster
)
from app.db.schemas import GeneBase

cluster_router = r = APIRouter()

@r.get(
    "/cluster_tree/{gene_name}",
    #response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def cluster_tree(
        gene_name,
        response_model_exclude_none=True,
        status_code=200,
        db=Depends(get_db)
):
    """Get all strains"""
    strains = get_strains_cluster(db,gene_name)

    return strains
