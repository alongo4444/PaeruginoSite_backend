from fastapi import APIRouter, Depends, Response, Query
from app.db.session import get_db
import pandas as pd
from app.db.crud import (
    get_defense_systems_names,
    get_defense_systems_of_two_strains, get_strain_column_data, get_defense_systems_of_one_strain
)
from typing import List, Optional
from scipy.stats import hypergeom

statistics_router = r = APIRouter()


@r.get(
    "/correlationBetweenDefenseSystems",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_correlation_between_defense_systems(response: Response,
                                                  systems: List[str] = Query([]),
                                                  db=Depends(get_db)):
    names_of_def_systems = get_defense_systems_names(db, True)
    if len(systems) != 2:
        return Response(content="Wrong number of parameters", status_code=400)
    for item in systems:
        if item not in names_of_def_systems:
            return Response(content="Defense system doesn't exist", status_code=400)
    df = get_defense_systems_of_two_strains(db, systems[0], systems[1])
    # calculate the distribution
    N = len(list(df['index']))
    K_l = df.index[df[systems[0].lower()] == 1].tolist()
    n_l = df.index[df[systems[1].lower()] == 1].tolist()
    k_l = list(set(K_l) & set(n_l))
    K = len(K_l)
    n = len(n_l)
    k = len(k_l)
    pval = hypergeom.sf(k - 1, N, K, n)
    exp_number = "{:e}".format(pval)
    values = {"N": [N], "K": [K], "n": [n], "k": [k], "pvalue": [exp_number]}
    df = pd.DataFrame.from_dict(values)
    df = df.to_dict('records')
    return df

@r.get(
    "/correlationBetweenDefenseSystemAndAttribute",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_correlation_between_defense_systems(response: Response,
                                                  system: str, category: str,
                                                  db=Depends(get_db)):
    attributes = get_strain_column_data(db, system, category)
    defense_system = get_defense_systems_of_one_strain(db, system)
    combined = pd.merge(attributes, defense_system, on="index")
    print(combined)
    return combined