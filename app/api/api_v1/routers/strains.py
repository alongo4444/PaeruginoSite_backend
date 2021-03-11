from fastapi import APIRouter, Request, Depends, Response, encoders
import subprocess, os
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from app.db.session import get_db
from app.db.crud import (
    get_strains,
)
from pathlib import Path
from PIL import Image

from app.db.schemas import StrainBase

strains_router = r = APIRouter()


@r.get(
    "/strains",
    # response_model=t.List[StrainBase],
    response_model_exclude_none=True,
)
async def strains_list(
        response: Response,
        db=Depends(get_db)
):
    """Get all strains"""
    strains = get_strains(db)
    # This is necessary for react-admin to work
    # response.headers["Content-Range"] = f"0-9/{len(users)}"
    return strains


@r.get(
    "/strains/phyloTree",
    response_model_exclude_none=True,
)
async def strains_list(
        response: Response
):
    """Get all strains"""

    r_script = open("static/phylo_tree.R", "w")
    r_script.write(
        'library(ggtreeExtra)\n##library(ggstar)\nlibrary(ggplot2)\nlibrary(ggtree)\nlibrary(treeio)\nlibrary(ggnewscale)\nlibrary(ape)\n' +
        'trfile <- system.file("extdata","tree.nwk", package="ggtreeExtra")\ntree <- read.tree(trfile)\n'+
        'p <- ggtree(tree, layout="fan", open.angle = 10, size = 0.5)\npng("'
        + (os.path.abspath("static/phylo_tree.png")).replace('\\', '/') +
        '", units="cm", width=800, height=800, res=60)\nplot(p + geom_tiplab())\ndev.off(0)')
    r_script.close()
    command = 'C:/Program Files/R/R-4.0.3/bin/Rscript.exe'
    # todo replace with command = 'Rscript'  # OR WITH bin FOLDER IN PATH ENV VAR
    arg = '--vanilla'
    try:
        p = subprocess.Popen([command, arg, os.path.abspath("static/phylo_tree.R")],
                             cwd=os.path.normpath(os.getcwd() + os.sep + os.pardir), stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output, error = p.communicate()
        return FileResponse('static/phylo_tree.png')

    except Exception as e:
        print("dbc2csv - Error converting file: phylo_tree.R")
        print(e)

        return False
    return False


@r.get(
    "/strains/strainCircos/{strain_name}",
    response_model_exclude_none=True,
    response_class=FileResponse,
    status_code=200,
    #  response: Response
)
async def strain_circos_graph(strain_name):
    # the structure of the dir file will be stain_name.html and it will be stored in a specific directory.
    strain_file = Path("static/"+strain_name+".html")
    if strain_file.is_file():
        return FileResponse(strain_file, status_code=200)
    else:
        # file is not in the directory (the strain name is wrong)
        return Response(status_code=400)


