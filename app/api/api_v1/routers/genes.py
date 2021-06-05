from fastapi import APIRouter, Query, Request, Depends, Response, encoders
from typing import List
import io
from starlette.responses import StreamingResponse

from app.db.session import get_db
from app.db.crud import (
    get_genes, get_genes_download, get_genes_by_defense, prepare_csv_file, get_genes_by_cluster
)
genes_router = r = APIRouter()


@r.get(
    "/",
    response_model_exclude_none=True,
)
async def genes_list(
        response: Response,
        db=Depends(get_db)
):
    """
    the API call returns all of the genes in the database
    """
    genes = get_genes(db)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    return genes


@r.get(
    "/download_genes",
    response_model_exclude_none=True,
)
async def download_genes(
        response: Response,
        db=Depends(get_db),
        selectedC: List[str] = Query(None),
        selectedAS: List[str] = Query(None)
):
    """
    Get genes of the selected strains
    :param response: the response
    :param db: the database connections
    :param selectedC: the selected columns to return
    :param selectedAS: the strains that were selected by the user
    :return: csv of the genes information
    """
    genes = get_genes_download(db, selectedC, selectedAS)

    if genes.empty:
        return Response(content="One or more of the parameters is invalid", status_code=400)

    return prepare_csv_file(genes)


@r.get(
    "/genes_by_defense",
    response_model_exclude_none=True,
)
async def genes_by_defense(
        response: Response,
        db=Depends(get_db),
        selectedC: List[str] = Query(None), # the selected columns to return
        selectedAS: List[str] = Query(None) # the strains that were selected by the user
):
    """
    gets the genes by choosing the defense systems
    :param response: the response
    :param db: the database connection
    :param selectedC: the selected columns to return
    :param selectedAS: the defense systems that were selected by the user
    :return: csv that contains the genes information
    """
    genes_by_defense = get_genes_by_defense(db, selectedC, selectedAS)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    if genes_by_defense.empty:
        return Response(content="One or more of the parameters is invalid", status_code=400)

    return prepare_csv_file(genes_by_defense)


@r.get(
    "/genes_by_cluster",
    response_model_exclude_none=True,
)
async def genes_by_cluster(
        response: Response,
        db=Depends(get_db),
        genes: List[str] = Query(None), # the index of the selected cluster
        csv: bool = Query(None),  # flag for csv file or fasta file
        prot: bool = Query(None) # if fasta file, flag if protein or dna
):
    """
    the function returns the genes by choosing their cluster
    :param response: the response
    :param db: the database connection
    :param genes: the index of the selected clusters
    :param csv: flag for csv file of fasta file
    :param prot: if fasta file, flag if protein or DNA
    :return: csv that contains the genes information
    """
    genes_by_cluster = get_genes_by_cluster(db, genes)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    if genes_by_cluster.empty:
        return Response(content="One or more of the parameters is invalid", status_code=400)

    if csv:
        genes_by_cluster = genes_by_cluster.drop(columns=['protein_sequence', 'dna_sequence'])
        return prepare_csv_file(genes_by_cluster)
    # selected a fasta file
    else:
        return prepare_fasta_file(genes_by_cluster, prot)



def prepare_fasta_file(df, prot):
    """
    prepares a fasta file.
    :param df: the dataframe we converting
    :param prot: what format of the fasta file
    :return: as a text file to the user. the front end needs to translate it into a .faa file.
    """
    final_txt = ""
    for index, row in df.iterrows():
        locus_tag, start_g, end_g, name, g_accession, cluster_index,product_accession  = row['locus_tag'], row['start'], row['end'], row['name'], row['genomic_accession'], row['cluster_index'], row['product_accession']
        seq = row['protein_sequence'] if prot else row['dna_sequence']
        every = 120
        seq = '\n'.join(seq[i:i+every] for i in range(0, len(seq), every))
        type = 'prot' if prot else 'dna'
        newentry = ">{}_{} [locus_tag = {}] [location = {}..{}] [name = {}] [cluster_index = {}] [product_accession = {}] \n{}\n".format(g_accession,type,locus_tag,start_g,end_g,name,cluster_index,product_accession,seq)
        final_txt += newentry

    output = io.StringIO()
    output.write(final_txt)

    # Returns a csv prepared to be downloaded in the FrontEnd
    response = StreamingResponse(iter([output.getvalue()]),
                                 media_type="text/plain"
                                 )

    response.headers["Content-Disposition"] = "attachment; filename=export.txt"

    return response

