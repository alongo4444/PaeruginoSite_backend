from fastapi import APIRouter, Request, Depends, Response, encoders, Query
import subprocess, os
import pandas as pd
from fastapi.responses import FileResponse,HTMLResponse
from app.db.session import get_db
from app.db.crud import (
    get_strains,get_strains_names
)
import numpy as np
from pathlib import Path
from typing import List, Optional
from sorting_techniques import pysort
import hashlib
import json



def random_color():
    rand = lambda: np.random.randint(100, 255)
    return '#%02X%02X%02X' % (rand(), rand(), rand())

from bs4 import BeautifulSoup
from bs4.element import Tag

from PIL import Image

def load_colors():
    # Opening JSON file colors.json
    colors_dict = dict()
    with open("static/def_Sys/colors.json") as f:
        li = json.load(f)
        colors = [x['color'] for x in li]
        names = [x['label'] for x in li]  # note that you use load(), not loads() to read from file
    for (x, col) in zip(names, colors):
        colors_dict[x.upper()] = col

    return colors_dict


sortObj = pysort.Sorting()
strains_router = r = APIRouter()
colors = load_colors()
def_sys = ['SHEDU', 'RM', 'PAGOS', 'SEPTU', 'THOERIS', 'WADJET', 'ZORYA', 'ABI', 'BREX', 'CRISPR', 'DISARM', 'DND',
           'DRUANTIA', 'GABIJA', 'HACHIMAN', 'KIWA', 'LAMASSU']


@r.get(
    "/",
    # response_model=t.List[StrainBase],
    # response_model_exclude_none=True,
)
async def strains_list(
        response: Response,
        db=Depends(get_db)
):
    """Get all strains"""
    strains = get_strains_names(db)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    return strains


@r.get(
    "/phyloTree",
    # response_model_exclude_none=True,
)
async def phylogenetic_tree(
        systems: Optional[List[str]] = Query([]),
        subtree: Optional[List[int]] = Query([]),
        db=Depends(get_db)
):
    """Get all strains"""
    # generating filename
    subtreeSort = []
    if len(systems) > 0:
        systems.sort()
    if len(subtree) > 0:
        subtreeSort = sortObj.radixSort(subtree)
    filenameStr = "".join(systems) + "".join(str(x) for x in subtreeSort)
    filenameHash = hashlib.md5(filenameStr.encode())
    filename = filenameHash.hexdigest()

    # check if such query allready computed and return it. else, compute new given query.
    if not os.path.exists('static/def_Sys/' + filename + ".png"):
        # prepare POPEN variables needed
        command = 'C:/Program Files/R/R-4.0.3/bin/Rscript.exe'
        # todo replace with command = 'Rscript'  # OR WITH bin FOLDER IN PATH ENV VAR
        arg = '--vanilla'

        # data preprocessing for the R query
        strains = get_strains(db)
        strains['Defense_sys'] = np.random.choice(def_sys, strains.shape[
            0])  # todo remove when defense systems are uploaded to db
        strains = strains[['index', 'strain', 'Defense_sys']]
        if len(subtree) > 0:
            strains = strains.loc[strains['index'].isin(subtree)]
            systems = strains.loc[strains['Defense_sys'].isin(systems)]['Defense_sys'].unique().tolist() if len(
                systems) > 0 else []
        strains = pd.get_dummies(strains, columns=["Defense_sys"])
        strains.to_csv("static/def_Sys/Defense_sys.csv")

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
        if len(subtree) > 0:
            query = query + """
                subtree =c(""" + ",".join('"' + str(x) + '"' for x in subtreeSort) + """)
                tree <- keep.tip(tree,subtree)
                """
        query = query + """
            p <- ggtree(tree, layout="circular",branch.length = 'none', open.angle = 10, size = 0.5) + geom_tiplab()
                    """
        layer = 0
        query = query + """
             dat1 <- read.csv("C:/Users/yinon/PycharmProjects/PaeruginoSite_backend/app/static/def_Sys/Defense_sys.csv")
                """
        for sys in systems:
            color = colors[sys]
            if (layer == 0):
                query = query + """p <- p + new_scale_fill() +
                                      geom_fruit(
                                        data=dat1,
                                        geom=geom_bar,
                                        mapping=aes(y=index,x=Defense_sys_""" + sys + """, colour=c('""" + color + """')),
                                        orientation="y",
                                        width=1,
                                        pwidth=0.05,
                                        stat="identity",
                                        fill='""" + color + """'
                                      ) + theme(
                                      
                                        legend.text = element_text(size = 100),
                                        legend.title = element_blank(),
                                        legend.margin=margin(c(0,200,0,0)),
                                        legend.spacing = unit(2,"cm"),
                                        legend.spacing.x = unit(2,"cm")
                                      )+
                                        scale_colour_manual(values = c('""" + color + """'), labels = c('""" + sys + """'))
                                      """
            if (layer > 0):
                query = query + """p <- p + new_scale_colour()+
                                      geom_fruit(
                                        data=dat1,
                                        geom=geom_bar,
                                        mapping=aes(y=index,x=Defense_sys_""" + sys + """, colour=c('""" + color + """')),
                                        orientation="y",
                                        width=1,
                                        pwidth=0.05,
                                        offset=0.01,
                                        stat="identity",
                                        fill='""" + color + """'
                                      ) + theme(
                                        legend.margin=margin(c(0,200,0,0)),
                                        legend.text = element_text(size = 100),
                                        legend.title = element_blank(),
                                        legend.spacing = unit(2,"cm"),
                                        legend.spacing.x = unit(2,"cm")
                                      )+
                                        scale_colour_manual(values = c('""" + color + """'), labels = c('""" + sys + """'))
                                      """
            layer += 1

        query = query + """
            png("C:/Users/yinon/PycharmProjects/PaeruginoSite_backend/app/static/def_Sys/""" + filename + """.png", units="cm", width=300, height=300, res=100)
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
            return FileResponse('static/def_Sys/' + filename + ".png")

        except Exception as e:
            print("dbc2csv - Error converting file: phylo_tree.R")
            print(e)

            return False
    else:
        return FileResponse('static/def_Sys/' + filename + ".png")

    return False

@r.get(
    "/strainCircos/{strain_name}",
    response_model_exclude_none=True,
    response_class=FileResponse,
    status_code=200,
)
async def strain_circos_graph(strain_name, response: Response):
    # the structure of the dir file will be stain_name.html and it will be stored in a specific directory.
    strain_file = Path("static/"+strain_name+".txt")
    if strain_file.is_file():
        '''
        f = open(strain_file, "r", encoding='utf-8')
        text = f.read()
        stopwords = ['<!DOCTYPE html>', '<html>', '</html>']
        for word in stopwords:
            if word in text:
                text = text.replace(word, "")
        '''
        return FileResponse(strain_file, status_code=200)
    else:
        # file is not in the directory (the strain name is wrong)
        return Response(status_code=400)
