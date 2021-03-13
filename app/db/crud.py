from fastapi import HTTPException, status
from sqlalchemy.orm import Session
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

def test(db: Session,q):
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
    print(q)

    stream = io.StringIO()

    df_from_records.to_csv(stream, index=False)

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
    strains_query = db.query(models.Genes).with_entities(models.Strains.Assembly,
                                                       models.Strains.Strain, )

    # Getting all the entries via SQLAlchemy
    all_strains= strains_query.all()

    # We provide also the (alternate) column names and set the index here,
    # renaming the column `id` to `currency__id`
    df_from_records = pd.DataFrame.from_records(all_strains
                                                , index='Assembly'
                                                , columns=['Assembly',
                                                           'Strain',
                                                           ])
    df_from_records = df_from_records.rename(columns={"Strain": "name"})
    print(df_from_records.head(5))
    df_from_records['key'] = df_from_records.index
    result = df_from_records.to_json(orient="records")
    parsed = json.loads(result)
    json.dumps(parsed, indent=4)
    return parsed
    #return df_from_records.to_csv()


def get_cluster(db: Session,strain_name):
    my_query = "SELECT * FROM cluster WHERE (PA14 LIKE '%{}%') OR (PAO1 LIKE '%{}%')".format(strain_name,strain_name)
    results = db.execute(my_query).fetchall()
    # data_cluster = pd.DataFrame(columns=['index','function','PA14','PAO1','Other','virulence','virulenecCount',
    #                                      'crisprTarget','maxlength','meanLength','std','members','numOfStrains',
    #                                      '0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15',
    #                                      '16','17','18','19','20','21','22','23','24','25','26','27','28,''29',
    #                                      '30','31','32','33','34','35','36','37','38','39','40','41','42','43',
    #                                      '44','45','46','47','48','49','50','51','L0','L1','L2','L3','L4','L5',
    #                                      'L6','L7','L8','L9','L10','L11','L12','L13','L14','L15','L16','L17',
    #                                      'L18','L19','L20','L21','L22','L23','L24','L25','L26','L27','L28',
    #                                      'L29','L30','L31','L32','L33','L34','L35','L36','L37','L38','L39',
    #                                      'L40','L41','L42','L43','L44','L45','L46','L47','L48','L49','L50','L51',
    #                                      'MW1','MW2','T-test1','T-test2','ROC','LR','Slope','log MW','log T-test',
    #                                      'log LR','mean VW','mean VWO','logMW','logLR','count logMW','count logLR',
    #                                      'P-val logMW','pval logLR','X5','X40','X51','X28','X2','X17','X48','X16',
    #                                      'X4','X43','X41','X45','X31','X12','X1','X13','X20','X37',
    #                                      'X8','X32','X29','X38','X9','X3','X6','X25','X30','X44','X14',
    #                                      'X36','X33','X23','X42','X49','X46','X19','X52','X11','X27','X21',
    #                                      'X24','X39','X10','X15','X47','X7','X50','X26', 'X34','X22','X35','X18',
    #                                      'Abi', 'BREX','DISARM','CRISPR','DISARMassociated','DND','RM','TA',
    #                                      'Wadjet', 'Zorya','Hachiman','Lamassu','Septu','Thoeris','Gabija','Druantia'])

    row = results[0]
    row = dict(zip(row.keys(), row))
    for i in range(52):
        row[str(i)] = row['i'+str(i)]
        del row['i'+str(i)]
    K =5
    print(results)
