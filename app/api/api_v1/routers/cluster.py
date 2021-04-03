import hashlib
import json
import os, subprocess

import pandas as pd
from fastapi import APIRouter, Query, Request, Depends, Response, HTTPException
from typing import List, Optional
from pathlib import Path

from sorting_techniques import pysort
from starlette.responses import FileResponse

from app.api.api_v1.routers.strains import get_offset, get_font_size, get_spacing, get_resolution
from app.db.session import get_db
from app.db.crud import (
    get_genes, get_strains_cluster, get_strain_id_name, get_strains_MLST, get_defense_system_names, get_gene_by_strain
)

from app.db.schemas import GeneBase

cluster_router = r = APIRouter()

sortObj = pysort.Sorting()


@r.get(
    "/cluster_tree",
    response_model_exclude_none=True,
    status_code=200,

)
async def cluster_tree(
        response: Response,
        list_strain_gene: List[str] = Query(None),
        subtree: Optional[List[int]] = Query([]),
        MLST: bool = False,
        db=Depends(get_db)
):
    """
    this function handles all requests to generate Phylogenetic tree from browse page in the website.
    the function gets 2 list: one for layers of strains and genes that are needed to be shows and another to
    subtrees the user might need. if the subtree list are empty: the system will show full tree.
    this function also generate Dynamic R script in order to generate the tree.
    """
    list_strains = get_strains_cluster(db, list_strain_gene)
    cluster_ids = ""
    for l in list_strains:
        cluster_ids += str(l[0]) + '_'  # cluster id is used for the hash id used for later
    str_list = ""
    if len(subtree) > 0:
        str_list = " ".join(str(x) for x in subtree)
    cluster_ids = cluster_ids + str_list
    cluster_ids = cluster_ids + str(MLST)
    filenameHash = hashlib.md5(cluster_ids.encode())
    filename = filenameHash.hexdigest()
    my_file = Path(r'static/cluster/' + filename + ".png")
    myPath = str(Path().resolve()).replace('\\', '/') + '/static/cluster'
    if not os.path.exists(my_file):
        command = 'C:/Program Files/R/R-4.0.3/bin/Rscript.exe'
        # todo replace with command = 'Rscript'  # OR WITH bin FOLDER IN PATH ENV VAR
        arg = '--vanilla'
        # data preprocessing for the R query
        all_strain_id = get_strains_MLST(db) if MLST is True else get_strain_id_name(db)
        for i in range(len(list_strains)):
            dict_id_strain = json.loads(list_strains[i][1].replace("'", "\""))
            data_id_strain = pd.DataFrame(dict_id_strain.items(), columns=['index', 'count' + str(i)])
            data_id_strain['index'] = data_id_strain['index'].astype(int)

            all_strain_id = pd.merge(all_strain_id, data_id_strain, how='left', on="index")
            all_strain_id = all_strain_id.fillna(0)

        subtreeSort = []
        if len(subtree) > 0:
            subtreeSort = sortObj.radixSort(subtree)
            all_strain_id = all_strain_id.loc[all_strain_id['index'].isin(subtree)]
        all_strain_id.to_csv(r'static/cluster/cluster.csv', index=False)
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
                     dat1 <- read.csv('""" + myPath + """/cluster.csv')
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

        layer = len(list_strains)
        if layer >= 1:
            query = query + """p <- p + new_scale_colour() +
                                  geom_fruit(
                                    data=dat1,
                                    geom=geom_bar,
                                    mapping=aes(y=index,x=count0, colour=c('red')),
                                    orientation="y",
                                    width=1,
                                    pwidth= 0.08,
                                    offset = """ + get_offset(len(subtreeSort)) + """,
                                    stat="identity",
                                    fill='red'
                                  ) + theme(

                                    legend.text = element_text(size = """ + get_font_size(len(subtreeSort)) + """),
                                    legend.title = element_blank(),
                                    legend.margin=margin(c(0,200,0,0)),
                                    legend.spacing = unit(""" + get_spacing(len(subtreeSort)) + ""","cm"),
                                    legend.spacing.x = unit(""" + get_spacing(len(subtreeSort)) + ""","cm")
                                  )+
                                    scale_colour_manual(values = c('red'), labels = c('""" + \
                    list_strain_gene[0].split('-')[1] + """'))
                                  """
        if layer >= 2:
            query = query + """p <- p + new_scale_colour() +
                                  geom_fruit(
                                    data=dat1,
                                    geom=geom_bar,
                                    mapping=aes(y=index,x=count1, colour=c("blue")),
                                    orientation="y",
                                    width=1,
                                    pwidth=0.08,
                                    offset = """ + get_offset(len(subtreeSort)) + """,
                                    stat="identity",
                                    fill="blue"
                                  ) + theme(

                                    legend.text = element_text(size = """ + get_font_size(len(subtreeSort)) + """),
                                    legend.title = element_blank(),
                                    legend.margin=margin(c(0,200,0,0)),
                                    legend.spacing = unit(""" + get_spacing(len(subtreeSort)) + ""","cm"),
                                    legend.spacing.x = unit(""" + get_spacing(len(subtreeSort)) + ""","cm")
                                  )+
                                    scale_colour_manual(values = c("blue"), labels = c('""" + \
                    list_strain_gene[1].split('-')[1] + """'))
                                  """
        if layer >= 3:
            query = query + """p <- p + new_scale_colour() +
                                  geom_fruit(
                                    data=dat1,
                                    geom=geom_bar,
                                    mapping=aes(y=index,x=count2, colour=c('green')),
                                    orientation="y",
                                    width=1,
                                    pwidth=0.05,
                                    offset = """ + get_offset(len(subtreeSort)) + """,
                                    stat="identity",
                                    fill='green'
                                  ) + theme(

                                    legend.text = element_text(size = """ + get_font_size(len(subtreeSort)) + """),
                                    legend.title = element_blank(),
                                    legend.margin=margin(c(0,200,0,0)),
                                    legend.spacing = unit(""" + get_spacing(len(subtreeSort)) + ""","cm"),
                                    legend.spacing.x = unit(""" + get_spacing(len(subtreeSort)) + ""","cm")
                                  )+
                                    scale_colour_manual(values = c('green'), labels = c('""" + \
                    list_strain_gene[2].split('-')[1] + """'))
                                  """
        resolution = get_resolution(len(subtreeSort))
        # resolution = 300
        query = query + """
            p <- p + geom_tiplab(show.legend=FALSE)
            png(""" + '"' + myPath + '/' + filename + """.png", units="cm", width=""" + str(
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
            raise HTTPException(status_code=404, detail="e")
    else:
        return FileResponse('static/cluster/' + filename + ".png")

    raise HTTPException(status_code=404, detail="e")


@r.get(
    "/get_gene_strain/{strain_name}",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_gene_strain(
        strain_name,
        response: Response,
        db=Depends(get_db)
):
    try:
        gene = get_genes(db)  # need to add strains name to the function
        list_genes = [d.get('locus_tag_copy') for d in gene]
        return list_genes
    except Exception as e:
        return Response(content="No Results", status_code=400)


'''
this function used to get all the genes of a certain assembly of a strain  
'''


@r.get(
    "/get_gene_strain_id/{strain_id}",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_gene_strain_id(
        strain_id,
        response: Response,
        db=Depends(get_db)
):
    try:
        gene = get_gene_by_strain(db, strain_id)
        # need to add strains name to the function
        if (len(gene) > 0):
            list_genes = []
            for row in gene:
                d = dict(row.items())
                list_genes.append(d['locus_tag'])
            df = pd.DataFrame(list_genes, columns=['name'])
            result = df.to_json(orient="records")
            parsed = json.loads(result)
            json.dumps(parsed, indent=4)
            return parsed
        else:
            status_code = 400
            return json.dumps({'name': "No Results"}, indent=4)
    except Exception as e:
        print(e)
        return Response(content="No Results", status_code=400)


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
    ds = get_defense_system_names()
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    if ds is None:
        return Response(content="No Results", status_code=400)
    return ds
