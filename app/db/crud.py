import io
import zipfile
import csv
from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, class_mapper, defer
import pandas as pd
import typing as t
import json
import io
import re
from sqlalchemy.sql import select

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

'''
def get_table_names(db: Session):
    my_query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"
    results = db.execute(my_query).fetchall()
    print(results)
'''

'''
def selectedAS_to_query(selectedAS, ss):
    """
    prepares the "where" query, gets the selected options from the user and adds it to the field we what to filter by
    example: selectedAS = ['PAO1', 'PA14'] , ret = 'assembly_x' will return:
    assembly_x='PAO1' OR assembly_x='PA14'
    :param selectedAS: the chosen strains from the frontend
    :param ss:
    """
    if not selectedAS:
        return "1=1"  # if the user didn't select a strain, return all strains
    for idx, s in enumerate(selectedAS):
        if idx == 0:
            ret = ss + "='{}'".format(s)
        else:
            ret = ret + " OR {}='{}'".format(ss, s)
    return ret
'''

def get_genes_download(db: Session, selectedC, selectedAS):
    selectedC.insert(0, 'locus_tag')
    cols_attr = [getattr(models.Genes, col) for col in selectedC]
    results = db.query(models.Genes).filter(models.Genes.assembly.in_(selectedAS)).with_entities(*cols_attr).all()
    df_from_records = pd.DataFrame(results, columns=selectedC)

    return df_from_records


def get_genes(db: Session):
    # Defining the SQLAlchemy-query
    genes_query = db.query(models.Genes).with_entities(models.Genes.locus_tag,
                                                       models.Genes.assembly,
                                                       models.Genes.attributes_x,
                                                       models.Genes.genomic_accession,
                                                       models.Genes.start,
                                                       models.Genes.end,
                                                       models.Genes.strand,
                                                       models.Genes.product_accession,
                                                       models.Genes.name,
                                                       models.Genes.symbol,
                                                       models.Genes.dna_sequence,
                                                       models.Genes.protein_sequence)

    # Getting all the entries via SQLAlchemy
    all_genes = genes_query.all()

    # We provide also the (alternate) column names and set the index here,
    # renaming the column `id` to `currency__id`
    df_from_records = pd.DataFrame.from_records(all_genes
                                                , index='locus_tag'
                                                , columns=['locus_tag',
                                                           'assembly',
                                                           'attributes_x',
                                                           'genomic_accession',
                                                           'start',
                                                           'end',
                                                           'strand',
                                                           'product_accession',
                                                           'name',
                                                           'symbol',
                                                           'dna_sequence',
                                                           'protein_sequence'
                                                           ])
    df_from_records['locus_tag'] = df_from_records.index
    return df_from_records.to_dict('records')

def get_strains_index(db: Session):
    """
    this function returns from DB a JSON with 2 keys: index of strains and name of strain.
    """
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain).all()
    df_from_records = pd.DataFrame.from_records(result, columns=['index', 'strain'])
    df_from_records = df_from_records.rename(columns={"strain": "name"})
    result = df_from_records.to_json(orient="records")
    parsed = json.loads(result)
    json.dumps(parsed, indent=4)
    return parsed


def get_strains(db: Session):
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain, models.Strains.level,
                                                    models.Strains.gc, models.Strains.size,
                                                    models.Strains.scaffolds, models.Strains.assembly_refseq,
                                                    models.Strains.assembly_genbank).all()
    df_from_records = pd.DataFrame.from_records(result, columns=['index', 'strain', 'level', 'gc', 'size', 'scaffolds',
                                                                 'assembly_refseq', 'assembly'])
    return df_from_records


def get_strains_names(db: Session):
    # Defining the SQLAlchemy-query
    strains_query = db.query(models.Genes).with_entities(models.Strains.assembly_refseq,
                                                         models.Strains.strain, )

    # Getting all the entries via SQLAlchemy
    all_strains = strains_query.all()

    # We provide also the (alternate) column names and set the index here,
    # renaming the column `id` to `currency__id`
    df_from_records = pd.DataFrame.from_records(all_strains
                                                , index='assembly_refseq'
                                                , columns=['assembly_refseq',
                                                           'strain'
                                                           ])
    df_from_records = df_from_records.rename(columns={"strain": "name"})
    print(df_from_records.head(5))
    df_from_records['key'] = df_from_records.index
    result = df_from_records.to_json(orient="records")
    parsed = json.loads(result)
    json.dumps(parsed, indent=4)
    return parsed
    # return df_from_records.to_csv()


'''
this function get all the strains of a certain gene in a cluster
'''


def get_strains_cluster(db: Session, strains_genes):
    list_strains = []
    for s_g in strains_genes:
        split = s_g.split('-')
        search = "%{}%".format(split[1])
        results = db.query(models.Clusters).\
            with_entities(models.Clusters.index, models.Clusters.combined_index).\
            filter(getattr(models.Clusters, split[0].lower()).like(search)).all()
        # my_query = "SELECT index,combined_index FROM \"Cluster\" WHERE {} LIKE '%{}%'".format(split[0], split[1])
        # results = db.execute(my_query).fetchall()
        if (len(results) > 0):
            list_strains.append(results[0])
    return list_strains


'''
this get the strain id and the strain name and isolation type
'''


def get_strain_isolation(db: Session):
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain,
                                                    models.Strains.isolation_type).all()
    df_from_records = pd.DataFrame.from_records(result, index='index', columns=['index', 'strain', 'isolation_type'])
    return df_from_records



'''
this get the strain id and the strain name and isolation type and mlst
'''


def get_strain_isolation_mlst(db: Session):
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain,
                                                    models.Strains.isolation_type,models.Strains.mlst_sequence_type).all()
    df_from_records = pd.DataFrame.from_records(result, columns=['index', 'strain', 'isolation_type', 'MLST'])
    return df_from_records



'''
this get the strain id and the strain name 
'''


def get_strain_id_name(db: Session):
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain).all()
    df_from_records = pd.DataFrame.from_records(result, index='index', columns=['index', 'strain'])
    return df_from_records


'''
this function used to get all the genes of a certain assembly of a strain  
'''


def get_gene_by_strain(db: Session, strain_id):
    results = db.query(models.Genes.locus_tag).filter(models.Genes.assembly == strain_id).all()
    # my_query = "SELECT locus_tag FROM \"Genes\" WHERE assembly = '{}'".format(strain_id)
    # results = db.execute(my_query).fetchall()
    return results


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

# prepares the "where" query, gets the selected options from the user and adds it to the field we what to filter by
#
# example: selectedAS = ['PAO1', 'PA14'] , ret = 'assembly_x' will return:
#   assembly_x='PAO1' OR assembly_x='PA14'
'''
def selectedAS_to_query_contains_str(selectedAS):
    ss = "defense_system LIKE "
    if not selectedAS:
        return "1=1"  # if the user didn't select a defense system, return all genes
    for idx, s in enumerate(selectedAS):
        if idx == 0:
            ret = ss + "'%{}%'".format(s)
        else:
            ret = ret + " OR " + ss + "'%{}%'".format(s)
    return ret
'''

# returns a dataframe with the genes information of the system defenses in selectedAS with the columns in selectedC.
def get_genes_by_defense(db: Session, selectedC, selectedAS):
    # if the user didn't select any defense system, return all:
    if not selectedAS:
        ds_names = get_defense_systems_names(db)
        selectedAS = [x['name'] for x in ds_names]

    # make a list of tuples to be imported to a dataframe later
    genes_ds = []
    for s in selectedAS:
        search = "%{}%".format(s)
        results = db.query(models.GenesDefenseSystems).\
            with_entities(models.GenesDefenseSystems.locus_tag).\
            filter(models.GenesDefenseSystems.defense_system.like(search)).all()
        # my_query = "SELECT full_locus FROM \"Genes_Defence_Systems\" WHERE defense_system LIKE '%{}%'".format(s)
        # results = db.execute(my_query).fetchall()

        for r in results:
            for t in r:
                s_name = t.split('|')[0]
                new_row = (s_name, s)
                genes_ds.append(new_row)

    df_genes_ds = pd.DataFrame(genes_ds, columns=['locus_tag',
                                                  'ds_name'])  # import list of tuples to a dataframe. currently holds the genes and the defense system names (i.e: [PA2735, brex])

    selectedC_copy = selectedC.copy()

    # for idx, s in enumerate(selectedC_copy):
    #     selectedC_copy[idx] = "\"" + s + "\""
    selectedC.insert(0, 'locus_tag')
    selectedC_copy.insert(0, "locus_tag")
    cols = ', '.join(selectedC_copy)
    cols_attr = [getattr(models.Genes, item) for item in selectedC_copy]
    results = db.query(models.Genes).with_entities(*cols_attr).all()
    # my_query = "SELECT {} FROM \"Genes\"".format(cols)  # Get all genes
    # results = db.execute(my_query).fetchall()
    df_genes_info = pd.DataFrame(results, columns=selectedC)
    result = df_genes_ds.merge(df_genes_info)

    return result


# returns a csv file of a dataframe to the frontend
def prepare_csv_file(dafaframe):
    stream = io.StringIO()

    dafaframe.to_csv(stream, index=False)

    # Returns a csv prepared to be downloaded in the FrontEnd
    response = StreamingResponse(iter([stream.getvalue()]),
                                 media_type="text/csv"
                                 )

    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

    return response


def get_defense_systems_of_genes(db: Session, strain_name):
    """
    the function returns all the information about defense system of a specific strain
    :param db: the connection to the database
    :param strain_name: the strain we want to present its defense systems
    :return: dataframe that contains the relevant information
    """
    query = db.query(models.GenesDefenseSystems) \
        .with_entities(models.GenesDefenseSystems.locus_tag,
                       models.GenesDefenseSystems.defense_system, models.GenesDefenseSystems.anti_crispr). \
        filter(models.GenesDefenseSystems.strain == strain_name).all()
    df = pd.DataFrame.from_records(query, columns=['locus_tag', 'defense_system', 'anti_crispr'])
    print(df)
    if df.empty:
        return "No Results"
    else:
        df = df.to_dict('records')
    return df


def value_loc(value, df):
    for col in list(df):
        if df[col].values.find(value) != -1:
            return (list(df).index(col), df[col][df[col].find(value) != -1].index[0])


def get_genes_by_cluster(db: Session, genes):
    results = db.query(models.Clusters).with_entities(models.Clusters.index,
                                                      models.Clusters.pa14,
                                                      models.Clusters.pao1,
                                                      models.Clusters.combined_index
                                                      ).all()
    # my_query = "SELECT * FROM \"Cluster\""
    # results = db.execute(my_query)
    col_names = ['index','pa14','pao1','combined_index']
    df_from_records = pd.DataFrame.from_records(results, columns=col_names)
    first_column = df_from_records.columns[0]
    last_column = df_from_records.columns[-1]
    # filter only the strains columns
    df_from_records_copy = df_from_records.drop([first_column], axis=1)
    df_from_records_copy = df_from_records_copy.drop([last_column], axis=1)

    genes_cluster = []
    frames = []
    # search the cluster index to get the other genes in the same cluster
    for g in genes:
        if g == '':
            continue
        cluster_index = -1
        for c in df_from_records_copy.columns:
            b = df_from_records_copy[c].str.contains(r'{}'.format(g))
            a = b[b == True]
            if not a.empty:
                cluster_index = df_from_records['index'][a.index[0]]  # found the cluster index number
                strain = c
                break
        if cluster_index == -1:
            continue
        dfb = df_from_records[df_from_records['index'] == cluster_index].index.values.astype(int)[0]
        row = df_from_records.iloc[dfb]
        row_v = row[1:-1]

        # extract the other genes names in the same cluster
        for t in row_v:
            strain = row_v[row_v == t].index[0]  # get the strain of the current gene
            if t == '-':
                continue
            s_ds = t.split(';')
            for s_name in s_ds:
                if s_name == '-':
                    continue
                tup = (s_name, strain, cluster_index)
                genes_cluster.append(tup)

        df_from_records_g = pd.DataFrame.from_records(genes_cluster,
                                                      columns=['locus_tag', 'strain_name', 'cluster_index'])

        col_names = ['locus_tag', 'genomic_accession', 'start', 'end', 'strand', 'attributes_x',
                     'product_accession', 'nonredundant_refseq', 'name', 'protein_sequence', 'dna_sequence']
        cols_attr = (getattr(models.Genes, item) for item in col_names)
        results = db.query(models.Genes).with_entities(*cols_attr).all()
        # cols = ', '.join(col_names)
        # my_query = "SELECT {} FROM \"Genes\"".format(cols)
        # results = db.execute(my_query).fetchall()
        df_from_records_all_genes = pd.DataFrame(results, columns=col_names)
        res = df_from_records_g.merge(df_from_records_all_genes)

        # move cluster_index column to first column
        mid = res['cluster_index']
        res.drop(labels=['cluster_index'], axis=1, inplace=True)
        res.insert(0, 'cluster_index', mid)

        frames.append(res)
        # df_from_records_all_genes['locus_tag'] =  df_from_records_all_genes['attributes_x']
        # df_from_records_all_genes['locus_tag'] = df_from_records_all_genes['locus_tag'].apply(lambda x: remove_old_locus_string(x))
        # frames.append(df_from_records_g.merge(df_from_records_all_genes))

    return pd.concat(
        frames).drop_duplicates()  # return a single dataframe with all of the genes info in the same cluster


def remove_old_locus_string(s):
    if s:
        return s.replace('old_locus_tag=', '')
    return s


# for requirement 4.5
def get_defense_systems_of_two_strains(db: Session, first_strain_name, second_strain_name):
    """
    the function returns df that contains two vectors of each defense system that represents is they are in the strains
    :param db: the connection to the database
    :param first_strain_name: the first defense system
    :param second_strain_name: the second defense system
    :return: dataframe that contains the relevant information
    """
    cols = ['index', first_strain_name.lower(), second_strain_name.lower()]
    query = db.query(models.StrainsDefenseSystems) \
        .with_entities(getattr(models.StrainsDefenseSystems, cols[0]),
                       getattr(models.StrainsDefenseSystems, cols[1]),
                       getattr(models.StrainsDefenseSystems, cols[2])) \
        .all()
    df = pd.DataFrame.from_records(query, columns=['index', first_strain_name.lower(), second_strain_name.lower()])
    return df


# for requirement 4.5 and 4.6
def get_defense_systems_names(db: Session, flag=False):
    """
    the function returns all of the defense systems names
    :param db: the connection to the database
    :param flag: the flag decides which value to return (true = set, false = df in records format)
    :return: dataframe that contains the relevant information or set of the names
    """
    query = db.query(models.GenesDefenseSystems) \
        .with_entities(models.DefenseSystems.name).all()
    df = pd.DataFrame.from_records(query, columns=['defense_systems'])
    if flag:
        lst = df['defense_systems']
        s = set(lst)
        return s
    result_str = []
    id = 0
    list_of_def = list(df['defense_systems'])
    for r in list_of_def:
        d = {}
        d['name'] = r
        d['key'] = id
        id += 1
        result_str.append(d)
    return result_str


# for the requirement of 4.6
def get_all_strains_of_defense_system(db: Session, defense_system):
    """
    the function returns df that contains one vector of each defense system that represents is they are in the strain
    :param db: the connection to the database
    :param defense_system: the first defense system
    :return: dataframe that contains the relevant information
    """
    cols = ['index', defense_system.lower()]
    query = db.query(models.StrainsDefenseSystems)\
        .with_entities(getattr(models.StrainsDefenseSystems, cols[0]),
                       getattr(models.StrainsDefenseSystems, cols[1]),)                       \
        .all()
    df = pd.DataFrame.from_records(query, columns=['index', defense_system.lower()])
    if df.empty:
        return "No Results"
    return df


# for the requirement of 4.6
def get_strain_column_data(db: Session, category_name):
    """
    the function returns df that contains one vector of each defense system that represents is they are in the strain
    :param db: the connection to the database
    :param category_name: the name of the column we want to extract from the DB
    :return: dataframe that contains the relevant information
    """
    cols = ['index', category_name.lower()]
    query = db.query(models.Strains)\
        .with_entities(getattr(models.Strains, cols[0]),
                       getattr(models.Strains, cols[1]),).all()
    df = pd.DataFrame.from_records(query, columns=['index', category_name.lower()])
    if df.empty:
        return "No Results"
    return df


# for requirement 4.6
def dict_of_clusters_related_to_gene(db: Session, strain, gene):
    """
    the function returns df that contains the cluster, the gene and the dictionary of all the other cluster
    :param db: the connection to the database
    :param strain: the name of the strain (it's the column name in clusters table)
    :param gene: the name of the gene we are looking for
    :return: dataframe that contains the relevant information
    """
    search = "%{}%".format(gene)
    query = db.query(models.Clusters)\
        .with_entities(models.Clusters.index, getattr(models.Clusters, strain.lower()),
                       models.Clusters.combined_index).filter(getattr(models.Clusters, strain.lower()).like(search)).all()
    df = pd.DataFrame.from_records(query, columns=['index', strain.lower(), 'combined_index'])
    if df.empty:
        return "No Results"
    return df

'''
this get the strain id and the strain name with the MLST metadata
'''

def get_strains_MLST(db: Session):
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain,models.Strains.mlst_sequence_type).all()
    df_from_records = pd.DataFrame.from_records(result, columns=['index', 'strain', 'MLST'])
    return df_from_records


def get_colors_dict(db: Session):
    """
    the function returns a dictionary of colors
    :param db: the connection to the database
    :return: dictionary of colors
    """
    result = db.query(models.DefenseSystems).with_entities(models.DefenseSystems.name, models.DefenseSystems.label,
                                                   models.DefenseSystems.color).all()
    df_from_records = pd.DataFrame.from_records(result, columns=['value', 'label', 'color'])
    print(df_from_records)
    dict = df_from_records.to_dict(orient='records')
    return dict