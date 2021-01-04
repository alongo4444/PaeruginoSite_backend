from pydantic import BaseModel
import typing as t
from decimal import *


class GeneBase(BaseModel):
    locus_tag: str
    # attributes_x: str
    # chromosome_y: str
    genomic_accession_y: str
    start_y: int
    end_y: int
    strand_y: str
    product_accession_y: str
    # non_redundant_refseq_y: str
    name_y: str
    symbol_y: str
    geneID_y: int
    product_length_y: Decimal
    dna_sequence: str
    protein_sequence: str


class StrainBase(BaseModel):
    Assembly: str
    Strain: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str = None
    permissions: str = "user"
