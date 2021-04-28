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
    # SELECT index, assembly, genomic_accession, start_g, end_g, strand, symbol, locus_tag,
    # attributes_x, product_accession, nonredundant_refseq, name, protein_sequence, dna_sequence
    #
    locus_tag = Column("locus_tag", Text, primary_key=True, index=True, nullable=False)
    assembly = Column("assembly", Text)
    attributes_x = Column("attributes_x", Text)
    genomic_accession = Column("genomic_accession", Text)
    start = Column("start_g", Integer)
    end = Column("end_g", Integer)
    strand = Column("strand", String)
    product_accession = Column("product_accession", Text)
    name = Column("name", Text)
    symbol = Column("symbol", Text)
    dna_sequence = Column("dna_sequence", Text)
    protein_sequence = Column("protein_sequence", Text)
    nonredundant_refseq = Column("nonredundant_refseq", Text)


class Strains(Base):
    __tablename__ = "Strains"
    index = Column("index", Text, primary_key=True, index=True, nullable=False)
    assembly_genbank = Column("assembly_genbank", Text)  # assembly
    strain = Column("strain", Text)
    assembly_refseq = Column("assembly_refseq", Text)
    level = Column("level", Text)
    size = Column("sizemb", Numeric)
    gc = Column("gc", Numeric)
    scaffolds = Column("scaffolds", Integer)
    mlst_sequence_type = Column("mlst_sequence_type", Text)
    isolation_type = Column("isolation_type", Text)
    cds = Column("cds", Integer)


# class that is used for the 4.4 requirement
class GenesDefenseSystems(Base):
    __tablename__ = "Genes_Defence_Systems"
    strain = Column("strain", Text, primary_key=True, index=True, nullable=False)
    locus_tag = Column("full_locus", Text, primary_key=True, index=True, nullable=False)
    defense_system = Column("defense_system", Text)
    anti_crispr = Column("anti_crispr", Text)


# class that is used for the 4.5 requirement
class StrainsDefenseSystems(Base):
    __tablename__ = "Strains_Defence_Systems"
    index = Column("index", Integer, primary_key=True, index=True, nullable=False)
    strain = Column("strain", Text)
    abi = Column("abi", Integer)
    brex = Column("brex", Integer)
    crispr = Column("crispr", Integer)
    disarm = Column("disarm", Integer)
    dnd = Column("dnd", Integer)
    druantia = Column("druantia", Integer)
    gabija = Column("gabija", Integer)
    hachiman = Column("hachiman", Integer)
    kiwa = Column("kiwa", Integer)
    lamassu = Column("lamassu", Integer)
    pagos = Column("pagos", Integer)
    rm = Column("rm", Integer)
    septu = Column("septu", Integer)
    shedu = Column("shedu", Integer)
    thoeris = Column("thoeris", Integer)
    wadjet = Column("wadjet", Integer)
    zorya = Column("zorya", Integer)
    ta = Column("ta", Integer)
    disarmassociated = Column("disarmassociated", Integer)



# class that is used for the 4.5 requirement
class DefenseSystems(Base):
    __tablename__ = "DefenseSystems"
    name = Column("defense_system", Text, primary_key=True, index=True, nullable=False)
    color = Column("color", Text, nullable=False)
    label = Column("label", Text, nullable=False)


class Clusters(Base):
    __tablename__ = "Cluster"
    index = Column("index", Integer, primary_key=True, index=True, nullable=False)
    pa14 = Column("pa14", Text)
    pao1 = Column("pao1", Text)
    combined_index = Column("combined_index", Text)