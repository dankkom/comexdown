"""Functions to manage downloaded file locations and paths.

Filenames follow the ecosystem convention:
    {dataset}_{partition}@{YYYYMMDD}.{ext}

where ``@YYYYMMDD`` is the server's Last-Modified date.  When the date is
unknown the ``@`` suffix is omitted and the legacy bare name is used.
"""

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica.core.storage import (
    BaseDataRepository,
    build_stamped_filename,
    stamp_filename,
)

from comex_fetcher.constants import TABLES


class DataRepository(BaseDataRepository):
    """Manages local storage for comex-fetcher files."""

    def __init__(self, root: Path | str):
        super().__init__(root)

    # ------------------------------------------------------------------
    # Auxiliary tables
    # ------------------------------------------------------------------

    def path_aux(
        self,
        name: str,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for an auxiliary code table file.

        Example: ``auxiliary-tables/ncm@20240315.csv``
        """
        file_info = TABLES.get(name)
        if not file_info:
            raise ValueError(f"Unknown auxiliary table name: {name}")
        ext = file_info["file_ref"].rsplit(".", 1)[-1].lower()
        filename = stamp_filename(name, ext, last_modified)
        return self.storage.path_for(f"auxiliary-tables/{filename}")

    def path_other(
        self,
        name: str,
        ext: str,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for miscellaneous auxiliary files (e.g. tabelas-auxiliares).

        Example: ``auxiliary-tables/tabelas-auxiliares@20240315.xlsx``
        """
        filename = stamp_filename(name, ext, last_modified)
        return self.storage.path_for(f"auxiliary-tables/{filename}")

    # ------------------------------------------------------------------
    # Trade data (NCM)
    # ------------------------------------------------------------------

    def path_trade(
        self,
        direction: str,
        year: int,
        mun: bool = False,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for a trade data file (NCM classification).

        Examples:
            ``exp/exp_2023@20240315.csv``
            ``exp-mun/exp-mun_2023@20240315.csv``
        """
        direction = direction.lower()
        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction!r}")
        dataset = f"{direction}-mun" if mun else direction
        filename = build_stamped_filename(
            dataset, year, ext="csv", timestamp=last_modified
        )
        return self.storage.path_for(f"{dataset}/{filename}")

    def path_trade_nbm(
        self,
        direction: str,
        year: int,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for an NBM trade data file (1989–1996).

        Example: ``exp-nbm/exp-nbm_1994@20240315.csv``
        """
        direction = direction.lower()
        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction!r}")
        dataset = f"{direction}-nbm"
        filename = build_stamped_filename(
            dataset, year, ext="csv", timestamp=last_modified
        )
        return self.storage.path_for(f"{dataset}/{filename}")

    # ------------------------------------------------------------------
    # REPETRO and validation
    # ------------------------------------------------------------------

    def path_repetro(
        self,
        dataset: str,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for a REPETRO file.

        Example: ``repetro/exp-repetro@20240315.xlsx``
        """
        filename = stamp_filename(dataset, "xlsx", last_modified)
        return self.storage.path_for(f"repetro/{filename}")

    def path_validacao(
        self,
        dataset: str,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for a validation totals file.

        Example: ``validacao/exp-validacao@20240315.csv``
        """
        filename = stamp_filename(dataset, "csv", last_modified)
        return self.storage.path_for(f"validacao/{filename}")

    def path_for_entry(
        self,
        entry: dict[str, Any],
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Route entry to the correct path generator based on its properties."""
        if entry.get("is_trade"):
            if entry.get("nbm"):
                return self.path_trade_nbm(
                    direction=entry["direction"],
                    year=entry["year"],
                    last_modified=last_modified,
                )
            return self.path_trade(
                direction=entry["direction"],
                year=entry["year"],
                mun=entry.get("mun", False),
                last_modified=last_modified,
            )
        
        if entry.get("is_table"):
            group = entry.get("table_group")
            if group == "auxiliary":
                return self.path_aux(entry["id"], last_modified=last_modified)
            elif group == "repetro":
                return self.path_repetro(entry["id"], last_modified=last_modified)
            elif group == "validation":
                return self.path_validacao(entry["id"], last_modified=last_modified)
            elif group == "other":
                return self.path_other(entry["id"], entry["ext"], last_modified=last_modified)
        
        raise ValueError(f"Unable to build path for entry: {entry}")
