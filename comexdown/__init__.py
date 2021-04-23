"""Brazil's foreign trade data downloader"""


from comexdown import download, fs

__version__ = "1.3.3"


def get_year(path, year, exp=False, imp=False, mun=False):
    """Download trade data

    Parameters
    ----------
    path : str
        Destination path to save downloaded data, by default None
    year : int
        Year to download
    exp : bool, optional
        If True, download exports data, by default False
    imp : bool, optional
        If True, download imports data, by default False
    mun : bool, optional
        If True, download municipality data, by default False
    """
    if mun:
        if exp:
            download.exp_mun(
                year=year,
                path=fs.path_trade(
                    root=path,
                    direction="exp",
                    year=year,
                    mun=True,
                ),
            )
        if imp:
            download.imp_mun(
                year=year,
                path=fs.path_trade(
                    root=path,
                    direction="imp",
                    year=year,
                    mun=True,
                ),
            )
    else:
        if exp:
            download.exp(
                year=year,
                path=fs.path_trade(
                    root=path,
                    direction="exp",
                    year=year,
                    mun=False,
                ),
            )
        if imp:
            download.imp(
                year=year,
                path=fs.path_trade(
                    root=path,
                    direction="imp",
                    year=year,
                    mun=False,
                ),
            )


def get_year_nbm(path, year, exp=False, imp=False):
    """Download older trade data

    Parameters
    ----------
    path : str
        Destination path to save downloaded data, by default None
    year : int
        Year to download
    exp : bool, optional
        If True, download export data, by default False
    imp : bool, optional
        If True, download import data, by default False
    """
    if exp:
        download.exp_nbm(
            year=year,
            path=fs.path_trade_nbm(root=path, direction="exp", year=year),
        )
    if imp:
        download.imp_nbm(
            year=year,
            path=fs.path_trade_nbm(root=path, direction="imp", year=year),
        )


def get_complete(path, exp=False, imp=False, mun=False):
    """Download complete trade data

    Parameters
    ----------
    path : str
        Destination path to save downloaded data, by default "."
    exp : bool, optional
        If True, download complete export data, by default False
    imp : bool, optional
        If True, download complete import data, by default False
    mun : bool, optional
        If True, download complete municipality trade data, by default False
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


def get_table(path, table):
    """Download auxiliary code tables

    Parameters
    ----------
    path : str
        Destination path to save downloaded code table
    table : str
        Name of auxiliary code table to download
    """
    if table == "agronegocio":
        download.agronegocio(
            path=fs.path_aux(root=path, name=table),
        )
        return
    download.table(
        table_name=table,
        path=fs.path_aux(root=path, name=table),
    )
