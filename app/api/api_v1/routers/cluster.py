import hashlib
import json
import pandas as pd
from fastapi import APIRouter, Query, Request, Depends, Response, encoders
from typing import List, Optional
from pathlib import Path
from app.db.session import get_db
from app.db.crud import (
    get_genes, get_strains_cluster, get_strain_id_name,get_defense_system_names
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
    cluster_id = str(strains[0]) #cluster id is used for the hash id used for later
    filenameHash = hashlib.md5(cluster_id.encode())
    filename = filenameHash.hexdigest()
    my_file = Path(r'static/cluster/'+filename+'.txt')
    if my_file.is_file():
        return 1

    dict_id_strain = json.loads(strains[1].replace("'", "\""))
    data_id_strain = pd.DataFrame(dict_id_strain.items(), columns=['index', 'count'])
    data_id_strain['index'] = data_id_strain['index'].astype(int)
    complet_data = get_strain_id_name(db,data_id_strain)
    complet_data.to_csv(r'static/cluster/cluster.csv', index=False)
    return 0

@r.get(
    "/get_defense_system_names/",
    # response_model=t.List[StrainBase],
    # response_model_exclude_none=True,
)
async def strains_list(
        response: Response,
        db=Depends(get_db)
):
    """Get all strains"""
    ds = get_defense_system_names(db)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    return ds