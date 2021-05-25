
from fastapi import APIRouter
from pathlib import Path
from sorting_techniques import pysort
from app.utilities.utilities import (
     get_first_layer_offset, get_font_size, get_spacing, get_offset
)
from app.db.crud import (
    get_strain_isolation_mlst, get_strain_isolation
)

isolation_router = r = APIRouter()

sortObj = pysort.Sorting()

myPath = str(Path().resolve()).replace('\\', '/') + '/static/isolation'


@r.get(
    "/",
    response_model_exclude_none=True,
)
async def isoTypes(
):
    """
    the API call returns the Isolation Types names for the autocomplete at in the Frontend
    :return: dictionary that contains isolation types
    """
    # This is necessary for react-admin to work
    return [{'name': 'Clinical', 'key': 0}, {'name': 'Environmental/other', 'key': 1}]



@r.get(
    "/attributes",
    # response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def attributes(
):
    """
    the API call returns the attributes names for the autocomplete at in the Frontend
    :return: dictionary that contains attributes
    """
    # This is necessary for react-admin to work
    return [{'name': 'size', 'key': 0},{'name': 'gc', 'key':1}, {'name': 'cds', 'key':2}]


def get_query_isolation(subtreeSort, layer):
    """
    this function get called if the user wants to show isolation type distribution in his phylogenetic tree.
    the function create a string that represent the isolation types distribution in R code for later tree generation
    :param subtreeSort: the desired strains by the user.
    :param layer: the current generated layer in the API function. used to know if defense systems are the first layer of
            the phylogenetic tree or not.
    :return: string of the R query built from the parameters
    """
    offset = get_first_layer_offset(len(subtreeSort)) if layer ==0 else get_offset(len(subtreeSort))
    return """p <- p + new_scale_colour() +
                                  geom_fruit(
                                    data=dat4,
                                    geom=geom_bar,
                                    mapping=aes(y=index, x=count, fill=isolation_type),
                                    orientation="y",
                                    width=1,
                                    pwidth= 0.08,
                                    offset = """ + offset + """,
                                    stat="identity",
                                  ) + theme(

                                    legend.text = element_text(size = """ + get_font_size(len(subtreeSort)) + """),
                                    legend.title = element_blank(),
                                    legend.margin=margin(c(0,200,0,0)),
                                    legend.spacing = unit(""" + get_spacing(len(subtreeSort)) + ""","cm"),
                                    legend.spacing.x = unit(""" + get_spacing(len(subtreeSort)) + ""","cm")
                                  )
                                      """


def get_csv_isolation():
    """
        loads the relevant csv with the information of each strain and defense system.
        :return: string of R query to load the csv from file
    """
    return """
    dat4 <- read.csv('""" + myPath + """/isolation.csv') 
    """


def preprocess_isolation(db, subtree, MLST):
    """
    preprocessing to retrieve isolation type to each strain.
    this function saves the data to csv file for later use.
    :param db: an instance of the systems db
    :param subtree: list of the user-chosen strains.
    :param MLST: boolean variable that indicates if the user wants to show MLST or not.
    """
    # data preprocessing for the R query
    all_strain = get_strain_isolation_mlst(db) if MLST is True else get_strain_isolation(db)
    all_strain['index'] = all_strain.index
    if len(subtree) > 0:
        all_strain = all_strain.loc[all_strain['index'].isin(subtree)]
    all_strain['count'] = 1
    all_strain['isolation_type'] = all_strain['isolation_type'].fillna("unknown")
    all_strain = all_strain[['index', 'strain', 'isolation_type', 'count']]

    all_strain.to_csv(r'static/isolation/isolation.csv', index=False)