from app.db.session import get_db
from app.db.crud import (
    get_colors_dict
)


def validate_params(systems, subtree, strains, db_systems):
    """
    this function gets the user parameters of systems and subtrees and keep only
    the arguments that saved in the db. otherwise - deletes from the parameters the bad values.
    systems - list of defence systems
    subtree - list of strains to show
    strains - strains that saved in the db
    db_systems - defence systems that saved in the db
    return:
        systems - cleared list of defence systems after deleting bad values
        subtree - cleared list of strains after deleting bad values
    """
    bad_systems = [sys.replace('-', '_').replace('|', '_').replace(' ', '_').upper() for sys in systems if
                   sys.replace('-', '_').replace('|', '_').replace(' ', '_').upper() not in db_systems]

    systems = [sys.replace('-', '_').replace('|', '_').replace(' ', '_').upper() for sys in systems if
               sys.replace('-', '_').replace('|', '_').replace(' ', '_').upper() in db_systems]
    # systems = [sys for sys in systems if sys not in bad_systems]
    bad_subtree = [strain for strain in subtree if strain not in strains['index']]
    subtree = [strain for strain in subtree if strain in strains['index']]
    # subtree = [strain for strain in subtree if strain not in bad_subtree]
    # bad_subtree = [str(x) for x in bad_subtree]
    return systems, subtree, bad_systems, bad_subtree


def get_first_layer_offset(x):
    """
    this function calculate the first layer offset of the phylogenetic tree via
    a non-linear regression function based on trial and error
    """
    if x > 1100 or x == 0:
        return str(0.08)
    return str(0.00000038 * (x ** 2) - 0.00097175 * x + 0.67964847)


def get_font_size(x):
    """
    this function gets the number of strains the user want to show and return compatible font size
    """
    if (x == 0):
        return str(100)
    return str(0.06 * x + 15.958)


def get_spacing(x):
    """
     this function gets the number of strains the user want to show and return compatible spacing in legend of graph
    """
    if (x == 0):
        return str(2)
    return str(0.001162 * x + 0.311)


def get_offset(x):
    """
    this function gets the number of strains the user want to show and return compatible offset (spacing) between layers
    """
    if (x == 0):
        return str(0.03)
    return str(-0.0001 * x + 0.15)


def get_resolution(x, layer):
    """
    this function gets the number of strains the user want to show and return compatible graph resolution
    """
    if (x == 0):
        resolution = 350
        plus_offset = resolution + resolution * 0.03 * layer
        return plus_offset
    return 0.183 * x + 23.672


def load_colors():
    """
    this function reads the colors from the DB and save it in dictionary
    for layer coloring
    """
    # Opening JSON file colors.json
    db = next(get_db())
    colors_dict = dict()
    li = get_colors_dict(db)  # json.load(f)
    colors_d = [x['color'] for x in li]
    names = [x['label'] for x in li]
    for (x, col) in zip(names, colors_d):
        colors_dict[x.replace('-', '_').replace('|', '_').replace(' ',
                                                                  '_').upper()] = col  # save systems (key) and color(value) in dictionary and return it
    return colors_dict


def load_def_systems_names():
    """
    this function reads the defense systems names from the DB and save it in dictionary
    for layer coloring
    """
    def_dict = load_colors()
    defense_names = [x for x in def_dict.keys()]
    return list(defense_names)


def get_systems_counts(strains):
    str_columns = ['index', 'strain', 'isolation_type', 'MLST']
    columns = [column for column in strains.columns if column not in str_columns]
    strains['count'] = strains.apply(lambda x: x[columns].tolist().count(1), axis=1)
    return strains
