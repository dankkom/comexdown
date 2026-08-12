"""URL generation for Brazil's foreign trade data sources.

This module provides functions to generate URLs for downloading various
types of foreign trade data from the Brazilian Ministry of Economy servers.
"""

from .constants import (
    AUX_TABLES,
    BASE_URL,
    OTHER_TABLES,
    REPETRO_TABLES,
    TOTAIS_PARA_VALIDACAO,
    TRADE,
)


def table(table_name: str) -> str:
    """Generate URL for an auxiliary code table.

    Args:
        table_name (str): The name of the auxiliary table.

    Returns:
        str: The URL for the auxiliary code table.
    """
    return get_url(table_name)


def trade(
    direction: str,
    year: int,
    mun: bool = False,
    nbm: bool = False,
) -> str:
    """Generate URL for trade transaction data.

    Args:
        direction (str): The direction of trade ('exp' or 'imp').
        year (int): The year of the data.
        mun (bool): Whether to get municipal-level data. Defaults to False.
        nbm (bool): Whether to get NBM data. Defaults to False.

    Returns:
        str: The URL for the trade transaction data.
    """
    if nbm:
        return get_url(f"{direction.lower()}-nbm", year=year)
    if mun:
        return get_url(f"{direction.lower()}-mun", year=year)
    return get_url(direction.lower(), year=year)


def get_url(table_name: str, **kwargs) -> str:
    """Centralized URL generation logic.

    Args:
        table_name (str): The name of the table or dataset.
        **kwargs: Additional arguments, such as 'year' for trade data.

    Returns:
        str: The generated URL.

    Raises:
        ValueError: If the table or dataset name is unknown.
    """
    year = kwargs.get("year")

    if table_name in TRADE:
        return TRADE[table_name]["server_dir"] + TRADE[table_name][
            "server_filename"
        ].format(year=year)

    if table_name in TOTAIS_PARA_VALIDACAO:
        return TOTAIS_PARA_VALIDACAO[table_name]["url"]

    if table_name in REPETRO_TABLES:
        return REPETRO_TABLES[table_name]["url"]

    if table_name == "tabelas-auxiliares":
        return OTHER_TABLES[table_name]["url"]

    if table_name in AUX_TABLES:
        return f"{BASE_URL}tabelas/{AUX_TABLES[table_name]}"

    raise ValueError(f"Unknown table or dataset: {table_name}")
