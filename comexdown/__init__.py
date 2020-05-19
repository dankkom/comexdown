"""Brazil's foreign trade data downloader"""


import os

from . import download


__author__ = "Daniel K. Komesu"
__author_email__ = "danielkomesu@gmail.com"
__version__ = "0.9"


# -----------------------------------DOWNLOAD-----------------------------------
def get_year(year, exp=False, imp=False, mun=False, path="."):
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
        Destination path to save downloaded data, by default "."
    """
    if mun:
        if exp:
            download.exp_mun(year, os.path.join(path, "mun_exp"))
        if imp:
            download.imp_mun(year, os.path.join(path, "mun_imp"))
    else:
        if exp:
            download.exp(year, os.path.join(path, "exp"))
        if imp:
            download.imp(year, os.path.join(path, "imp"))


def get_year_nbm(year, exp=False, imp=False, path="."):
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
        Destination path to save downloaded data, by default "."
    """
    if exp:
        download.exp_nbm(year, os.path.join(path, "nbm_exp"))
    if imp:
        download.imp_nbm(year, os.path.join(path, "nbm_imp"))


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


def get_table(table, path="."):
    """Download auxiliary code tables

    Parameters
    ----------
    table : str
        Name of auxiliary code table to download
    path : str, optional
        Destination path to save downloaded code table, by default "."
    """
    download.table(table, path=os.path.join(path, "auxiliary_tables"))
