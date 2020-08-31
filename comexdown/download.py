"""Functions to download trade data and code tables"""


from urllib import error, request
import os
import time
import sys

from comexdown.tables import AUX_TABLES


CANON_URL = "http://www.mdic.gov.br/balanca/bd/"


def download_file(url, filepath=None, retry=3, blocksize=1024):
    """Downloads the file in `url` and saves it in `path`

    Parameters
    ----------
    url: str
        The resource's URL to download
    filepath: str
        The destination path of downloaded file
    retry: int [default=3]
        Number of retries until raising exception
    blocksize: int [default=1024]
        The block size of requests
    """

    if filepath:
        dirname, _ = os.path.split(filepath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        dest = filepath
    else:
        dest = url.rsplit("/", maxsplit=1)[1]
    for x in range(retry):
        sys.stdout.write(f"Downloading: {url:<50} --> {dest}\n")
        sys.stdout.flush()
        try:
            resp = request.urlopen(url)
            length = resp.getheader("content-length")
            if length:
                length = int(length)

            size = 0
            with open(dest, "wb") as f:
                while True:
                    buf1 = resp.read(blocksize)
                    if not buf1:
                        break
                    f.write(buf1)
                    size += len(buf1)
                    p = size / length
                    bar = "[{:<70}]".format("=" * int(p * 70))
                    if size > 2**20:
                        size_txt = "{: >9.2f} MiB".format(size / 2**20)
                    else:
                        size_txt = "{: >9.2f} KiB".format(size / 2**10)
                    if length:
                        sys.stdout.write(
                            f"{bar} {p*100: >5.1f}% {size_txt}\r")
                        sys.stdout.flush()

        except error.URLError as e:
            sys.stdout.write(f"\nError... {e}")
            sys.stdout.flush()
            time.sleep(3)
            if x == retry - 1:
                raise

        else:
            sys.stdout.write("\n")
            sys.stdout.flush()
            break


def table(table_name, path):
    download_file(CANON_URL + "tabelas/" + AUX_TABLES[table_name], path)


def exp(year, path):
    """Downloads a exp file

    Parameters
    ----------
    year: int
        exp year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_URL + "comexstat-bd/ncm/EXP_{year}.csv".format(year=year)
    download_file(url, path)


def imp(year, path):
    """Downloads a imp file

    Parameters
    ----------
    year: int
        imp year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_URL + "comexstat-bd/ncm/IMP_{year}.csv".format(year=year)
    download_file(url, path)


def exp_mun(year, path):
    """Downloads a exp_mun file

    Parameters
    ----------
    year: int
        exp_mun year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_URL + "comexstat-bd/mun/EXP_{year}_MUN.csv".format(year=year)
    download_file(url, path)


def imp_mun(year, path):
    """Downloads a imp_mun file

    Parameters
    ----------
    year: int
        imp_mun year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_URL + "comexstat-bd/mun/IMP_{year}_MUN.csv".format(year=year)
    download_file(url, path)


def exp_nbm(year, path):
    """Downloads a exp_nbm file

    Parameters
    ----------
    year: int
        exp_nbm year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_URL + "comexstat-bd/nbm/EXP_{year}_NBM.csv".format(year=year)
    download_file(url, path)


def imp_nbm(year, path):
    """Downloads a imp_nbm file

    Parameters
    ----------
    year: int
        imp_nbm year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_URL + "comexstat-bd/nbm/IMP_{year}_NBM.csv".format(year=year)
    download_file(url, path)


def exp_complete(path):
    """Downloads the file with complete data of exp

    Parameters
    ----------
    path : str
        Destination path directory to save file

    """
    url = CANON_URL + "comexstat-bd/ncm/EXP_COMPLETA.zip"
    download_file(url, path)


def imp_complete(path):
    """Downloads the file with complete data of imp

    Parameters
    ----------
    path : str
        Destination path directory to save file

    """
    url = CANON_URL + "comexstat-bd/ncm/IMP_COMPLETA.zip"
    download_file(url, path)


def exp_mun_complete(path):
    """Downloads the file with complete data of exp_mun

    Parameters
    ----------
    path : str
        Destination path directory to save file

    """
    url = CANON_URL + "comexstat-bd/mun/EXP_COMPLETA_MUN.zip"
    download_file(url, path)


def imp_mun_complete(path):
    """Downloads the file with complete data of imp_mun

    Parameters
    ----------
    path : str
        Destination path directory to save file

    """
    url = CANON_URL + "comexstat-bd/mun/IMP_COMPLETA_MUN.zip"
    download_file(url, path)
