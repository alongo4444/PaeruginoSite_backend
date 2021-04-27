from fastapi import APIRouter, Request, Depends, Response, encoders, Query, HTTPException
from app.db.session import get_db
from app.db.crud import (
    get_defense_systems_names, get_strain_isolation_mlst
)
from typing import List, Optional
from pathlib import Path
from sorting_techniques import pysort
import hashlib
import subprocess, os
import pandas as pd
from fastapi.responses import FileResponse
from app.api.api_v1.routers.strains import (
    get_first_layer_offset, get_resolution
)

sortObj = pysort.Sorting()  # sorting object
defense_systems_router = r = APIRouter()


def get_systems_counts(strains):
    str_columns = ['index', 'strain', 'isolation_type', 'MLST']
    columns = [column for column in strains.columns if column not in str_columns]
    strains['count'] = strains.apply(lambda x: x[columns].tolist().count(1), axis=1)
    return strains


def validate_params(subtree, strains):
    subtree = [strain for strain in subtree if strain in strains['index']]
    return subtree


# returns all of the defense systems


@r.get(
    "/",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_defense_systems(response: Response, db=Depends(get_db)):
    df = get_defense_systems_names(db)
    return df


@r.get(
    "/distinct_count",
    response_model_exclude_none=True,
)
async def distinct_count(
        subtree: Optional[List[int]] = Query([]),
        MLST: bool = False,
        db=Depends(get_db),
):
    # validate parameters and R code injection
    strains = pd.read_csv("static/def_Sys/Defense_sys.csv")
    subtree = validate_params(subtree, strains)
    # generating filename
    myPath = str(Path().resolve()).replace('\\', '/') + '/static/distinct_sys'
    subtreeSort = []
    if len(subtree) > 0:
        subtreeSort = sortObj.radixSort(subtree)
    filenameStr = "".join(str(x) for x in subtreeSort)
    filenameStr = filenameStr + str(MLST)
    filenameHash = hashlib.md5(filenameStr.encode())
    filename = filenameHash.hexdigest()
    # check if such query allready computed and return it. else, compute new given query.
    if not os.path.exists('static/distinct_sys/' + filename + ".png"):
        # prepare POPEN variables needed
        command = 'C:/Program Files/R/R-4.0.4/bin/Rscript.exe'
        # todo replace with command = 'Rscript'  # OR WITH bin FOLDER IN PATH ENV VAR
        arg = '--vanilla'
        # data preprocessing for the R query
        strains = get_systems_counts(strains)
        strains.to_csv('static/distinct_sys/count.csv')

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
        query = query + """
                 dat1 <- read.csv('""" + myPath + """/count.csv')
                    """
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

        query = query + """p <- p +
                          geom_fruit(
                            data=dat1,
                            geom=geom_bar,
                            mapping=aes(y=index,x=count),
                            orientation="y",
                            width=1,
                            pwidth=0.05,
                            offset = """ + get_first_layer_offset(len(subtreeSort)) + """,
                            stat="identity",
                          )
                          """

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
        f = open("static/distinct_sys/" + filename + ".R", "w")
        f.write(query)
        f.close()

        # Execute R query
        try:
            p = subprocess.Popen([command, arg, os.path.abspath("static/distinct_sys/" + filename + ".R")],
                                 cwd=os.path.normpath(os.getcwd() + os.sep + os.pardir), stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            output, error = p.communicate()
            return FileResponse('static/distinct_sys/' + filename + ".png")

        except Exception as e:
            print("dbc2csv - Error converting file: phylo_tree.R")
            print(e)

            raise HTTPException(status_code=404, detail=e)
    else:
        return FileResponse('static/distinct_sys/' + filename + ".png")

    raise HTTPException(status_code=404, detail="e")
