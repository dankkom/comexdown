#!/usr/bin/env python3

"""Command-line interface for downloading Brazil's foreign trade data.

This module provides a CLI tool for downloading trade transaction data and
auxiliary code tables from Brazil's Ministry of Economy (SECEX/COMEX).

Usage:
    comexdown { trade | table } <arguments>

    comexdown trade <year> ... -o <output>
    comexdown table <table name> -o <output>

Examples:
    Download exports and imports for 2020:
        $ comexdown trade 2020

    Download exports for years 2018-2020:
        $ comexdown trade 2018:2020 -exp

    Download municipality data:
        $ comexdown trade 2020 -mun

    Download all auxiliary tables:
        $ comexdown table all

    Download specific auxiliary table:
        $ comexdown table ncm
"""


import argparse
from pathlib import Path

from comexdown import get_complete, get_table, get_year, get_year_nbm
from comexdown.constants import AUX_TABLES, TABLES


def expand_years(args_years: str) -> list[int]:
    """Expand year arguments into a list of individual years.

    Processes command-line year arguments which may include individual years
    or year ranges (e.g., "2018:2020") and expands them into a complete list
    of years.

    Parameters
    ----------
    args_years : str
        List of year strings, which can be individual years (e.g., "2020") or
        ranges (e.g., "2018:2020"). Ranges can be ascending or descending.

    Returns
    -------
    list[int]
        Expanded list of years in the order they were specified.

    Examples
    --------
    >>> expand_years(["2020"])
    [2020]
    >>> expand_years(["2018:2020"])
    [2018, 2019, 2020]
    >>> expand_years(["2020:2018"])
    [2020, 2019, 2018]
    >>> expand_years(["2018", "2020:2022"])
    [2018, 2020, 2021, 2022]
    """
    years = []
    for arg in args_years:
        if ":" in arg:
            start, end = arg.split(":")
            start, end = int(start), int(end)
            if start > end:
                years += list(range(start, end - 1, -1))
            else:
                years += list(range(start, end + 1))
        else:
            years.append(int(arg))
    return years


# =============================================================================
# ----------------------------TRANSACTION TRADE DATA---------------------------
# =============================================================================
def download_trade(args: argparse.Namespace):
    """Download trade transaction data based on command-line arguments.

    Handles the download of Brazil's foreign trade data for specified years.
    Supports downloading exports, imports, and municipality-level data for both
    modern NCM classification (1997+) and older NBM classification (1989-1996).

    Parameters
    ----------
    args : argparse.Namespace
        Command-line arguments containing:
        - years: List of years or year ranges to download
        - exp: Flag to download export data only
        - imp: Flag to download import data only
        - mun: Flag to download municipality-level data
        - path: Output directory path for downloaded files

    Notes
    -----
    - If neither exp nor imp flags are set, both are downloaded
    - Years before 1989 are not available
    - Years 1989-1996 use NBM classification (municipality data not available)
    - Years 1997+ use NCM classification
    - Special year value "complete" downloads complete historical datasets
    """
    if not args.exp and not args.imp:
        exp = imp = True
    else:
        exp, imp = args.exp, args.imp

    mun = args.mun

    if args.years == ["complete"]:
        get_complete(
            exp=exp,
            imp=imp,
            mun=mun,
            path=args.path,
        )
        return

    for year in expand_years(args.years):
        if year < 1989:
            print("Year not available!", year)
            continue
        if year < 1997:
            if mun:
                print(
                    f"Municipality data for this year ({year}) not available!"
                    "\nDownloading national data instead..."
                )
            get_year_nbm(
                year=year,
                exp=exp,
                imp=imp,
                path=args.path,
            )
        else:
            get_year(
                year=year,
                exp=exp,
                imp=imp,
                mun=mun,
                path=args.path,
            )


# =============================================================================
# ----------------------------AUXILIARY CODE TABLES----------------------------
# =============================================================================
def download_tables(args: argparse.Namespace):
    """Download auxiliary code tables based on command-line arguments.

    Handles downloading of various classification and reference tables used
    for interpreting Brazil's foreign trade data, including NCM codes, country
    codes, municipality codes, and various product classifications.

    Parameters
    ----------
    args : argparse.Namespace
        Command-line arguments containing:
        - tables: List of table names to download (or 'all' for all tables)
        - path: Output directory path for downloaded tables

    Notes
    -----
    - If no table names are provided, prints available tables and exits
    - Special value 'all' downloads all available auxiliary tables
    - Tables are saved in an 'auxiliary-tables' subdirectory
    """
    if args.tables == []:
        print_code_tables()
    if "all" in args.tables:
        for table in AUX_TABLES:
            get_table(
                table=table,
                path=args.path,
            )
        return
    for table in args.tables:
        get_table(
            table=table,
            path=args.path,
        )


def print_code_tables():
    """Print formatted list of all available auxiliary code tables.

    Displays a formatted list of all auxiliary tables available for download,
    including their short names, full names, and descriptions. Long descriptions
    are word-wrapped to fit within 70 characters per line.

    Notes
    -----
    This function is called when the user runs 'comexdown table' without
    specifying any table names, serving as a help/reference guide.
    """
    print("\nAvailable code tables:")
    for table in TABLES:
        print(f"\n  {table: <11}{TABLES[table]['name']}")
        description = TABLES[table]["description"]
        len_description = len(description)
        i = 0
        if len_description > 70:
            print(13 * " ", end="")
            for word in description.split(" "):
                i += len(word) + 1
                if i < 70:
                    print(word, end=" ")
                else:
                    print(word)
                    print(13 * " ", end="")
                    i = 0
            print("")
        else:
            print(12 * " ", description)
    print("")


def download_help(args: argparse.Namespace):
    """Print CLI help message.

    Parameters
    ----------
    args : argparse.Namespace
        Unused, but required by argparse callback interface.
    """
    print(__doc__)


# =============================================================================
# ------------------------------------PARSERS----------------------------------
# =============================================================================
def set_download_trade_subparser(
    download_subs: argparse.ArgumentParser,
    default_output: Path,
):
    """Configure the 'trade' subcommand parser.

    Sets up the argument parser for downloading trade transaction data,
    including all supported flags and options.

    Parameters
    ----------
    download_subs : argparse.ArgumentParser
        Subparser collection to add the trade subcommand to.
    default_output : Path
        Default output directory path for downloaded files.

    Notes
    -----
    Configures the following arguments:
    - years: Required positional argument for years to download
    - -exp: Optional flag to download only exports
    - -imp: Optional flag to download only imports
    - -mun: Optional flag to download municipality-level data
    - -nbm: Optional flag for NBM classification data
    - -o: Optional output path argument
    """
    # !!! DOWNLOAD TRADE TRANSACTIONS DATA
    download_trade_parser = download_subs.add_parser(
        "trade", description="Download Exports & Imports data")
    download_trade_parser.add_argument(
        "years",
        action="store",
        nargs="+",
        help="Year (or year range) or list of years (year ranges) to download",
    )
    download_trade_parser.add_argument("-exp", action="store_true")
    download_trade_parser.add_argument("-imp", action="store_true")
    download_trade_parser.add_argument("-mun", action="store_true")
    download_trade_parser.add_argument("-nbm", action="store_true")
    download_trade_parser.add_argument(
        "-o",
        action="store",
        dest="path",
        type=Path,
        default=default_output,
        help="Output path directory where files will be saved",
    )
    download_trade_parser.set_defaults(func=download_trade)


def set_download_table_subparser(
    download_subs: argparse.ArgumentParser,
    default_output: Path,
):
    """Configure the 'table' subcommand parser.

    Sets up the argument parser for downloading auxiliary code tables.

    Parameters
    ----------
    download_subs : argparse.ArgumentParser
        Subparser collection to add the table subcommand to.
    default_output : Path
        Default output directory path for downloaded tables.

    Notes
    -----
    Configures the following arguments:
    - tables: Optional list of table names to download
    - -o: Optional output path argument
    """
    # !!! DOWNLOAD CODE TABLES
    download_table_parser = download_subs.add_parser(
        "table", description="Download code tables for Brazil's foreign data")
    download_table_parser.add_argument(
        "tables",
        action="store",
        nargs="*",
        default=[],
        help=(
            "Name (or list of names) of table to download ('all' to download "
            "all tables)"
        ),
    )
    download_table_parser.add_argument(
        "-o",
        action="store",
        dest="path",
        type=Path,
        default=default_output,
        help="Output path directory where files will be saved",
    )
    download_table_parser.set_defaults(func=download_tables)


def set_parser() -> argparse.ArgumentParser:
    """Create and configure the main argument parser.

    Builds the complete command-line argument parser with all subcommands
    and their respective options.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser ready to parse command-line arguments.

    Notes
    -----
    Sets up two subcommands:
    - trade: For downloading trade transaction data
    - table: For downloading auxiliary code tables
    Default output path is './data/secex-comex'
    """
    default_output = Path(".", "data", "secex-comex")

    parser = argparse.ArgumentParser(
        description="Download Brazil's foreign trade data")
    parser.set_defaults(func=download_help)

    subparsers = parser.add_subparsers()

    set_download_trade_subparser(subparsers, default_output)
    set_download_table_subparser(subparsers, default_output)

    return parser


def main():
    """Main entry point for the comexdown CLI tool.

    Parses command-line arguments and dispatches to the appropriate
    download function based on the subcommand provided.

    Notes
    -----
    This function is called when the module is executed as a script or
    when the 'comexdown' command is run from the command line.
    """
    parser = set_parser()
    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as ki:
        print(f"\n\n{ki}\n\n")
        print("\n\n\nEXITING...\n\n\n")
