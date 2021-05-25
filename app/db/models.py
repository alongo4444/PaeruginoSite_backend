from sqlalchemy import Boolean, Column, Integer, String, Text, Numeric
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
    __tablename__ = "Genes_Defense_Systems"
    strain = Column("assembly", Text, primary_key=True, index=True, nullable=False)
    locus_tag = Column("full_locus", Text, primary_key=True, nullable=False)
    defense_system = Column("defense_system", Text)
    anti_crispr = Column("anti_crispr", Text)


# class that is used for the 4.5 requirement
class StrainsDefenseSystems(Base):
    __tablename__ = "Strains_Defence_Systems"
    index = Column("index", Integer, primary_key=True, index=True, nullable=False)
    strain = Column("strain", Text)

    # main - 18
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
    ta = Column("ta_typeii", Integer)
    # disarmassociated = Column("disarmassociated", Integer)

    # types - 26
    rm_typei = Column("rm_typei", Integer)
    rm_typeii = Column("rm_typeii", Integer)
    rm_typeiii = Column("rm_typeiii", Integer)
    wadjet_typei = Column("wadjet_typei", Integer)
    wadjet_typeii = Column("wadjet_typeii", Integer)
    wadjet_typeiii = Column("wadjet_typeiii", Integer)
    zorya_typei = Column("zorya_typei", Integer)
    zorya_typeii = Column("zorya_typeii", Integer)
    abi_pifa = Column("abi_pifa", Integer)
    abi_abie = Column("abi_abie", Integer)
    abi_abij = Column("abi_abij", Integer)
    abi_abic = Column("abi_abic", Integer)
    abi_prrc = Column("abi_prrc", Integer)
    abi_abil = Column("abi_abil", Integer)
    abi_abiv = Column("abi_abiv", Integer)
    abi_abih = Column("abi_abih", Integer)
    brex_typeii = Column("brex_typeii", Integer)
    brex_typeiii = Column("brex_typeiii", Integer)
    brex_typeiv = Column("brex_typeiv", Integer)
    crispr_cas_typeic = Column("crispr_cas_typeic", Integer)
    crispr_cas_typeie = Column("crispr_cas_typeie", Integer)
    crispr_cas_typeif = Column("crispr_cas_typeif", Integer)
    disarm_typei = Column("disarm_typei", Integer)
    disarm_typeii = Column("disarm_typeii", Integer)
    druantia_typei = Column("druantia_typei", Integer)
    druantia_typeii = Column("druantia_typeii", Integer)
    druantia_typeiii = Column("druantia_typeiii", Integer)

    # ANTI CRISPR - 4
    anticrispr = Column("anticrispr", Integer)
    anticrispr_ic = Column("anticrispr_ic", Integer)
    anticrispr_ie = Column("anticrispr_ie", Integer)
    anticrispr_if = Column("anticrispr_if", Integer)


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