from fastapi import APIRouter, Query, Request, Depends, Response, encoders
from typing import List, Optional
import pandas as pd

from app.db.session import get_db
from app.db.crud import (
    get_genes, get_genes_download, get_genes_by_defense, prepare_csv_file, prepare_zip, get_genes_by_cluster, prepare_fasta_file
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

    return prepare_csv_file(genes)

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
    return prepare_csv_file(genes_by_defense)

@r.get(
    "/genes_by_cluster",
    #response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def genes_by_cluster(
        response: Response,
        db=Depends(get_db),
        genes: List[str] = Query(None), # the index of the selected cluster
        csv: bool = Query(None),
        prot: bool = Query(None)
):
    """Get all genes"""
    genes_by_cluster = get_genes_by_cluster(db, genes)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    if csv:
        genes_by_cluster = genes_by_cluster.drop(columns=['protein_sequence', 'dna_sequence'])
        return prepare_csv_file(genes_by_cluster)
        # d = {'col1': [1, 2], 'col2': [3, 4]}
        # df = pd.DataFrame(data=d)
        # return prepare_zip([genes_by_cluster,df])
    else: # selected a fasta file
        return prepare_fasta_file(genes_by_cluster, prot)


