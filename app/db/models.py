from sqlalchemy import Boolean, Column, Integer, String, Text, Numeric, VARCHAR

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

class Cluster(Base):
    __tablename__ = "cluster"

    index = Column("index", Integer, primary_key=True, index=True, nullable=False)
    function = Column("function", VARCHAR)
    PA14 = Column("PA14", VARCHAR)
    PAO1 = Column("PAO1", VARCHAR)
    i0 = Column("i0", Integer)
    i1 = Column("i1", Integer)
    i2 = Column("i2", Integer)
    i3 = Column("i3", Integer)
    i4 = Column("i4", Integer)
    i5 = Column("i5", Integer)
    i6 = Column("i6", Integer)
    i7 = Column("i7", Integer)
    i8 = Column("i8", Integer)
    i9 = Column("i9", Integer)
    i10 = Column("i10", Integer)
    i11 = Column("i11", Integer)
    i12 = Column("i12", Integer)
    i13 = Column("i13", Integer)
    i14 = Column("i14", Integer)
    i15 = Column("i15", Integer)
    i16 = Column("i16", Integer)
    i17 = Column("i17", Integer)
    i18 = Column("i18", Integer)
    i19 = Column("i19", Integer)
    i20 = Column("i20", Integer)
    i21 = Column("i21", Integer)
    i22 = Column("i22", Integer)
    i23 = Column("i23", Integer)
    i24 = Column("i24", Integer)
    i25 = Column("i25", Integer)
    i26 = Column("i26", Integer)
    i27 = Column("i27", Integer)
    i28 = Column("i28", Integer)
    i29 = Column("i29", Integer)
    i30 = Column("i30", Integer)
    i31 = Column("i31", Integer)
    i32 = Column("i32", Integer)
    i33 = Column("i33", Integer)
    i34 = Column("i34", Integer)
    i35 = Column("i35", Integer)
    i36 = Column("i36", Integer)
    i37 = Column("i37", Integer)
    i38 = Column("i38", Integer)
    i39 = Column("i39", Integer)
    i40 = Column("i40", Integer)
    i41 = Column("i41", Integer)
    i42 = Column("i42", Integer)
    i43 = Column("i43", Integer)
    i44 = Column("i44", Integer)
    i45 = Column("i45", Integer)
    i46 = Column("i46", Integer)
    i47 = Column("i47", Integer)
    i47 = Column("i47", Integer)
    i48 = Column("i48", Integer)
    i49 = Column("i49", Integer)
    i50 = Column("i50", Integer)
    i51 = Column("i51", Integer)


class Strains(Base):
    __tablename__ = "Strains"

    assembly = Column("assembly", Text, primary_key=True, index=True, nullable=False)
    strain = Column("strain", Text)
