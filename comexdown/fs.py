"""Class to manage files downloaded.

root
├───auxiliary_tables
├───exp
├───imp
├───mun_exp
├───mun_imp
├───nbm_exp
└───nbm_imp

Index:

data_directory.root/index.json

{
    "auxiliary_tables": [<file_info>, ...],
    "exp": [<file_info>, ...],
    "imp": [<file_info>, ...],
    "nbm_exp": [<file_info>, ...],
    "nbm_imp": [<file_info>, ...],
    "mun_exp": [<file_info>, ...],
    "mun_imp": [<file_info>, ...],
}

file_info = {
    "filepath": <filepath>,
    "size": <size>,
    "blake2": <blake2>,
    "timestamp": <timestamp>,
}

"""


import datetime as dt
import hashlib
import json
from pathlib import Path, PurePath
from typing import Union

from comexdown import download
from comexdown.tables import TABLES


class DataDirectory:

    def __init__(self, root: str) -> None:
        self.root = Path(root)

    def path_aux(self, name: str) -> str:
        file_info = TABLES.get(name)
        if not file_info:
            return
        filename = file_info.get("file_ref")
        path = self.root / "auxiliary_tables" / filename
        return path

    def path_trade(self, direction: str, year: int, mun: bool = False) -> str:
        prefix = sufix = ""
        if direction.lower() == "exp":
            prefix = "EXP_"
        elif direction.lower() == "imp":
            prefix = "IMP_"
        else:
            raise ValueError(f"Invalid argument direction={direction}")
        if mun:
            sufix = "_MUN"
        return self.root / direction / f"{prefix}{year}{sufix}.csv"

    def update_aux(self, name: str) -> None:
        path = self.path_aux(name)
        download.table(name, path)

    def update_trade(self, direction: str, year: int, mun: bool = False) -> None:
        path = self.path_trade(direction=direction, year=year, mun=mun)
        if direction == "exp" and not mun:
            if mun:
                download.exp_mun(year, path)
            else:
                download.exp(year, path)
        elif direction == "imp" and not mun:
            if mun:
                download.imp_mun(year, path)
            else:
                download.imp(year, path)
        else:
            raise ValueError(f"Invalid arguments direction={direction}")

    def update_exp(self, year: int) -> None:
        self.update_trade(direction="exp", year=year, mun=False)

    def update_imp(self, year: int) -> None:
        self.update_trade(direction="imp", year=year, mun=False)

    def update_exp_mun(self, year: int) -> None:
        self.update_trade(direction="exp", year=year, mun=True)

    def update_imp_mun(self, year: int) -> None:
        self.update_trade(direction="imp", year=year, mun=True)

    def update_aux_all(self) -> None:
        for name in TABLES:
            self.update_aux(name)

    def create_index(self) -> dict:
        index = {
            "auxiliary_tables": [],
            "exp": [],
            "imp": [],
            "nbm_exp": [],
            "nbm_imp": [],
            "mun_exp": [],
            "mun_imp": [],
        }
        for directory in index.keys():
            for file in (self.root / directory).iterdir():
                print(file)
                file_hash = get_hash(file)
                timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                index[directory].append(
                    {
                        "filepath": str(file),
                        "size": file.stat().st_size,
                        "blake2": file_hash,
                        "timestamp": timestamp,
                    }
                )
        with open(self.root / "index.json", "w", encoding="utf-8") as f:
            json.dump(index, f, indent=4)
        return index

    def read_index(self):
        path = self.root / "index.json"
        with open(path, "r", encoding="utf-8") as f:
            index = json.load(f)
        for directory in index:
            for file_info in index[directory]:
                file_info["timestamp"] = dt.datetime.strptime(
                    file_info["timestamp"],
                    "%Y-%m-%d %H:%M:%S.%f",
                )
        return index


def get_hash(filepath: Union[str, PurePath]) -> str:
    h = hashlib.blake2b()
    with open(filepath, "rb") as f:
        while chunk := f.read(4096):
            h.update(chunk)
    return h.hexdigest()
