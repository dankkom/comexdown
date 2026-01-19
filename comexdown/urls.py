"""URL generation for Brazil's foreign trade data sources.

This module provides functions to generate URLs for downloading various
types of foreign trade data from the Brazilian Ministry of Economy servers.

Data sources:
- Trade transaction data (NCM classification, 1997+)
- Historical trade data (NBM classification, 1989-1996)
- Municipality-level trade data
- Complete historical datasets
- Auxiliary code tables

All URLs point to the official government server at balanca.economia.gov.br.
"""

from comexdown import constants

BASE_URL = "https://balanca.economia.gov.br/balanca/bd/"


def table(table_name: str) -> str:
    """Generate URL for an auxiliary code table.

    Creates the download URL for a specific auxiliary table used to interpret
    trade data (e.g., NCM codes, country codes, municipality codes).

    Parameters
    ----------
    table_name : str
        Name of the table to download. Must be a key in constants.TABLES
        (e.g., 'ncm', 'pais', 'uf', 'agronegocio').

    Returns
    -------
    str
        Full URL to download the requested table.

    Notes
    -----
    The 'agronegocio' table is hosted on GitHub rather than the government
    server and has a custom URL.
    """
    if table_name == "agronegocio":
        return constants.TABLES["agronegocio"]["url"]
    return f"{BASE_URL}tabelas/{constants.AUX_TABLES[table_name]}"


def trade(
    direction: str,
    year: int,
    mun: bool = False,
    nbm: bool = False,
) -> str:
    """Generate URL for trade transaction data.

    Creates the download URL for trade data based on the specified parameters,
    supporting both modern NCM and historical NBM classifications, as well as
    national and municipality-level data.

    Parameters
    ----------
    direction : str
        Trade direction, either 'exp' (exports) or 'imp' (imports).
        Case insensitive, will be converted to uppercase.
    year : int
        Year of the trade data to download.
    mun : bool, optional
        If True, generates URL for municipality-level data, by default False.
        Only available for NCM data (1997+).
    nbm : bool, optional
        If True, generates URL for NBM classification data (1989-1996),
        by default False. NBM and mun cannot both be True.

    Returns
    -------
    str
        Full URL to download the requested trade data file.

    Notes
    -----
    URL patterns:
    - NCM (national): .../ncm/EXP_2020.csv
    - NCM (municipality): .../mun/EXP_2020_MUN.csv
    - NBM: .../nbm/EXP_1995_NBM.csv
    """
    direction = direction.upper()
    if nbm:
        return f"{BASE_URL}comexstat-bd/nbm/{direction}_{year}_NBM.csv"

    if mun:
        return f"{BASE_URL}comexstat-bd/mun/{direction}_{year}_MUN.csv"

    return f"{BASE_URL}comexstat-bd/ncm/{direction}_{year}.csv"


def complete(direction: str, mun: bool = False) -> str:
    """Generate URL for complete historical trade dataset.

    Creates the download URL for the complete historical dataset containing
    all available years of trade data in a single compressed file.

    Parameters
    ----------
    direction : str
        Trade direction, either 'exp' (exports) or 'imp' (imports).
        Case insensitive, will be converted to uppercase.
    mun : bool, optional
        If True, generates URL for complete municipality-level dataset,
        by default False.

    Returns
    -------
    str
        Full URL to download the complete historical dataset as a ZIP file.

    Notes
    -----
    Complete files are large (multiple GB) and include all available years.
    File names:
    - National: EXP_COMPLETA.zip or IMP_COMPLETA.zip
    - Municipality: EXP_COMPLETA_MUN.zip or IMP_COMPLETA_MUN.zip
    """
    direction = direction.upper()
    if mun:
        return f"{BASE_URL}comexstat-bd/mun/{direction}_COMPLETA_MUN.zip"
    return f"{BASE_URL}comexstat-bd/ncm/{direction}_COMPLETA.zip"
