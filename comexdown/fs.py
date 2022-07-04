"""Functions to manage files downloaded.

root
├───auxiliary-tables
├───exp
├───imp
├───mun-exp
├───mun-imp
├───nbm-exp
└───nbm-imp

"""


import pathlib
from typing import Union

from comexdown.tables import TABLES


def path_aux(
    root: Union[pathlib.PurePath, str],
    name: str,
) -> str:
    if isinstance(root, str):
        root = pathlib.Path(root)
    file_info = TABLES.get(name)
    if not file_info:
        return
    filename = file_info.get("file_ref")
    path = root / "auxiliary-tables" / filename
    return path


def path_trade(
    root: Union[pathlib.PurePath, str],
    direction: str,
    year: int,
    mun: bool = False,
) -> str:
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
        direction = direction + "-mun"
    return root / direction / f"{prefix}{year}{sufix}.csv"


def path_trade_nbm(
    root: Union[pathlib.PurePath, str],
    direction: str,
    year: int,
) -> None:
    if isinstance(root, str):
        root = pathlib.Path(root)
    prefix = ""
    if direction.lower() == "exp":
        prefix = "EXP_"
    elif direction.lower() == "imp":
        prefix = "IMP_"
    else:
        raise ValueError(f"Invalid argument direction={direction}")
    direction = direction + "-nbm"
    return root / direction / f"{prefix}{year}_NBM.csv"
