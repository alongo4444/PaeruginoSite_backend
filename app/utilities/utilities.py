from app.db.session import get_db
from app.db.crud import (
    get_colors_dict
)


def validate_params(systems, subtree, strains, db_systems):
    """
    this function gets the user parameters of systems and subtrees and keep only
    the arguments that saved in the db. otherwise - deletes from the parameters the bad values.
    :param systems: list of defence systems
    :param subtree: list of strains to show
    :param strains: strains that saved in the db
    :param db_systems: defence systems that saved in the db
    :return:
        systems - cleared list of defence systems after deleting bad values
        subtree - cleared list of strains after deleting bad values
    """
    bad_systems = [sys.replace('-', '_').replace('|', '_').replace(' ', '_').upper() for sys in systems if
                   sys.replace('-', '_').replace('|', '_').replace(' ', '_').upper() not in db_systems]

    systems = [sys.replace('-', '_').replace('|', '_').replace(' ', '_').upper() for sys in systems if
               sys.replace('-', '_').replace('|', '_').replace(' ', '_').upper() in db_systems]
    bad_subtree = [strain for strain in subtree if strain not in strains['index']]
    subtree = [strain for strain in subtree if strain in strains['index']]

    return systems, subtree, bad_systems, bad_subtree


def get_first_layer_offset(x):
    """
    this function calculate the first layer offset of the phylogenetic tree via
    a non-linear regression function based on trial and error
    :param x: size of the phylogenetic subtree
    :return: offset of the first layer
    """
    if x == 0:
        return str(0.065)
    return str(28.9477*(x**-0.884779))


def get_font_size(x):
    """
    this function gets the number of strains the user want to show and return compatible font size.
    :param x: size of the phylogenetic subtree
    :return: font size of the phylogenetic tree
    """
    if (x == 0):
        return str(100)
    return str(0.06 * x + 15.958)


def get_spacing(x):
    """
    this function gets the number of strains the user want to show and return compatible spacing in legend of graph
    :param x: size of the phylogenetic subtree
    :return: the spacing required for the phylogenetic tree
    """
    if (x == 0):
        return str(2)
    return str(0.001162 * x + 0.311)


def get_offset(x):
    """
    this function gets the number of strains the user want to show and return compatible offset (spacing) between layers
    :param x: size of the phylogenetic subtree
    :return: offset of the layers (where layer index >0)
    """
    if (x == 0):
        return str(0.03)
    return str(-0.0001 * x + 0.15)


def get_resolution(x, layer):
    """
    this function gets the number of strains the user want to show and return compatible graph resolution
    :param x: size of the phylogenetic subtree
    :return: resolution of the phylogenetic tree
    """
    if x == 0:
        return 150
    return -9.2456e-11 * (x ** 4) + 2.9165e-7 * (x ** 3) + -0.00032504 * (x ** 2) + 0.241398 * x


def load_colors():
    """
    this function reads the colors from the DB and save it in dictionary
    for layer coloring
    :return: dictionary that maps each defense system to its color code.
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
    :return: list of all defense systems names
    """
    def_dict = load_colors()
    defense_names = [x for x in def_dict.keys()]
    return list(defense_names)


def get_systems_counts(strains):
    """
    the function counts the system
    :param strains: strains lists
    :return: strains with counter number
    """
    str_columns = ['index', 'strain', 'isolation_type', 'MLST']
    columns = [column for column in strains.columns if column not in str_columns]
    strains['count'] = strains.apply(lambda x: x[columns].tolist().count(1), axis=1)
    return strains
