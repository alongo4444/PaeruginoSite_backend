from sqlalchemy.orm import Session
import pandas as pd
import json
import io

from starlette.responses import StreamingResponse

from . import models, schemas


# from app.core.security import get_password_hash


def get_genes_download(db: Session, selectedC, selectedAS):
    """
    the function gets the information of the genes from the db
    :param db: the database connection
    :param selectedC: the selected columns
    :param selectedAS: the selected rows names
    :return: a table with information on the genes
    """
    selectedC.insert(0, 'locus_tag')

    try:
        cols_attr = [getattr(models.Genes, col) for col in selectedC]
    except AttributeError as err:
        print(err)
        return pd.DataFrame()
    if(selectedAS):
        results = db.query(models.Genes).filter(models.Genes.assembly.in_(selectedAS)).with_entities(*cols_attr).all()
    else:
        results = db.query(models.Genes).with_entities(*cols_attr).all()
    df_from_records = pd.DataFrame(results, columns=selectedC)

    return df_from_records


def get_genes(db: Session):
    """
    this function return all the the genes that appears in the strains and their genes
    :param db: the connection to the database
    :return: dataframe that contains the relevant information
    """
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
    :param db: the connection to the database
    """
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain).all()
    df_from_records = pd.DataFrame.from_records(result, columns=['index', 'strain'])
    df_from_records = df_from_records.rename(columns={"strain": "name"})
    result = df_from_records.to_json(orient="records")
    parsed = json.loads(result)
    json.dumps(parsed, indent=4)
    return parsed


def get_strains_names(db: Session):
    """
    the function gets the names of the strains
    :param db: the connection to the db
    :return: a dictionary of the strains names
    """
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
    df_from_records['name'] = df_from_records['name'] + " (" + df_from_records['key'] + ")"
    result = df_from_records.to_json(orient="records")
    parsed = json.loads(result)
    json.dumps(parsed, indent=4)
    return parsed
    # return df_from_records.to_csv()


# for requirement 4.7

def get_strains_cluster(db: Session, strains_genes):
    """
    this function return all the the clusters that appears in the strains and their genes
    :param db: the connection to the database
    :param strains_genes: the list of the strains and their genes max of 3 min of 1
    :return: list of the cluster index and the combined_index
    """
    list_strains = []
    for s_g in strains_genes:
        split = s_g.split('-')
        search = "%{}%".format(split[1])
        results = db.query(models.Clusters). \
            with_entities(models.Clusters.index, models.Clusters.combined_index). \
            filter(getattr(models.Clusters, split[0].lower()).like(search)).all()
        if len(results) > 0:
            list_strains.append(results[0])
    return list_strains


# for requirement 4.8
def get_strain_isolation(db: Session):
    """
    this function get the strain id and the strain name and isolation type
    :param db: the connection to the database
    :return: dataframe that contains the relevant information
    """
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain,
                                                    models.Strains.isolation_type).all()
    df_from_records = pd.DataFrame.from_records(result, index='index', columns=['index', 'strain', 'isolation_type'])
    return df_from_records


# for requirement 4.8
def get_strain_isolation_mlst(db: Session):
    """
    this function return the dataframe that contain the columns 'index', 'strain', 'isolation_type', 'MLST'
    and return all of the rows
    :param db: the connection to the database
    :return: dataframe that contains the relevant information
    """
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain,
                                                    models.Strains.isolation_type,
                                                    models.Strains.mlst_sequence_type).all()
    df_from_records = pd.DataFrame.from_records(result, columns=['index', 'strain', 'isolation_type', 'MLST'])
    return df_from_records


# for requirement 4.7

def get_strain_id_name(db: Session):
    """
    this function return a dataframe that contains the strain id and the strain name
    :param db: the connection to the database
    :return: dataframe that contains the relevant information
    """
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain).all()
    df_from_records = pd.DataFrame.from_records(result, columns=['index', 'strain'])  # , index='index'
    return df_from_records


# for requirement 4.7

def get_gene_by_strain(db: Session, strain_id):
    """
    this function return all genes of a certain strain
    :param db: the connection to the database
    :param strain_id: the stain that we want to get all of the genes
    :return: dataframe of all the the genes of a certain strain
    """
    results = db.query(models.Genes.locus_tag).filter(models.Genes.assembly == strain_id).all()
    return results


def get_genes_by_defense(db: Session, selectedC, selectedAS):
    """
    returns a dataframe with the genes information of the system defenses in
    selectedAS with the columns in selectedC.
    :param db: the connection to the database
    :param selectedC: the selected columns
    :param selectedAS: the selected defense systems
    :return: a table of the genes with the defense systems
    """
    # if the user didn't select any defense system, return all:
    if not selectedAS:
        ds_names = get_defense_systems_names(db)
        selectedAS = [x['name'] for x in ds_names]

    # make a list of tuples to be imported to a dataframe later
    genes_ds = []
    for s in selectedAS:
        search = "%{}%".format(s)
        results = db.query(models.GenesDefenseSystems). \
            with_entities(models.GenesDefenseSystems.locus_tag). \
            filter(models.GenesDefenseSystems.defense_system.like(search)).all()


        for r in results:
            for t in r:
                s_name = t.split('|')[0]
                new_row = (s_name, s)
                genes_ds.append(new_row)

    df_genes_ds = pd.DataFrame(genes_ds, columns=['locus_tag',
                                                  'ds_name'])  # import list of tuples to a dataframe. currently holds the genes and the defense system names (i.e: [PA2735, brex])

    selectedC_copy = selectedC.copy()

    # for idx, s in enumerate(selectedC_copy):
    selectedC.insert(0, 'locus_tag')
    selectedC_copy.insert(0, "locus_tag")
    try:
        cols_attr = [getattr(models.Genes, item) for item in selectedC_copy]
    except AttributeError as err:
        print(err)
        return pd.DataFrame()
    results = db.query(models.Genes).with_entities(*cols_attr).all()
    df_genes_info = pd.DataFrame(results, columns=selectedC)
    result = df_genes_ds.merge(df_genes_info)

    return result


def prepare_csv_file(dafaframe):
    """
    the function gets a df and converts it to csv
    :param dafaframe: the df
    :return: a csv file
    """
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


def get_genes_by_cluster(db: Session, genes):
    """
    the function get the genes that belongs to a cluster
    :param db: the database connection
    :param genes: the genes names
    :return: the information about the genes belong to a cluster
    """
    results = db.query(models.Clusters).with_entities(models.Clusters.index,
                                                      models.Clusters.pa14,
                                                      models.Clusters.pao1,
                                                      models.Clusters.combined_index
                                                      ).all()

    col_names = ['index', 'pa14', 'pao1', 'combined_index']
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

        df_from_records_all_genes = pd.DataFrame(results, columns=col_names)
        res = df_from_records_g.merge(df_from_records_all_genes)

        # move cluster_index column to first column
        mid = res['cluster_index']
        res.drop(labels=['cluster_index'], axis=1, inplace=True)
        res.insert(0, 'cluster_index', mid)

        frames.append(res)


    if len(frames) > 0:
        return pd.concat(
            frames).drop_duplicates()  # return a single dataframe with all of the genes info in the same cluster

    return pd.DataFrame()


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
    if df.empty:
        return "No Results"
    # else:
    #     df = df.to_dict('records')
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
    the function returns df that contains one vector of each defense system that
    represents is they are in the strain
    :param db: the connection to the database
    :param defense_system: the first defense system
    :return: dataframe that contains the relevant information
    """
    cols = ['index', defense_system.lower()]
    query = db.query(models.StrainsDefenseSystems) \
        .with_entities(getattr(models.StrainsDefenseSystems, cols[0]),
                       getattr(models.StrainsDefenseSystems, cols[1]), ) \
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
    query = db.query(models.Strains) \
        .with_entities(getattr(models.Strains, cols[0]),
                       getattr(models.Strains, cols[1]), ).all()
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
    query = db.query(models.Clusters) \
        .with_entities(models.Clusters.index, getattr(models.Clusters, strain.lower()),
                       models.Clusters.combined_index).filter(
        getattr(models.Clusters, strain.lower()).like(search)).all()
    df = pd.DataFrame.from_records(query, columns=['index', strain.lower(), 'combined_index'])
    if df.empty:
        return "No Results"
    return df


# For the browse in the phylogenetic tree
def get_strains_MLST(db: Session):
    """
    the function return the strain id and the strain name with the MLST metadata in a dataframe
    for the browse in the phylogenetic tree
    """
    result = db.query(models.Strains).with_entities(models.Strains.index, models.Strains.strain,
                                                    models.Strains.mlst_sequence_type).all()
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
    df_from_records = pd.DataFrame.from_records(result, columns=['label', 'value', 'color'])
    if df_from_records.empty:
        return "No Results"
    dict = df_from_records.to_dict(orient='records')
    return dict
