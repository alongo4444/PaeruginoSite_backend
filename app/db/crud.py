from fastapi import HTTPException, status
from sqlalchemy.orm import Session,class_mapper, defer
import pandas as pd
import typing as t
import json
import io

from starlette.responses import StreamingResponse


from . import models, schemas
from app.core.security import get_password_hash



def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_email(db: Session, email: str) -> schemas.UserBase:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(
    db: Session, skip: int = 0, limit: int = 100
) -> t.List[schemas.UserOut]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return user


def edit_user(
    db: Session, user_id: int, user: schemas.UserEdit
) -> schemas.User:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = user.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(user.password)
        del update_data["password"]

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_table_names(db: Session):
    my_query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"
    results = db.execute(my_query).fetchall()
    print(results)

def defer_everything_but(entity, cols):
    m = class_mapper(entity)
    return [defer(k) for k in
            set(p.key for p
                in m.iterate_properties
                if hasattr(p, 'columns')).difference(cols)]

    # s = Session()
    # print s.query(A).options(*defer_everything_but(A, ["q", "p"]))

# prepares the "where" query for the get_genes_download function, to select only the genes from the desired strains
def selectedAS_to_query(selectedAS):
    ret = 'assembly_x='
    for idx,s in enumerate(selectedAS):
        if idx == 0:
            ret = ret + "'{}'".format(s)
        else:
            ret = ret + " OR assembly_x='{}'".format(s)
    return ret

def get_genes_download(db: Session, selectedC, selectedAS):

    cols = ','.join(selectedC)

    rows_q=selectedAS_to_query(selectedAS)

    my_query = "SELECT {} FROM pao1_data WHERE {}".format(cols,rows_q) # Need to change the FROM TABLE to the total genes table eventually
    results = db.execute(my_query).fetchall()
    df_from_records = pd.DataFrame(results, columns=selectedC)

    stream = io.StringIO()

    df_from_records.to_csv(stream, index=False)

    #Returns a csv prepared to be downloaded in the FrontEnd
    response = StreamingResponse(iter([stream.getvalue()]),
                                 media_type="text/csv"
                                 )

    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

    return response


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
    df_from_records['locus_tag_copy'] = df_from_records.index
    # return FileResponse("../road-sign-361513_960_720.jpg")
    print(df_from_records.head(5))

    return df_from_records.to_dict('records')
    #query = "select * from Genes"
    # df = pd.read_sql(models.Genes, db.bind)
    # df = pd.DataFrame(db.query(models.Genes).all())
    # print(df.head(5))
    #return db.query(models.Genes).all()
    # return db.query(models.Genes).all()


def get_strains(db: Session):
    # Defining the SQLAlchemy-query
    strains_query = db.query(models.Genes).with_entities(models.Strains.assembly_accession_x,
                                                       models.Strains.strain, )

    # Getting all the entries via SQLAlchemy
    all_strains= strains_query.all()

    # We provide also the (alternate) column names and set the index here,
    # renaming the column `id` to `currency__id`
    df_from_records = pd.DataFrame.from_records(all_strains
                                                , index='assembly_accession_x'
                                                , columns=['assembly_accession_x',
                                                           'strain',
                                                           ])
    df_from_records = df_from_records.rename(columns={"strain": "name"})
    print(df_from_records.head(5))
    df_from_records['key'] = df_from_records.index
    result = df_from_records.to_json(orient="records")
    parsed = json.loads(result)
    json.dumps(parsed, indent=4)
    return parsed
    #return df_from_records.to_csv()


def get_strains_cluster(db: Session,gene_name):
    my_query = "SELECT index,combined_index FROM \"Cluster\" WHERE (PA14 LIKE '%{}%') OR (PAO1 LIKE '%{}%')".format(gene_name,gene_name)
    results = db.execute(my_query).fetchall()

    result = results[0]

    return result
