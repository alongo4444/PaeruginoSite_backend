from fastapi import APIRouter, Depends, Response, Query, HTTPException
import subprocess, os
import pandas as pd
from fastapi.responses import FileResponse
from app.db.session import get_db
from app.db.crud import (
    get_strain_isolation_mlst, get_strains_names, get_defense_systems_of_genes, get_strains_index, get_colors_dict
)
from app.api.api_v1.routers.cluster import (
    get_query_cluster, get_csv_cluster, preprocess_cluster
)
from app.api.api_v1.routers.isolation import (
    get_query_isolation, get_csv_isolation, preprocess_isolation
)
from app.api.api_v1.routers.defense_systems import (
    load_avg_systems_data, load_avg_systems_layer, preprocessing_avg_systems
)
from app.utilities.utilities import (
    validate_params, get_first_layer_offset, get_font_size, get_spacing, get_offset, get_resolution, load_colors,
    load_def_systems_names
)
import numpy as np
from pathlib import Path
from typing import List, Optional
from sorting_techniques import pysort
import hashlib
from pathlib import Path

strains_router = r = APIRouter()

# sorting object
sortObj = pysort.Sorting()
# load colors to dictionary
colors = load_colors()
def_sys = load_def_systems_names()


@r.get(
    "/",
)
async def strains_list(
        response: Response,
        db=Depends(get_db)
):
    """
    get all the names and assembly id of all strains
    :param response: the response
    :param db: the database connection
    :return: the strain's assembly list
    """
    strains = get_strains_names(db)
    return strains


@r.get(
    "/indexes",
)
async def strains_indexes(
        response: Response,
        db=Depends(get_db)
):
    """
    Get the index and name of all strains
    :param response: the response
    :param db: the database connection
    :return: the strain's indexes
    """
    strains = get_strains_index(db)
    return strains


@r.get(
    "/phyloTree",
)
async def phylogenetic_tree(
        systems: Optional[List[str]] = Query([]),
        subtree: Optional[List[int]] = Query([]),
        list_strain_gene: List[str] = Query([]),
        avg_defense_sys: bool = False,
        isolation_type: bool = False,
        MLST: bool = False,
        db=Depends(get_db)
):
    """
    this function handles all requests to generate Phylogenetic tree from browse page in the website.
    the function gets 2 arrays: one for  the defense systems and needs to be shows and another to
    subtrees the user might need. if they are empty: the system will show full tree with no defense systems
    on it. this function also generate Dynamic R script in order to generate the tree.
    systems - list of defence systems from front-end input
    subtree - list of strains from front-end input
    MLST - flag that indicates if MLST branch-coloring is needed (from front-end input)
    db - and object of the DB
    return:
        png file in case the phylogenetic tree successfully created and 400 response status otherwise.
    """
    # validate parameters using DB pre-defined strains and def-systems
    strains = get_strain_isolation_mlst(db)
    db_systems = load_def_systems_names()
    systems, subtree, bad_systems, bad_subtree = validate_params(systems, subtree, strains, db_systems)
    headers = {"bad_systems": ",".join(bad_systems),
               "bad_subtree": ",".join([str(x) for x in bad_subtree])}  # indicate to the user somethings is wrong
    # generating filename
    myPath = str(Path().resolve()).replace('\\', '/') + '/static/def_Sys'
    subtreeSort = []
    if len(systems) > 0:
        systems.sort()
    if len(subtree) > 0:
        subtreeSort = sortObj.radixSort(subtree)
    filenameStr = "".join(systems) + "".join(str(x) for x in subtreeSort) + "".join(list_strain_gene)
    filenameStr = filenameStr + str(MLST) + str(avg_defense_sys) + str(isolation_type)
    filenameHash = hashlib.md5(filenameStr.encode())
    filename = filenameHash.hexdigest()

    # check if such query allready computed and return it. else, compute new given query.
    if not os.path.exists('static/def_Sys/' + filename + ".png"):
        # prepare POPEN variables needed
        command = 'C:/Program Files/R/R-4.0.4/bin/Rscript.exe'
        # todo replace with command = 'Rscript'  # OR WITH bin FOLDER IN PATH ENV VAR
        arg = '--vanilla'

        # R query build-up
        query = """
                    library(ggtreeExtra)
                    library(ggplot2)
                    library(ggtree)
                    library(treeio)
                    library(ggnewscale)
                    library(ape)
                    library(dplyr)

                    trfile <- system.file("extdata","our_tree.tree", package="ggtreeExtra")
                    tree <- read.tree(trfile) """
        if len(subtree) > 0:
            query = query + """
                subtree =c(""" + ",".join('"' + str(x) + '"' for x in subtreeSort) + """)
                tree <- keep.tip(tree,subtree)
                """
        layer = 0
        # data preprocessing and random defense systems distribution
        strains, systems = defense_systems_preprocessing(strains, subtree, systems)

        # load systems csv
        query = query + load_systems_data(myPath)
        if MLST is True:
            query = query + """
            # For the clade group
                dat4 <- dat2 %>% select(c("index", "MLST"))
                dat4 <- aggregate(.~MLST, dat4, FUN=paste, collapse=",")
                clades <- lapply(dat4$index, function(x){unlist(strsplit(x,split=","))})
                names(clades) <- dat4$MLST
                
                tree <- groupOTU(tree, clades, "MLST_color")
                MLST <- NULL
                p <- ggtree(tree, layout="circular",branch.length = 'none', open.angle = 10, size = 0.5, aes(color=MLST_color), show.legend=FALSE)
            """
        else:
            query = query + """
                    p <- ggtree(tree, layout="circular",branch.length = 'none', open.angle = 10, size = 0.5)
                            """
        if len(list_strain_gene) > 0:
            list_strains = preprocess_cluster(db, list_strain_gene, subtreeSort, MLST)
            query = query + get_csv_cluster()
            query = query + get_query_cluster(list_strains, list_strain_gene, subtreeSort)
            layer = len(list_strains)  # define if defense systems are first layer or not
        if len(systems) > 0:
            query = query + load_systems_layers(systems, subtreeSort, layer)
            layer += len(systems)
        if isolation_type is True:
            preprocess_isolation(db, subtreeSort, MLST)
            query = query + get_csv_isolation()
            query = query + get_query_isolation(subtreeSort, layer)
            layer += 1
        if avg_defense_sys is True:
            preprocessing_avg_systems(strains, subtree)
            query = query + load_avg_systems_data()
            query = query + load_avg_systems_layer(subtreeSort, layer)
            layer += 1

        resolution = get_resolution(len(subtreeSort), layer)
        query = query + """
            dat2$index <- as.character(dat2$index)
            tree <- full_join(tree, dat2, by = c("label" = "index"))
            p <- p %<+% dat2  + geom_tiplab(show.legend=FALSE,aes(label=strain))
            png(""" + '"' + myPath + '/' + filename + """.png", units="cm", width=""" + str(
            resolution) + """, height=""" + str(resolution) + """, res=100)
            plot(p)
            dev.off(0)"""

        # for debugging purpose and error tracking
        print(query)
        f = open("static/def_Sys/" + filename + ".R", "w")
        f.write(query)
        f.close()

        # Execute R query
        try:
            p = subprocess.Popen([command, arg, os.path.abspath("static/def_Sys/" + filename + ".R")],
                                 cwd=os.path.normpath(os.getcwd() + os.sep + os.pardir), stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            output, error = p.communicate()
            return FileResponse('static/def_Sys/' + filename + ".png", headers=headers)

        except Exception as e:
            print("dbc2csv - Error converting file: phylo_tree.R")
            print(e)

            raise HTTPException(status_code=400, detail=e)
    else:
        return FileResponse('static/def_Sys/' + filename + ".png", headers=headers)


@r.get(
    "/strainCircos/{strain_name}",
    response_model_exclude_none=True,
    response_class=FileResponse,
    status_code=200,
)
async def strain_circos_graph(strain_name, response: Response):
    """
    The API call returns a circos strain html file to the frontend
    which display the distribution of defense systems on a specific strain
    :param strain_name: the name of the strain
    :param response: the response
    :return: html file of the circos strain
    """
    # the structure of the dir file will be stain_name.html and it will be stored in a specific directory.
    if strain_name:
        try:
            split = strain_name.split("(")
            assembly = split[1][:-1]
            print(assembly)
            strain_file = Path("static/Circos/" + assembly + ".html")
            print(strain_file)
            if strain_file.is_file():
                return FileResponse(strain_file, status_code=200)
            else:
                return FileResponse(Path("static/Circos/" + "GCF_000404265.1" + ".html"), status_code=200)
        # if the user inserts a wrong format
        except Exception:
            return Response(content="Wrong Parameters", status_code=400)
    # in the meantime if the file doesn't exist we return a default one
    else:
        # file is not in the directory (the strain name is wrong)
        return FileResponse(Path("static/Circos/" + "GCF_000404265.1" + ".html"), status_code=200)
        # return Response(content="No Results", status_code=400)


@r.get(
    "/strainGenesDefSystems/{strain_name}",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_genes_def_systems(strain_name, response: Response, db=Depends(get_db)):
    """
    the API call returns the genes of a strains (the ones that have defense systems)
    :param strain_name: the name of the strain
    :param response: the response
    :param db: the database connection
    :return: a table with the genes information
    """
    if strain_name:
        try:
            split = strain_name.split("(")
            assembly = split[1][:-1]
            df = get_defense_systems_of_genes(db, assembly)
            if df == 'No Results':
                # return Response(content="No Results", status_code=400)
                df = get_defense_systems_of_genes(db, "GCF_000404265.1")
        except Exception:
            df = get_defense_systems_of_genes(db, "GCF_000404265.1")
    return df


@r.get(
    "/defSystemsColors",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_defense_systems_colors(response: Response, db=Depends(get_db)):
    """
    the API call returns the color of each defense system
    :param response: the response
    :param db: the database connection
    :return: a dictionary of defense system and its colors
    """
    defense_colors = get_colors_dict(db)
    if defense_colors == "No Results":
        return Response(content="No Results", status_code=400)
    return defense_colors


def defense_systems_preprocessing(strains, subtree, systems):
    """
    preprocessing to generate random defense systems to each strain.
    this function saves the data to csv file for later use.
    strains - dataframe of strains which saved in the db.
    subtree - list of the user-chosen strains.
    systems - list of the user-chosen defense systems.
    return an updated list of the strains and the systems chosen by the user and validated by the db.
    """
    strains['Defense_sys'] = np.random.choice(def_sys, strains.shape[
        0])  # todo remove when defense systems are uploaded to db
    if len(subtree) > 0:
        strains = strains.loc[strains['index'].isin(subtree)]
        systems = strains.loc[strains['Defense_sys'].isin(systems)]['Defense_sys'].unique().tolist() if len(
            systems) > 0 else []
    strains = pd.get_dummies(strains, columns=["Defense_sys"])
    strains.to_csv("static/def_Sys/Defense_sys.csv")
    return strains, systems


def load_systems_data(myPath):
    """
    loads the relevant csv with the information of each strain and defense system.
    myPath - the path to the csv file
    """
    return """
             dat2 <- read.csv('""" + myPath + """/Defense_sys.csv')
            """


def load_systems_layers(systems, subtreeSort, layer):
    """
    this function get called if the user wants to show defense systems distribution in his phylogenetic tree.
    the function create a string that represent the defense systems distribution in R code for later tree generation
    systems - list of the desired defense systems by the user
    subtreeSort - the desired strains by the user.
    layer - the current generated layer in the API function. used to know if defense systems are the first layer of
            the phylogenetic tree or not.
    """
    query = ""
    for sys in systems:  # each system creates a layer of in the R code
        color = colors[sys]  # load the colors of each system
        if layer == 0:  # first layer
            query = query + """p <- p + new_scale_colour()+
                                  geom_fruit(
                                    data=dat2,
                                    geom=geom_bar,
                                    mapping=aes(y=index,x=Defense_sys_""" + sys + """, colour=c('""" + color + """')),
                                    orientation="y",
                                    width=1,
                                    pwidth=0.05,
                                    offset = """ + get_first_layer_offset(len(subtreeSort)) + """,
                                    stat="identity",
                                    fill='""" + color + """'
                                  ) + theme(

                                    legend.text = element_text(size = """ + get_font_size(len(subtreeSort)) + """),
                                    legend.title = element_blank(),
                                    legend.margin=margin(c(0,200,0,0)),
                                    legend.spacing = unit(""" + get_spacing(len(subtreeSort)) + ""","cm"),
                                    legend.spacing.x = unit(""" + get_spacing(len(subtreeSort)) + ""","cm")
                                  )+
                                    scale_colour_manual(values = c('""" + color + """'), labels = c('""" + sys + """'))
                                  """
        if (layer > 0):  # higher layer
            query = query + """p <- p + new_scale_colour()+
                                  geom_fruit(
                                    data=dat2,
                                    geom=geom_bar,
                                    mapping=aes(y=index,x=Defense_sys_""" + sys + """, colour=c('""" + color + """')),
                                    orientation="y",
                                    width=1,
                                    pwidth=0.05,
                                    offset = """ + get_offset(len(subtreeSort)) + """,
                                    stat="identity",
                                    fill='""" + color + """'
                                  ) + theme(
                                    legend.margin=margin(c(0,200,0,0)),
                                    legend.text = element_text(size = """ + get_font_size(len(subtreeSort)) + """),
                                    legend.title = element_blank(),
                                    legend.spacing = unit(""" + get_spacing(len(subtreeSort)) + ""","cm"),
                                    legend.spacing.x = unit(""" + get_spacing(len(subtreeSort)) + ""","cm")
                                  )+
                                    scale_colour_manual(values = c('""" + color + """'), labels = c('""" + sys + """'))
                                  """
        layer += 1

    return query
