"""Functions to manage files downloaded.

root
├───auxiliary_tables
├───exp
├───imp
├───mun_exp
├───mun_imp
├───nbm_exp
└───nbm_imp

"""

import os
import pathlib
from typing import Union

from comexdown.tables import TABLES


def path_aux(
    root: Union[pathlib.Path, str, os.PathLike],
    name: str,
) -> pathlib.Path:
    if isinstance(root, str):
        root = pathlib.Path(root)
    file_info = TABLES.get(name)
    if not file_info:
        return
    filename = file_info.get("file_ref")
    path = root / "auxiliary_tables" / filename
    return path


def path_trade(
    root: Union[pathlib.Path, str, os.PathLike],
    direction: str,
    year: int,
    mun: bool = False,
) -> pathlib.Path:
    if isinstance(root, str):
        root = pathlib.Path(root)
    prefix = sufix = ""
    if direction.lower() == "exp":
        prefix = "EXP_"
    elif direction.lower() == "imp":
        prefix = "IMP_"
    else:
        raise ValueError(f"Invalid argument direction={direction}")
    if mun:
        sufix = "_MUN"
        direction = "mun_" + direction
    return root / direction / f"{prefix}{year}{sufix}.csv"


def path_trade_nbm(
    root: Union[pathlib.Path, str, os.PathLike],
    direction: str,
    year: int,
) -> pathlib.Path:
    if isinstance(root, str):
        root = pathlib.Path(root)
    prefix = ""
    if direction.lower() == "exp":
        prefix = "EXP_"
    elif direction.lower() == "imp":
        prefix = "IMP_"
    else:
        raise ValueError(f"Invalid argument direction={direction}")
    direction = "nbm_" + direction
    return root / direction / f"{prefix}{year}_NBM.csv"
