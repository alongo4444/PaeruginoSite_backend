from fastapi import APIRouter, Request, Depends, Response, encoders, Query
import subprocess, os
import pandas as pd
from fastapi.responses import FileResponse
from app.db.session import get_db
from app.db.crud import (
    get_strains,
)
import numpy as np
from typing import List, Optional
from sorting_techniques import pysort
import hashlib

sortObj = pysort.Sorting()
strains_router = r = APIRouter()
def_sys = ['Sys1', 'Sys2', 'Sys3', 'Sys4', 'Sys5', 'Sys6']

@r.get(
    "/",
    # response_model=t.List[StrainBase],
    #response_model_exclude_none=True,
)
async def strains_list(
        response: Response,
        db=Depends(get_db)
):
    """Get all strains"""
    strains = get_strains(db)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    return strains


@r.get(
    "/phyloTree",
    #response_model_exclude_none=True,
)
async def phylogenetic_tree(
    systems: Optional[List[str]] = Query([]),
    subtree: Optional[List[int]] = Query([]),
    db=Depends(get_db)
):
    """Get all strains"""
    #generating filename
    subtreeSort =[]
    if len(systems)>0:
        systems.sort()
    if len(subtree)>0:
        subtreeSort = sortObj.radixSort(subtree)
    filenameStr = "".join(systems) + "".join(str(x) for x in subtreeSort)
    filenameHash = hashlib.md5(filenameStr.encode())
    filename = filenameHash.hexdigest()

    #check if such query allready computed and return it. else, compute new given query.
    if not os.path.exists('static/def_Sys/'+filename+".png"):
        #prepare POPEN variables needed
        command = 'C:/Program Files/R/R-4.0.3/bin/Rscript.exe'
        # todo replace with command = 'Rscript'  # OR WITH bin FOLDER IN PATH ENV VAR
        arg = '--vanilla'

        #data preprocessing for the R query
        strains = pd.read_excel('static/def_Sys/strains_info_table.xlsx')
        strains['Defense_sys'] = np.random.choice(['Sys1', 'Sys2', 'Sys3', 'Sys4', 'Sys5', 'Sys6'], strains.shape[0])  # todo remove when defense systems are uploaded to db
        strains = strains[['Index', 'Strain', 'Defense_sys']]
        if len(subtree)>0:
            strains = strains.loc[strains['Index'].isin(subtree)]
            systems = strains.loc[strains['Defense_sys'].isin(systems)]['Defense_sys'].unique().tolist() if len(systems)>0 else []
        strains = pd.get_dummies(strains,columns=["Defense_sys"])
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
        if len(subtree) >0:
            query = query + """
            subtree =c(""" +",".join('"'+str(x)+'"' for x in subtreeSort)+""")
            tree <- keep.tip(tree,subtree)
            """
        query = query+"""
        p <- ggtree(tree, layout="circular",branch.length = 'none', open.angle = 10, size = 0.5) + geom_tiplab()
                """
        layer = 0
        query = query +"""
         dat1 <- read.csv("C:/Users/yinon/PycharmProjects/PaeruginoSite_backend/app/static/def_Sys/Defense_sys.csv")
            """
        for sys in systems:
            if(layer==0):
                query = query + """p <- p + new_scale_fill() +
                                  geom_fruit(
                                    data=dat1,
                                    geom=geom_bar,
                                    mapping=aes(y=Index,x=Defense_sys_"""+sys+"""),
                                    orientation="y",
                                    width=1,
                                    pwidth=0.05,
                                    stat="identity",
                                    fill='"""+random_color()+"""'
                                  ) + theme(
                                    legend.text = element_text(size = 100),
                                    legend.title = element_text(size=100)
                                  )
                                  """
            if(layer>0):
                query = query + """p <- p + new_scale_fill() +
                                  geom_fruit(
                                    data=dat1,
                                    geom=geom_bar,
                                    mapping=aes(y=Index,x=Defense_sys_""" + sys + """),
                                    orientation="y",
                                    width=1,
                                    pwidth=0.05,
                                    offset=0.01,
                                    stat="identity",
                                    fill='""" + random_color() + """'
                                  ) + theme(
                                    legend.text = element_text(size = 100),
                                    legend.title = element_text(size=100)
                                  )
                                  """
            layer +=1

        query= query+"""
        p <- p + scale_fill_identity(name = 'Defense Systems', guide = 'legend',labels = c('Sys1')) +

        png("C:/Users/yinon/PycharmProjects/PaeruginoSite_backend/app/static/def_Sys/"""+filename+""".png", units="cm", width=300, height=300, res=100)
        plot(p)
        dev.off(0)"""

        # for debugging purpose and error tracking
        print(query)
        f = open("static/def_Sys/"+filename+".R", "w")
        f.write(query)
        f.close()

        # Execute R query
        try:
            p = subprocess.Popen([command, arg, os.path.abspath("static/def_Sys/"+filename+".R")],
                                 cwd=os.path.normpath(os.getcwd() + os.sep + os.pardir), stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            output, error = p.communicate()
            return FileResponse('static/def_Sys/'+filename+".png")

        except Exception as e:
            print("dbc2csv - Error converting file: phylo_tree.R")
            print(e)

            return False
    else:
        return FileResponse('static/def_Sys/'+filename+".png")

    return False


def random_color():
    rand = lambda: np.random.randint(100, 255)
    return '#%02X%02X%02X' % (rand(), rand(), rand())