import io

from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from sqlalchemy.orm import Session ,class_mapper, defer
import pandas as pd
import typing as t
import json
import re

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

# prepares the "where" query, gets the selected options from the user and adds it to the field we what to filter by
#
# example: selectedAS = ['PAO1', 'PA14'] , ret = 'assembly_x' will return:
#   assembly_x='PAO1' OR assembly_x='PA14'
def selectedAS_to_query(selectedAS, ret):
    if not selectedAS:
        return "1=1" # if the user didn't select a strain, return all strains
    for idx,s in enumerate(selectedAS):
        if idx == 0:
            ret = ret + "='{}'".format(s)
        else:
            ret = ret + " OR {}='{}'".format(ret,s)
    return ret

def get_genes_download(db: Session, selectedC, selectedAS):

    cols = ','.join(selectedC)

    rows_q=selectedAS_to_query(selectedAS, 'assembly_x')

    my_query = "SELECT {} FROM pao1_data WHERE {}".format(cols,rows_q) # Need to change the FROM TABLE to the total genes table eventually
    results = db.execute(my_query).fetchall()
    df_from_records = pd.DataFrame(results, columns=selectedC)

    return df_from_records



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
    return df_from_records.to_dict('records')
    #query = "select * from Genes"
    # df = pd.read_sql(models.Genes, db.bind)
    # df = pd.DataFrame(db.query(models.Genes).all())
    # print(df.head(5))
    #return db.query(models.Genes).all()
    # return db.query(models.Genes).all()

def get_strains(db: Session):
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain, models.Strains.level,
                                                    models.Strains.gc, models.Strains.size,
                                                    models.Strains.scaffolds, models.Strains.assembly_accession_x,
                                                    models.Strains.assembly).all()
    df_from_records = pd.DataFrame.from_records(result, columns=['index', 'strain', 'level', 'gc', 'size', 'scaffolds',
                                                                 'assembly_accession_x', 'assembly'])
    return df_from_records

def get_strains_names(db: Session):
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

def get_strain_id_name(db: Session, df_cluster):
    result = db.query(models.Strains).with_entities(models.Strains.index,models.Strains.strain).all()
    df_from_records = pd.DataFrame.from_records(result, index='index', columns=['index','strain',])
    merge_df = pd.merge(df_from_records, df_cluster,how='left', on="index")
    merge_df = merge_df.fillna(0)
    return merge_df


def parse_circos_html(html_file):
    with open(html_file, encoding='utf8') as infile:
        html = BeautifulSoup(infile, "html.parser")

    res_dict = {}

    head_tag = html.head

    head_scripts = head_tag.find_all('script')

    lhs = []
    for hs in head_scripts:
        lhs.append(hs.string.strip('\n'))

    res_dict['head'] = lhs

    # body_tag = html.body
    #
    # body_tags = body_tag.find_all()
    #
    # btgs = []
    # for bgs in body_tags:
    #     btgs.append(bgs.stripped_strings)
    #
    # res_dict['body'] = btgs

    return res_dict

# returns all the names of the defense systems
def get_defense_system_names(db: Session):
    my_query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Cluster' ORDER BY ORDINAL_POSITION"
    results = db.execute(my_query).fetchall()
    results_ri = results[141:157] # edit if added more defense systems to the DB in the future
    result_str = []
    id = 0
    for r in results_ri:
        d = {}
        regex = re.compile('[^a-zA-Z]')
        # First parameter is the replacement, second parameter is your input string
        r = regex.sub('', str(r))
        # Out: 'abdE'
        d['name'] = r
        d['key'] = id
        id += 1
        result_str.append(d)

    return result_str


def get_genes_by_defense(db: Session, selectedC, selectedAS):

    # s_names_l = get_strains_names(db)
    s_names = []

    # for l in s_names_l:
    #     if isinstance(l['name'], str):
    #         s_names.append("\'{}\'".format(l['name']))

    s_names.append('PAO1')
    s_names.append('PA14')

    ds = ','.join(s_names)

    genes_ds = []
    for s in selectedAS:
        ret = s + "=1"

        my_query = "SELECT {} FROM \"Cluster\" WHERE {}".format(ds,ret)  # Need to change the FROM TABLE to the total genes table eventually
        results = db.execute(my_query).fetchall()

        for r in results:
            for t in r:
                if t == '-':
                    continue
                s_ds = t.split(';')
                for s_name in s_ds:
                    if s_name == '-':
                        continue
                    new_row = (s_name,s)
                    genes_ds.append(new_row)

    df_genes_ds = pd.DataFrame(genes_ds, columns=['locus_tag', 'ds_name']) # currently holds the genes and the defense system names (i.e: [PA2735, brex])

    selectedC_copy = selectedC.copy()

    for idx,s in enumerate(selectedC):
        selectedC[idx] = "\"" + s + "\""
    selectedC.insert(0,'\"locus_tag\"')
    selectedC_copy.insert(0, "locus_tag")
    cols = ', '.join(selectedC)
    my_query = "SELECT {} FROM \"Genes\"".format(cols)  # Get all genes
    results = db.execute(my_query).fetchall()
    df_genes_info = pd.DataFrame(results, columns=selectedC_copy)

    result = df_genes_ds.merge(df_genes_info)

    return result


# returns a csv file of a dataframe
def prepare_file(dafaframe):
    stream = io.StringIO()

    dafaframe.to_csv(stream, index=False)

    #Returns a csv prepared to be downloaded in the FrontEnd
    response = StreamingResponse(iter([stream.getvalue()]),
                                 media_type="text/csv"
                                 )

    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

    return response
