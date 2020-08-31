"""Brazil's foreign trade data downloader"""


from comexdown import download
from comexdown import fs


__version__ = "1.0"


# -----------------------------------DOWNLOAD-----------------------------------
def get_year(year, exp=False, imp=False, mun=False, path=None):
    """Download trade data

    Parameters
    ----------
    year : int
        Year to download
    exp : bool, optional
        If True, download exports data, by default False
    imp : bool, optional
        If True, download imports data, by default False
    mun : bool, optional
        If True, download municipality data, by default False
    path : str, optional
        Destination path to save downloaded data, by default None
    """
    dd = fs.DataDirectory(root=path)
    if mun:
        if exp:
            download.exp_mun(
                year=year,
                path=dd.path_trade(direction="exp", year=year, mun=True),
            )
        if imp:
            download.imp_mun(
                year=year,
                path=dd.path_trade(direction="imp", year=year, mun=True),
            )
    else:
        if exp:
            download.exp(
                year=year,
                path=dd.path_trade(direction="exp", year=year, mun=False),
            )
        if imp:
            download.imp(
                year=year,
                path=dd.path_trade(direction="imp", year=year, mun=False),
            )


def get_year_nbm(year, exp=False, imp=False, path=None):
    """Download older trade data

    Parameters
    ----------
    year : int
        Year to download
    exp : bool, optional
        If True, download export data, by default False
    imp : bool, optional
        If True, download import data, by default False
    path : str, optional
        Destination path to save downloaded data, by default None
    """
    dd = fs.DataDirectory(root=path)
    if exp:
        download.exp_nbm(
            year=year,
            path=dd.path_trade_nbm(direction="exp", year=year),
        )
    if imp:
        download.imp_nbm(
            year=year,
            path=dd.path_trade_nbm(direction="imp", year=year),
        )


def get_complete(exp=False, imp=False, mun=False, path="."):
    """Download complete trade data

    Parameters
    ----------
    exp : bool, optional
        If True, download complete export data, by default False
    imp : bool, optional
        If True, download complete import data, by default False
    mun : bool, optional
        If True, download complete municipality trade data, by default False
    path : str, optional
        Destination path to save downloaded data, by default "."
    """
    if mun:
        if exp:
            download.exp_mun_complete(path)
        if imp:
            download.imp_mun_complete(path)
    else:
        if exp:
            download.exp_complete(path)
        if imp:
            download.imp_complete(path)


def get_table(table, path=None):
    """Download auxiliary code tables

    Parameters
    ----------
    table : str
        Name of auxiliary code table to download
    path : str, optional
        Destination path to save downloaded code table, by default "."
    """
    dd = fs.DataDirectory(root=path)
    download.table(
        table_name=table,
        path=dd.path_aux(name=table),
    )
