from sqlalchemy import Boolean, Column, Integer, String, Text, Numeric, VARCHAR, FLOAT

from .session import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

class Genes(Base):
    __tablename__ = "Genes"

    locus_tag = Column("locus_tag", Text, primary_key=True, index=True, nullable=False)
    assembly_x =  Column("assembly_x", Text)
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
    index = Column("index", Text, primary_key=True, index=True, nullable=False)
    assembly = Column("assembly", Text)
    strain = Column("strain", Text)
    assembly_accession_x = Column("assembly_accession_x", Text)
    level = Column("level", Text)
    size = Column("sizemb", Numeric)
    gc = Column("gc", Numeric)
    scaffolds = Column("scaffolds", Integer)


# class that is used for the 4.4 requirement
class GenesDefenseSystems(Base):
    __tablename__ = "Genes_Defence_Systems"
    strain = Column("strain", Text, primary_key=True, index=True, nullable=False)
    locus_tag = Column("full_locus", Text, primary_key=True, index=True, nullable=False)
    defense_system = Column("defense_system", Text)
    anti_crispr = Column("anti_crispr", Text)

