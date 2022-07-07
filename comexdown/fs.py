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


from pathlib import Path

from comexdown.tables import TABLES


def path_aux(
    root: Path,
    name: str,
) -> Path:
    if isinstance(root, str):
        root = Path(root)
    file_info = TABLES.get(name)
    if not file_info:
        return
    filename = file_info.get("file_ref")
    path = root / "auxiliary-tables" / filename
    return path


def path_trade(
    root: Path,
    direction: str,
    year: int,
    mun: bool = False,
) -> Path:
    if isinstance(root, str):
        root = Path(root)
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
    root: Path,
    direction: str,
    year: int,
) -> Path:
    if isinstance(root, str):
        root = Path(root)
    prefix = ""
    if direction.lower() == "exp":
        prefix = "EXP_"
    elif direction.lower() == "imp":
        prefix = "IMP_"
    else:
        raise ValueError(f"Invalid argument direction={direction}")
    direction = direction + "-nbm"
    return root / direction / f"{prefix}{year}_NBM.csv"


def get_creation_time(path: Path) -> float:
    """Get the creation time of a file.

    Args:
        path: Path to the file.

    Returns:
        Creation time of the file.

    """
    return path.stat().st_ctime
