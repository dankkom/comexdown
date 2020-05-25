"""Functions to download trade data and code tables"""


from urllib import error, request
import os
import time
import sys


CANON_URL = "http://www.mdic.gov.br/balanca/bd/"

TABLES = {
    "ncm": {
        "description": "Códigos NCM e descrições.",
        "file_ref": "NCM.csv",
        "key": "CO_NCM",
        "name": "NCM - Nomenclatura Comum do Mercosul",
    },
    "sh": {
        "description": "Códigos e descrições do Sistema Harmonizado (Seções, Capítulos-SH2, Posições-SH4 e Subposições-SH6).",
        "file_ref": "NCM_SH.csv",
        "key": "CO_SH6",
        "name": "SH - Sistema Harmonizado",
    },
    "cuci": {
        "description": "Códigos e descrições dos níveis da classificação CUCI (Revisão 4). Pode ser utilizada conjuntamente com ISIC.",
        "file_ref": "NCM_CUCI.csv",
        "key": "CO_CUCI",
        "name": "CUCI - Classificação Uniforme para Comércio Internacional",
    },
    "cgce": {
        "description": "Códigos e descrições dos níveis da classificação CGCE.",
        "file_ref": "NCM_CGCE.csv",
        "key": "CO_CGCE_N3",
        "name": "CGCE - Classificação por Grandes Categorias Econômicas",
    },
    "isic": {
        "description": "Códigos e descrições da classificação ISIC (Revisão 4).",
        "file_ref": "NCM_ISIC.csv",
        "key": "CO_ISIC_CLASSE",
        "name": "ISIC - International Standard Industrial Classification (Setores Industriais)",
    },
    "siit": {
        "description": "Códigos e descrições da classificação SIIT.",
        "file_ref": "NCM_SIIT.csv",
        "key": "CO_SIIT",
        "name": "SIIT - Setores Industriais por Intensidade Tecnológica",
    },
    "fat_agreg": {
        "description": "Códigos e descrições de Fator Agregado das NCMs. Pode ser utilizada conjuntamente com a tabela de PPI ou PPE.",
        "file_ref": "NCM_FAT_AGREG.csv",
        "key": "",
        "name": "Fator Agregado da NCM - Classificação própria da SECEX",
    },
    "unidade": {
        "description": "Códigos e descrições das unidades estatísticas das NCMs.",
        "file_ref": "NCM_UNIDADE.csv",
        "key": "CO_UNID",
        "name": "Unidade Estatística da NCM",
    },
    "ppi": {
        "description": "Códigos e descrições da Pauta de Produtos Importados. DEVE SER UTILIZADA APENAS PARA IMPORTAÇÃO.",
        "file_ref": "NCM_PPI.csv",
        "key": "CO_PPI",
        "name": "Pauta de Produtos Importados - Classificação própria da SECEX",
    },
    "ppe": {
        "description": "Códigos e descrições da Pauta de Produtos Exportados. DEVE SER UTILIZADA APENAS PARA EXPORTAÇÃO.",
        "file_ref": "NCM_PPE.csv",
        "key": "CO_PPE",
        "name": "Pauta de Produtos Exportados - Classificação própria da SECEX",
    },
    "grupo": {
        "description": "Códigos e descrições de Grupo de Produtos. DEVE SER UTILIZADA APENAS PARA EXPORTAÇÃO.",
        "file_ref": "NCM_GRUPO.csv",
        "key": "CO_EXP_SUBSET",
        "name": "Grupo de Produtos- Classificação própria da SECEX",
    },
    "pais": {
        "description": "Códigos e descrições de países.",
        "file_ref": "PAIS.csv",
        "key": "CO_PAIS",
        "name": "Países",
    },
    "pais_bloco": {
        "description": "Códigos e descrições das principais agregações de países em blocos. Deve ser usada em cojunto com a tabela de países.",
        "file_ref": "PAIS_BLOCO.csv",
        "key": "CO_BLOCO",
        "name": "Blocos de Países",
    },
    "uf": {
        "description": "Códigos e nome das unidades da federação (estados) do Brasil.",
        "file_ref": "UF.csv",
        "key": ["CO_UF", "SG_UF"],
        "name": "Unidades da Federação",
    },
    "uf_mun": {
        "description": "Códigos e nome dos municípios brasileiros. Pode ser utilizada em conjunto com a tabela de UF. Fundamental para utilização junto com o arquivo de dados brutos por municípios domicílio fiscal das empresas.",
        "file_ref": "UF_MUN.csv",
        "key": "CO_MUN_GEO",
        "name": "Municípios",
    },
    "via": {
        "description": "Código e descrição da via (modal) de transporte",
        "file_ref": "VIA.csv",
        "key": "CO_VIA",
        "name": "Via",
    },
    "urf": {
        "description": "Código e descrição da Unidade da Receita Federal (embarque/despacho).",
        "file_ref": "URF.csv",
        "key": "CO_URF",
        "name": "Urf",
    },
    "isic_cuci": {
        "description": "Códigos e descrições dos níveis ISIC e CUCI usados na coletiva de apresentação da balança comercial brasileira.",
        "file_ref": "ISIC_CUCI.csv",
        "key": ["CO_CUCI_GRUPO", "CO_ISIC_SECAO"],
        "name": "ISIC Seção x CUCI Grupo",
    },
    "nbm": {
        "description": "Códigos NBM e descrições.",
        "file_ref": "NBM.csv",
        "key": "CO_NBM",
        "name": "NBM (1989-1996) - Nomenclatura Brasileira de Mercadorias",
    },
    "nbm_ncm": {
        "description": "Tabela de conversão entre códigos NBM e NCM.",
        "file_ref": "NBM_NCM.csv",
        "key": ["CO_NBM", "CO_NCM"],
        "name": "NBMxNCM - Tabela de conversão",
    },
}

AUX_TABLES = {
    name: TABLES[name]["file_ref"] for name in TABLES
}


def download_file(url, path, retry=3, blocksize=1024):
    """Downloads the file in `url` and saves it in `path`

    Parameters
    ----------
    url: str
        The resource's URL to download
    path: str
        The destination path of downloaded file
    retry: int [default=3]
        Number of retries until raising exception
    blocksize: int [default=1024]
        The block size of requests

    """
    if not os.path.exists(path):
        os.makedirs(path)

    filename = os.path.join(path, url.rsplit("/", maxsplit=1)[1])
    for x in range(retry):
        sys.stdout.write(f"Baixando arquivo: {url:<50} --> {filename}\n")
        sys.stdout.flush()
        try:
            resp = request.urlopen(url)
            length = resp.getheader("content-length")
            if length:
                length = int(length)

            size = 0
            with open(filename, "wb") as f:
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
            sys.stdout.write(f"\nErro... {e}")
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
