from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import pandas as pd
import typing as t

from . import models, schemas
from app.core.security import get_password_hash


def get_table_names(db: Session):
    my_query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"
    results = db.execute(my_query).fetchall()
    print(results)



def get_genes(db: Session):
    # Defining the SQLAlchemy-query
    genes_query = db.query(models.Genes).with_entities(models.Genes.locus_tag,
                                                       models.Genes.genomic_accession_y,
                                                       models.Genes.start_y,
                                                       models.Genes.end_y,
                                                       models.Genes.strand_y,
                                                       models.Genes.product_accession_y,
                                                       models.Genes.name_y,
                                                       models.Genes.symbol_y,
                                                       models.Genes.geneID_y,
                                                       models.Genes.product_length_y,
                                                       models.Genes.dna_sequence,
                                                       models.Genes.protein_sequence, )

    # Getting all the entries via SQLAlchemy
    all_genes = genes_query.all()

    # We provide also the (alternate) column names and set the index here,
    # renaming the column `id` to `currency__id`
    df_from_records = pd.DataFrame.from_records(all_genes
                                                , index='locus_tag'
                                                , columns=['locus_tag',
                                                           'genomic_accession_y',
                                                           'start_y',
                                                           'end_y',
                                                           'strand_y',
                                                           'product_accession_y',
                                                           'name_y',
                                                           'symbol_y',
                                                           'geneID_y',
                                                           'product_length_y',
                                                           'dna_sequence',
                                                           'protein_sequence'
                                                           ])
    print(df_from_records.head(5))
    return df_from_records.to_csv()
    #query = "select * from Genes"
    # df = pd.read_sql(models.Genes, db.bind)
    # df = pd.DataFrame(db.query(models.Genes).all())
    # print(df.head(5))
    #return db.query(models.Genes).all()
    # return db.query(models.Genes).all()
