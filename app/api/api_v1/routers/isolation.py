import hashlib
import os, subprocess
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Optional
from pathlib import Path
from sorting_techniques import pysort
from starlette.responses import FileResponse
from app.utilities.utilities import (
    validate_params, get_first_layer_offset, get_font_size, get_spacing, get_offset, get_resolution, load_colors,
    load_def_systems_names
)
from app.db.session import get_db
from app.db.crud import (
    get_strain_isolation_mlst, get_strain_isolation
)

from app.db.schemas import GeneBase

isolation_router = r = APIRouter()

sortObj = pysort.Sorting()

myPath = str(Path().resolve()).replace('\\', '/') + '/static/isolation'


# Returns the Isotypes names for the autocomplete at in the Frontend
@r.get(
    "/",
    # response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def isoTypes(
):
    """Get all genes"""
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    return [{'name': 'Clinical', 'key': 0}, {'name': 'Environmental/other', 'key': 1}]


# Returns the attributes names for the autocomplete at in the Frontend
@r.get(
    "/attributes",
    # response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def attributes(
):
    """Get all genes"""
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    return [{'name': 'size', 'key': 0}, {'name': 'gc', 'key': 1}, {'name': 'cds', 'key': 2}]


def get_query_isolation(subtreeSort, layer):
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
    return """
    dat4 <- read.csv('""" + myPath + """/isolation.csv') 
    """


def preprocess_isolation(db, subtree, MLST):
    # data preprocessing for the R query
    all_strain = get_strain_isolation_mlst(db) if MLST is True else get_strain_isolation(db)
    all_strain['index'] = all_strain.index
    if len(subtree) > 0:
        all_strain = all_strain.loc[all_strain['index'].isin(subtree)]
    all_strain['count'] = 1
    all_strain['isolation_type'] = all_strain['isolation_type'].fillna("unknown")
    all_strain = all_strain[['index', 'strain', 'isolation_type', 'count']]

    all_strain.to_csv(r'static/isolation/isolation.csv', index=False)


@r.get(
    "/isolation_tree",
    response_model_exclude_none=True,
)
async def isolation_tree(
        subtree: Optional[List[int]] = Query([]),
        MLST: bool = False,
        db=Depends(get_db),
):
    """
    this function handles all requests to generate Phylogenetic tree that contain the isolation type of
    each strain from browse page in the website.
    the function gets 1 array: the subtrees the user might need.
    if they are empty: the system will show full tree on it.
    this function also generate Dynamic R script in order to generate the tree.
    """

    subtreeSort, filename, command = preprocess_isolation(db, subtree, MLST)

    # str_list = 'all'
    # if len(subtree) > 0:
    #     str_list = str_list + " ".join(str(x) for x in subtree)
    # str_list = str_list + str(MLST)
    # filenameHash = hashlib.md5(str_list.encode())
    # filename = filenameHash.hexdigest()
    # my_file = Path(r'static/isolation/' + filename + ".png")
    # myPath = str(Path().resolve()).replace('\\', '/') + '/static/isolation'
    # #if not os.path.exists(my_file):
    # command = 'C:/Program Files/R/R-4.0.4/bin/Rscript.exe'
    # arg = '--vanilla'
    # # data preprocessing for the R query
    # all_strain = get_strain_isolation_mlst(db) if MLST is True else get_strain_isolation(db)
    # subtreeSort = []
    # all_strain['index'] = all_strain.index
    # if len(subtree) > 0:
    #     subtreeSort = sortObj.radixSort(subtree)
    #     all_strain = all_strain.loc[all_strain['index'].isin(subtree)]
    # all_strain['count'] = 1
    # all_strain['isolation_type'] = all_strain['isolation_type'].fillna("unknown")
    # all_strain = all_strain[['index', 'strain', 'isolation_type', 'count']]
    #
    # all_strain.to_csv(r'static/isolation/isolation.csv', index=False)
    # R query build-up

    query = """
                library(ggtreeExtra)
                ##library(ggstar)
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
    query = query + get_csv_isolation()
    if MLST is True:
        query = query + """
        # For the clade group
            dat4 <- dat1 %>% select(c("index", "MLST"))
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

    query = query + get_query_isolation(subtreeSort)

    resolution = get_resolution(len(subtreeSort))

    query = query + """
        dat1$index <- as.character(dat1$index)
        tree <- full_join(tree, dat1, by = c("label" = "index"))
        p <- p %<+% dat1  + geom_tiplab(show.legend=FALSE,aes(label=strain))
        png(""" + '"' + myPath + '/' + filename + """.png", units="cm", width=""" + str(
        resolution) + """, height=""" + str(resolution) + """, res=100)
        plot(p)
        dev.off(0)"""

    # for debugging purpose and error tracking
    print(query)
    f = open("static/isolation/" + filename + ".R", "w")
    f.write(query)
    f.close()

    # Execute R query
    try:
        p = subprocess.Popen([command, '--vanilla', os.path.abspath("static/isolation/" + filename + ".R")],
                             cwd=os.path.normpath(os.getcwd() + os.sep + os.pardir), stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output, error = p.communicate()
        return FileResponse('static/isolation/' + filename + ".png")

    except Exception as e:
        print("dbc2csv - Error converting file: phylo_tree.R")
        print(e)

        raise HTTPException(status_code=404, detail=e)
    # else:
    #     return FileResponse('static/isolation/' + filename + ".png")
    #
    # raise HTTPException(status_code=404, detail=e)
