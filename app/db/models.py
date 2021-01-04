from sqlalchemy import Boolean, Column, Integer, String, Text, Numeric

from .session import Base


class Genes(Base):
    __tablename__ = "Genes"

    locus_tag = Column("locus_tag", Text, primary_key=True, index=True, nullable=False)
    attributes_x = Column("attributes_x", Text)
    chromosome_y = Column("chromosome_y", Text)
    genomic_accession_y = Column("genomic_accession_y", Text)
    start_y = Column("start_y", Integer)
    end_y = Column("end_y", Integer)
    strand_y = Column("strand_y", String)
    product_accession_y = Column("product_accession_y", Text)
    # non-redundant_refseq_y = Column("non-redundant_refseq_y", Text)
    name_y = Column("name_y", Text)
    symbol_y = Column("symbol_y", Text)
    geneID_y = Column("geneID_y", Integer)
    product_length_y = Column("product_length_y", Numeric)
    dna_sequence = Column("dna_sequence", Text)
    protein_sequence = Column("protein_sequence", Text)


class Strains(Base):
    __tablename__ = "Strains"

    Assembly = Column("Assembly", Text, primary_key=True, index=True, nullable=False)
    Strain = Column("Strain", Text)
