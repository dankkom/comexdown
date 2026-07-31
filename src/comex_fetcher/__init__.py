"""Brazil's foreign trade data downloader"""

from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from quantilica.core.http import ProgressCallback
from quantilica.core.logging import get_logger

try:
    __version__ = version("comex-fetcher")
except PackageNotFoundError:
    __version__ = "0.0.0"

logger = get_logger(__name__)

__all__ = ["__version__"]

from . import download, storage, urls


def get_year(
    data_dir: Path,
    year: int,
    exp=False,
    imp=False,
    mun=False,
    show_progress: bool = False,
    progress: ProgressCallback | None = None,
):
    """Download trade data for a specific year."""
    if not exp and not imp:
        exp = imp = True
    directions = []
    if exp:
        directions.append("exp")
    if imp:
        directions.append("imp")

    repo = storage.DataRepository(root=data_dir)

    for direction in directions:
        url = urls.trade(direction=direction, year=year, mun=mun)
        date = download._safe_head_date(url)
        file_path = repo.path_trade(
            direction=direction, year=year, mun=mun, last_modified=date
        )
        download.download_file(
            url, file_path, show_progress=show_progress, progress=progress
        )


def get_year_nbm(
    data_dir: Path,
    year: int,
    exp=False,
    imp=False,
    show_progress: bool = False,
    progress: ProgressCallback | None = None,
):
    """Download older trade data (NBM) for a specific year."""
    if not exp and not imp:
        exp = imp = True
    directions = []
    if exp:
        directions.append("exp")
    if imp:
        directions.append("imp")

    repo = storage.DataRepository(root=data_dir)

    for direction in directions:
        url = urls.trade(direction=direction, year=year, nbm=True)
        date = download._safe_head_date(url)
        file_path = repo.path_trade_nbm(
            direction=direction, year=year, last_modified=date
        )
        download.download_file(
            url, file_path, show_progress=show_progress, progress=progress
        )


def get_table(
    data_dir: Path,
    table: str,
    show_progress: bool = False,
    progress: ProgressCallback | None = None,
):
    """Download an auxiliary code table."""
    url = urls.table(table)
    repo = storage.DataRepository(root=data_dir)
    date = download._safe_head_date(url)
    file_path = repo.path_aux(name=table, last_modified=date)
    download.download_file(
        url, file_path, show_progress=show_progress, progress=progress
    )


def get_repetro(
    data_dir: Path,
    show_progress: bool = False,
    progress: ProgressCallback | None = None,
):
    """Download REPETRO tables."""
    from .constants import REPETRO_TABLES

    repo = storage.DataRepository(root=data_dir)
    for dataset in REPETRO_TABLES:
        url = urls.get_url(dataset)
        date = download._safe_head_date(url)
        file_path = repo.path_repetro(dataset, last_modified=date)
        download.download_file(
            url, file_path, show_progress=show_progress, progress=progress
        )


def get_validation(
    data_dir: Path,
    show_progress: bool = False,
    progress: ProgressCallback | None = None,
):
    """Download validation totals."""
    from .constants import TOTAIS_PARA_VALIDACAO

    repo = storage.DataRepository(root=data_dir)
    for dataset in TOTAIS_PARA_VALIDACAO:
        url = urls.get_url(dataset)
        date = download._safe_head_date(url)
        file_path = repo.path_validacao(dataset, last_modified=date)
        download.download_file(
            url, file_path, show_progress=show_progress, progress=progress
        )


def get_other_tables(
    data_dir: Path,
    show_progress: bool = False,
    progress: ProgressCallback | None = None,
):
    """Download other auxiliary tables in Excel format."""
    repo = storage.DataRepository(root=data_dir)
    url = urls.get_url("tabelas-auxiliares")
    date = download._safe_head_date(url)
    file_path = repo.path_other("tabelas-auxiliares", "xlsx", last_modified=date)
    download.download_file(
        url, file_path, show_progress=show_progress, progress=progress
    )


def download_all(
    data_dir: Path,
    show_progress: bool = True,
    on_progress: Callable[[int, int], None] | None = None,
    file_progress: ProgressCallback | None = None,
):
    """Download all available datasets."""
    download.download_all(
        data_dir,
        show_progress=show_progress,
        on_progress=on_progress,
        file_progress=file_progress,
    )
