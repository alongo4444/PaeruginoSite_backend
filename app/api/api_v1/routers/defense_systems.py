from fastapi import APIRouter, Depends, Response
from app.db.session import get_db
from app.db.crud import (
    get_defense_systems_names, get_colors_dict
)
from pathlib import Path
from sorting_techniques import pysort
import pandas as pd
from app.utilities.utilities import (
    get_first_layer_offset, get_offset,
    load_def_systems_names, get_systems_counts
)
import itertools
import numpy as np

sortObj = pysort.Sorting()  # sorting object
defense_systems_router = r = APIRouter()
def_sys = load_def_systems_names()
myPath = str(Path().resolve()).replace('\\', '/') + '/static/distinct_sys'

@r.get(
    "/",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_defense_systems(response: Response, db=Depends(get_db)):
    """
    the API call returns all of the defense systems names
    :param response: the response
    :param db: the database connection
    :return: a dictionary of the defense systems names
    """
    df = get_defense_systems_names(db)
    return df


@r.get(
    "/triplets",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_triplets(db=Depends(get_db)):
    """
    this function retrive all possible triplets of all defense systems within an array of tuples
     - [(sys1,sys2,sys3),(sys1,sys2,sys4)....]
     :param db: instance of the systems db
     :return: triplets of defense systems
    """
    df = get_colors_dict(db)  # get defense systems.
    names = [x['label'] for x in df]  # fetch systems names
    triplets = list(itertools.combinations(np.random.choice(names, 6, replace=False), 3))  # split to triplets

    return triplets

def load_avg_systems_data():
    """
        loads the relevant csv with the information of each strain and defense system.
        :return: string of R query to load the csv from file
    """
    return """
             dat3 <- read.csv('""" + myPath + """/count.csv')
          """


def load_avg_systems_layer(subtreeSort,layer):
    """
    this function get called if the user wants to show avg defense systems number for each strain in his phylogenetic tree.
    the function creates a string that represent the avg defense system count in R code for later tree generation.
    :param subtreeSort: the desired strains by the user.
    :param layer: the current generated layer in the API function. used to know if defense systems are the first layer of
            the phylogenetic tree or not.
    :return: string of the R query built from the parameters
    """
    offset = get_first_layer_offset(len(subtreeSort)) if layer ==0 else get_offset(len(subtreeSort))
    return """p <- p +
                              geom_fruit(
                                data=dat3,
                                geom=geom_bar,
                                mapping=aes(y=index,x=count),
                                orientation="y",
                                width=1,
                                pwidth=0.05,
                                offset = """ + offset + """,
                                stat="identity",
                              )
                              """


def preprocessing_avg_systems(strains, subtree):
    """
    preprocessing to count avg defense system count of each strain.
    this function saves the data to csv file for later use.
    :param strains: dataframe of the information of the strains
    :param subtree: list of the user-chosen strains.
    :return: an updated dataframe of the strains and the systems chosen by the user and validated by the db.
    """
    strains['Defense_sys'] = np.random.choice(def_sys, strains.shape[
        0])  # todo remove when defense systems are uploaded to db
    if len(subtree) > 0:
        strains = strains.loc[strains['index'].isin(subtree)]
    strains = pd.get_dummies(strains, columns=["Defense_sys"])
    strains = get_systems_counts(strains)
    strains.to_csv('static/distinct_sys/count.csv')
    return strains
