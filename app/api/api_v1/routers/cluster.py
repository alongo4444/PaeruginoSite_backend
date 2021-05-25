import json
from pathlib import Path

import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, Response
from sorting_techniques import pysort

from app.utilities.utilities import (
    get_first_layer_offset,get_font_size,get_spacing,get_offset
)
from app.db.crud import (
    get_strains_cluster, get_strain_id_name, get_strains_MLST, get_gene_by_strain
)
from app.db.session import get_db
import itertools

cluster_router = r = APIRouter()

sortObj = pysort.Sorting()

myPath = str(Path().resolve()).replace('\\', '/') + '/static/cluster'


def get_query_cluster(list_strains, list_strain_gene, subtreeSort):
    """
    this function get called if the user wants to show any cluster distribution in his phylogenetic tree.
    the function create a string that represent the cluster distribution in R code for later tree generation.
    :param list_strains: list of the strains of the cluster chosen by the user.
    :param list_strain_gene: list of the genes chosen by the user.
    :param subtreeSort: the desired strains by the user.
    :return: string of the R query built from the parameters.
    """
    query = ""
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
                                        offset = """ + get_first_layer_offset(len(subtreeSort)) + """,
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
    return query


def get_csv_cluster():
    """
        loads the relevant csv with the information of each strain and defense system.
        :return: string of R query to load the csv from file
    """
    return """
    dat1 <- read.csv('""" + myPath + """/cluster.csv')
    """


def preprocess_cluster(db, list_strain_gene, subtree, MLST):
    """
    preprocessing to generate random cluster distribution to each strain.
    this function saves the data to csv file for later use.
    :param db: an instance of the systems db
    :param list_strain_gene: list of the genes chosen by the user.
    :param subtree: list of the user-chosen strains.
    :param MLST: boolean variable that indicates if the user wants to show MLST or not.
    :return: an updated list of the strains and the systems chosen by the user and validated by the db.
    """
    list_strains = get_strains_cluster(db, list_strain_gene)

    # data preprocessing for the R query
    all_strain_id = get_strains_MLST(db) if MLST is True else get_strain_id_name(db)
    for i in range(len(list_strains)):
        dict_id_strain = json.loads(list_strains[i][1].replace("'", "\""))
        data_id_strain = pd.DataFrame(dict_id_strain.items(), columns=['index', 'count' + str(i)])
        data_id_strain['index'] = data_id_strain['index'].astype(int)

        all_strain_id = pd.merge(all_strain_id, data_id_strain, how='left', on="index")
        all_strain_id = all_strain_id.fillna(0)

    if len(subtree) > 0:
        all_strain_id = all_strain_id.loc[all_strain_id['index'].isin(subtree)]
    all_strain_id.to_csv(r'static/cluster/cluster.csv', index=False)
    return list_strains

@r.get(
    "/get_gene_strain_id/{strain_id}",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_gene_strain_id(
        strain_id,
        db=Depends(get_db)
):
    """
       this function used to get all the genes of a certain assembly of a strain
       :param strain_id: the strain we are looking for his genes
       :param response: the response
       :param db: the database connection
   """
    try:
        gene = get_gene_by_strain(db, strain_id)
        # need to add strains name to the function
        if (len(gene) > 0):
            list_genes = []
            for row in gene:
                # d = dict(row.items())
                list_genes.append(row)
            df = pd.DataFrame(list_genes, columns=['name'])
            result = df.to_json(orient="records")
            parsed = json.loads(result)
            json.dumps(parsed, indent=4)
            return parsed
        else:
            return Response(content="No Results", status_code=400)
    except Exception as e:
        print(e)
        return Response(content="No Results", status_code=400)



@r.get(
    "/get_tuple_genes/{strain_id}",
    response_model_exclude_none=True,
    status_code=200,
)
async def get_tuple_genes(
        strain_id,
        combinations: int = 2,
        db=Depends(get_db)
):
    """
        this function retrieve all possible combination of genes of specific strain.
         in case of combinations =3 --> [(gene1,gene2,gene3),(gene1,gene2,gene4)....]
         :param strain_id: the strain of the desired gene
         :param combinations: size of the combinations (doubles =2 , triplets =3, quadruples= 4).
         :param db: instance of the systems db
         :return: triplets of defense systems
    """
    try:
        if combinations < 6:
            genes = np.array(get_gene_by_strain(db, strain_id)).ravel()
            genes = np.random.choice(genes, 5)
            tuples = list(itertools.combinations(genes, combinations))  # split to triplets
            return tuples
        else:
            return Response(content="Number of combinations is too high!", status_code=400)
    except Exception as e:
        print(e)
        return Response(content="No Results", status_code=400)
