import hashlib
import json
import os, subprocess

import pandas as pd
from fastapi import APIRouter, Query, Request, Depends, Response, encoders
from typing import List, Optional
from pathlib import Path

from sorting_techniques import pysort
from starlette.responses import FileResponse

from app.db.session import get_db
from app.db.crud import (
    get_genes, get_strains_cluster, get_strain_id_name, get_strains, get_defense_system_names
)

from app.db.schemas import GeneBase

cluster_router = r = APIRouter()

sortObj = pysort.Sorting()


def get_resolution(x):
    if (x == 0):
        return 300
    return 300  # 0.183 * x + 23.672


@r.get(
    "/cluster_tree/{gene_name}",
    # response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def cluster_tree(
        gene_name,
        strain_name,
        response_model_exclude_none=True,
        status_code=200,
        db=Depends(get_db)
):
    """Get all strains"""
    strains = get_strains_cluster(db,strain_name, gene_name)
    cluster_id = str(strains[0])  # cluster id is used for the hash id used for later
    filenameHash = hashlib.md5(cluster_id.encode())
    filename = filenameHash.hexdigest()
    my_file = Path(r'static/cluster/' + filename + ".png")
    if not os.path.exists(my_file):
        command = 'C:/Program Files/R/R-4.0.4/bin/Rscript.exe'
        # todo replace with command = 'Rscript'  # OR WITH bin FOLDER IN PATH ENV VAR
        arg = '--vanilla'
        # data preprocessing for the R query
        dict_id_strain = json.loads(strains[1].replace("'", "\""))
        data_id_strain = pd.DataFrame(dict_id_strain.items(), columns=['index', 'count'])
        data_id_strain['index'] = data_id_strain['index'].astype(int)
        complet_data = get_strain_id_name(db, data_id_strain)
        complet_data['count'] = complet_data['count']
        complet_data.to_csv(r'static/cluster/cluster.csv', index=False)
        subtreeSort = []
        # R query build-up
        query = """
                    library(ggtreeExtra)
                    ##library(ggstar)
                    library(ggplot2)
                    library(ggtree)
                    library(treeio)
                    library(ggnewscale)
                    library(ape)
                    trfile <- system.file("extdata","our_tree.tree", package="ggtreeExtra")
                    tree <- read.tree(trfile) """
        query = query + """
            p <- ggtree(tree, layout="circular",branch.length = 'none', open.angle = 10, size = 0.5) + geom_tiplab()
                    """
        layer = 0
        query = query + """
             dat1 <- read.csv("C:/Users/idoef/PycharmProjects/PaeruginoSite_backend/app/static/cluster/cluster.csv")
                """
        layer = 0
        if (layer == 0):
            query = query + """p <- p + new_scale_fill() +
                                  geom_fruit(
                                    data=dat1,
                                    geom=geom_bar,
                                    mapping=aes(y=index,x=count, colour=c('red')),
                                    orientation="y",
                                    width=1,
                                    pwidth=0.05,
                                    stat="identity",
                                    fill='red'
                                  ) + theme(

                                    legend.text = element_text(size = 100),
                                    legend.title = element_blank(),
                                    legend.margin=margin(c(0,200,0,0)),
                                    legend.spacing = unit(2,"cm"),
                                    legend.spacing.x = unit(2,"cm")
                                  )+
                                    scale_colour_manual(values = c('red'), labels = c('""" + gene_name + """'))
                                  """
        if (layer > 0):
            query = query + """p <- p + new_scale_colour()+
                                  geom_fruit(
                                    data=dat1,
                                    geom=geom_bar,
                                    mapping=aes(y=index,x=count, colour=c('""blue""')),
                                    orientation="y",
                                    width=1,
                                    pwidth=0.05,
                                    offset=0.01,
                                    stat="identity",
                                    fill='""blue ""'
                                  ) + theme(
                                    legend.margin=margin(c(0,200,0,0)),
                                    legend.text = element_text(size = 100),
                                    legend.title = element_blank(),
                                    legend.spacing = unit(2,"cm"),
                                    legend.spacing.x = unit(2,"cm")
                                  )+
                                    scale_colour_manual(values = c('""blue""'), labels = c('"" ""'))
                                  """
        layer += 1

        resolution = get_resolution(len(subtreeSort))
        query = query + """
            png("C:/Users/idoef/PycharmProjects/PaeruginoSite_backend/app/static/cluster/""" + filename + """.png", units="cm", width=""" + str(
            resolution) + """, height=""" + str(resolution) + """, res=100)
            plot(p)
            dev.off(0)"""

        # for debugging purpose and error tracking
        print(query)
        f = open("static/cluster/" + filename + ".R", "w")
        f.write(query)
        f.close()

        # Execute R query
        try:
            p = subprocess.Popen([command, arg, os.path.abspath("static/cluster/" + filename + ".R")],
                                 cwd=os.path.normpath(os.getcwd() + os.sep + os.pardir), stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            output, error = p.communicate()
            return FileResponse('static/cluster/' + filename + ".png")

        except Exception as e:
            print("dbc2csv - Error converting file: phylo_tree.R")
            print(e)

            return False
    else:
        return FileResponse('static/cluster/' + filename + ".png")

    return False


@r.get(
    "/get_gene_strain/{strain_name}",
    # response_model=t.List[GeneBase],
    response_model_exclude_none=True,
)
async def get_gene_strain(
        strain_name,
        response_model_exclude_none=True,
        status_code=200,
        db=Depends(get_db)
):
    gene = get_genes(db)  # need to add strains name to the function
    list_genes = [d.get('locus_tag_copy') for d in gene]
    return list_genes

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