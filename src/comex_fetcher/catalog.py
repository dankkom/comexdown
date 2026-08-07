"""COMEX unified dataset catalog."""

import datetime as dt
from typing import Any

from .constants import (
    AUX_TABLES,
    OTHER_TABLES,
    REPETRO_TABLES,
    TABLES,
    TOTAIS_PARA_VALIDACAO,
)
from .urls import get_url

# Generate years
_CURRENT_YEAR = dt.datetime.now().year
_YEARS_NCM = list(range(1997, _CURRENT_YEAR + 1))
_YEARS_NBM = list(range(1989, 1997))

def _make_trade_entries(direction: str, years: list[int], mun: bool = False, nbm: bool = False) -> list[dict[str, Any]]:
    entries = []
    group = f"trade-{direction}"
    if nbm:
        group += "-nbm"
        base_name = f"{direction}-nbm"
    elif mun:
        group += "-mun"
        base_name = f"{direction}-mun"
    else:
        base_name = direction

    for y in years:
        entries.append({
            "id": f"{base_name}-{y}",
            "group": group,
            "url": get_url(base_name, year=y),
            "ext": "csv",
            "year": y,
            "direction": direction,
            "mun": mun,
            "nbm": nbm,
            "is_trade": True,
        })
    return entries

_ENTRIES_EXP = _make_trade_entries("exp", _YEARS_NCM)
_ENTRIES_IMP = _make_trade_entries("imp", _YEARS_NCM)
_ENTRIES_EXP_MUN = _make_trade_entries("exp", _YEARS_NCM, mun=True)
_ENTRIES_IMP_MUN = _make_trade_entries("imp", _YEARS_NCM, mun=True)
_ENTRIES_EXP_NBM = _make_trade_entries("exp", _YEARS_NBM, nbm=True)
_ENTRIES_IMP_NBM = _make_trade_entries("imp", _YEARS_NBM, nbm=True)

def _make_table_entries(group: str, table_dict: dict) -> list[dict[str, Any]]:
    entries = []
    for name, info in table_dict.items():
        url = info.get("url")
        if not url and name in AUX_TABLES:
            url = get_url(name)
        elif not url:
            url = get_url(name)
        
        ext = "csv"
        if "server_filename" in info:
            ext = info["server_filename"].split(".")[-1]
        elif "file_ref" in info:
            ext = info["file_ref"].split(".")[-1]
            
        entries.append({
            "id": name,
            "group": group,
            "url": url,
            "ext": ext,
            "is_table": True,
            "table_group": group,
        })
    return entries

_ENTRIES_AUX = _make_table_entries("auxiliary", TABLES)
_ENTRIES_REPETRO = _make_table_entries("repetro", REPETRO_TABLES)
_ENTRIES_VALIDATION = _make_table_entries("validation", TOTAIS_PARA_VALIDACAO)
_ENTRIES_OTHER = _make_table_entries("other", OTHER_TABLES)

GROUPS = {
    "trade-exp": {"name": "Exportação", "entries": _ENTRIES_EXP},
    "trade-imp": {"name": "Importação", "entries": _ENTRIES_IMP},
    "trade-exp-mun": {"name": "Exportação Municipal", "entries": _ENTRIES_EXP_MUN},
    "trade-imp-mun": {"name": "Importação Municipal", "entries": _ENTRIES_IMP_MUN},
    "trade-exp-nbm": {"name": "Exportação NBM", "entries": _ENTRIES_EXP_NBM},
    "trade-imp-nbm": {"name": "Importação NBM", "entries": _ENTRIES_IMP_NBM},
    "auxiliary": {"name": "Tabelas Auxiliares", "entries": _ENTRIES_AUX},
    "repetro": {"name": "Tabelas REPETRO", "entries": _ENTRIES_REPETRO},
    "validation": {"name": "Totais para Validação", "entries": _ENTRIES_VALIDATION},
    "other": {"name": "Outras Tabelas", "entries": _ENTRIES_OTHER},
}

GROUP_ALIASES = {
    "trade": ["trade-exp", "trade-imp", "trade-exp-mun", "trade-imp-mun", "trade-exp-nbm", "trade-imp-nbm"],
    "tables": ["auxiliary", "repetro", "validation", "other"],
}

def list_datasets(group: str | None = None) -> list[dict[str, Any]]:
    if group is not None:
        if group in GROUPS:
            return GROUPS[group]["entries"]
        if group in GROUP_ALIASES:
            return [e for g in GROUP_ALIASES[group] for e in GROUPS[g]["entries"]]
        raise ValueError(f"Unknown group: {group!r}")
    
    return [e for g in GROUPS.values() for e in g["entries"]]
