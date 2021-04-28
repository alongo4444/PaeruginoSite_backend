from fastapi import APIRouter, Depends, Response, Query
from app.db.session import get_db
import pandas as pd
from app.db.crud import (
    get_defense_systems_names,
    get_defense_systems_of_two_strains, get_all_strains_of_defense_system, get_strain_column_data,
    dict_of_clusters_related_to_gene,
)
import ast
from typing import List
from scipy.stats import hypergeom
from scipy.stats import mannwhitneyu


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
    checks_dups = set(systems)
    if len(checks_dups) < 2:
        return Response(content="Same Defense System", status_code=400)
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
async def get_correlation_between_defense_systems_and_attribute(response: Response,
                                                  system: str, category: str,
                                                  db=Depends(get_db)):
    correct_params = ['size', 'gc', 'cds']
    if category not in correct_params:
        return Response(content="Wrong category name", status_code=400)
    names_of_def_systems = get_defense_systems_names(db, True)
    if system not in names_of_def_systems:
        return Response(content="Defense system doesn't exist", status_code=400)
    attributes = get_strain_column_data(db, category)
    defense_system = get_all_strains_of_defense_system(db, system)
    if defense_system is 'No Results' or attributes is "No Results":
        return Response(content="No Results", status_code=400)
    combined = pd.merge(attributes, defense_system, on="index")
    try:
        combined[category.lower()] = combined[category.lower()].astype(float)
    except Exception as e:
        print(e)
    with_def = combined.loc[combined[system.lower()] == 1]
    without_def = combined.loc[combined[system.lower()] == 0]
    with_def_attr = list(with_def[category.lower()])
    without_def_attr = list(without_def[category.lower()])
    N = len(list(combined['index']))
    stat, p = mannwhitneyu(with_def_attr, without_def_attr)
    exp_number = "{:e}".format(p)
    values_to_df = {"statistic": [stat], "pvalue": [exp_number], "N": [N],
              "K": [len(with_def_attr)], "n": [len(without_def_attr)],
              "k":[0]}
    df = pd.DataFrame.from_dict(values_to_df)
    df = df.to_dict('records')
    values = []
    box_plot_with = prepare_data_for_box_plot(with_def, category.lower())
    box_plot_without = prepare_data_for_box_plot(without_def, category.lower())
    values.append(df)
    values.append(box_plot_with)
    values.append(box_plot_without)

    return values


def prepare_data_for_box_plot(df, category):
    """
    the function takes a df and returns an array that contains all 5 values for the box-plot
    :param df: the df we are checking
    :param category: the column name we are extracting it's data
    :return: the array of the relevant values
    """
    Q1 = df[category].describe().loc['25%']
    Q2 = df[category].describe().loc['50%']
    Q3 = df[category].describe().loc['75%']
    min = df[category].describe().loc['min']
    max = df[category].describe().loc['max']
    all_params = [min, Q1, Q3, max, Q2]
    # [min, Q1, Q3, max, Q2]
    return all_params


@r.get(
    "/correlationBetweenDefenseSystemAndIsolationType",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_correlation_between_defense_systems_and_iso_type(response: Response,
                                                  system: str, isoType: str,
                                                  db=Depends(get_db)):
    correct_params = ['Environmental/other', 'Clinical']
    if isoType not in correct_params:
        return Response(content="Wrong isotype", status_code=400)
    names_of_def_systems = get_defense_systems_names(db, True)
    if system not in names_of_def_systems:
        return Response(content="Defense system doesn't exist", status_code=400)
    attributes = get_strain_column_data(db, 'isolation_type')
    defense_system = get_all_strains_of_defense_system(db, system)
    if defense_system is 'No Results' or attributes is "No Results":
        return Response(content="No Results", status_code=400)
    combined = pd.merge(attributes, defense_system, on="index").fillna("")
    # calculate the distribution
    N = len(list(combined['index']))
    K_l = combined.index[combined[system.lower()] == 1].tolist()
    n_l = combined.index[combined['isolation_type'] == isoType.lower()].tolist()
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
    "/correlationBetweenDefenseSystemAndCluster",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_correlation_between_defense_systems_and_cluster(response: Response,
                                                  system: str, strain: str, gene: str,
                                                  db=Depends(get_db)):
    names_of_def_systems = get_defense_systems_names(db, True)
    if system not in names_of_def_systems:
        return Response(content="Defense system doesn't exist", status_code=400)
    valid_strain = ['pao1', 'pa14']
    if strain.lower() not in valid_strain:
        return Response(content="Strain doesn't exist", status_code=400)
    clusters = dict_of_clusters_related_to_gene(db, strain, gene)
    defense_system = get_all_strains_of_defense_system(db, system)
    if clusters is 'No Results' or defense_system is "No Results":
        return Response(content="No Results", status_code=400)
    df = dict_of_clusters_related_to_gene(db, strain, gene)
    try:
        strains_in_cluster = ast.literal_eval(df['combined_index'].values[0])
    except Exception:
        return Response(content="Error in Value", status_code=400)
    strains_in_clusters = [int(k) for k in strains_in_cluster.keys()]
    # calculate the distribution
    N = len(list(defense_system['index']))
    K_l = defense_system.index[defense_system[system.lower()] == 1].tolist()
    k_l = list(set(K_l) & set(strains_in_clusters))
    K = len(K_l)
    n = len(strains_in_clusters)
    k = len(k_l)
    pval = hypergeom.sf(k - 1, N, K, n)
    exp_number = "{:e}".format(pval)
    values = {"N": [N], "K": [K], "n": [n], "k": [k], "pvalue": [exp_number]}
    df = pd.DataFrame.from_dict(values)
    df = df.to_dict('records')
    return df


@r.get(
    "/correlationBetweenClusterAndIsolationType",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_correlation_between_cluster_and_isotype(response: Response,
                                                  isoType: str, strain: str, gene: str,
                                                  db=Depends(get_db)):
    correct_params = ['Environmental/other', 'Clinical']
    if isoType not in correct_params:
        return Response(content="Wrong isotype", status_code=400)
    valid_strain = ['pao1', 'pa14']
    if strain.lower() not in valid_strain:
        return Response(content="Strain doesn't exist", status_code=400)
    clusters = dict_of_clusters_related_to_gene(db, strain, gene)
    attributes = get_strain_column_data(db, 'isolation_type')
    if clusters is 'No Results' or attributes is "No Results":
        return Response(content="No Results", status_code=400)
    try:
        strains_in_cluster = ast.literal_eval(clusters['combined_index'].values[0])
    except Exception:
        return Response(content="Error in Value", status_code=400)
    # calculate the distribution
    N = len(list(attributes['index']))
    K_l = attributes.index[attributes['isolation_type'] == isoType.lower()].tolist()
    k_l = list(set(K_l) & set(strains_in_cluster))
    K = len(K_l)
    n = len(strains_in_cluster)
    k = len(k_l)
    pval = hypergeom.sf(k - 1, N, K, n)
    exp_number = "{:e}".format(pval)
    values = {"N": [N], "K": [K], "n": [n], "k": [k], "pvalue": [exp_number]}
    df = pd.DataFrame.from_dict(values)
    df = df.to_dict('records')
    return df
