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
import os
from pathlib import Path, PurePath
from typing import Union

from comexdown.tables import TABLES


class DataDirectory:

    config_path = os.path.expanduser("~/.comexdown")

    def __init__(self, root: str = None) -> None:
        if root is None:
            root = self.read_config()
        else:
            self.root = Path(root)
            self.write_config()

    def read_config(self) -> None:
        if not os.path.exists(self.config_path):
            self.root = os.path.expanduser("~/data/comex")
            self.write_config()
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.root = Path(f.read())

    def write_config(self) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(str(self.root))

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
            direction = "mun_" + direction
        return self.root / direction / f"{prefix}{year}{sufix}.csv"

    def path_trade_nbm(self, direction: str, year: int) -> None:
        prefix = ""
        if direction.lower() == "exp":
            prefix = "EXP_"
        elif direction.lower() == "imp":
            prefix = "IMP_"
        else:
            raise ValueError(f"Invalid argument direction={direction}")
        direction = "nbm_" + direction
        return self.root / direction / f"{prefix}{year}_NBM.csv"

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
