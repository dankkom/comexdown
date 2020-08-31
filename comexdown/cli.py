#!/usr/bin/env python3


import argparse
import os

from comexdown import get_year, get_year_nbm, get_complete, get_table
from comexdown.tables import AUX_TABLES, TABLES
from comexdown.fs import DataDirectory


def expand_years(args_years):
    years = []
    for arg in args_years:
        if ":" in arg:
            start, end = arg.split(":")
            start, end = int(start), int(end)
            if start > end:
                years += list(range(start, end-1, -1))
            else:
                years += list(range(start, end+1))
        else:
            years.append(int(arg))
    return years


# ==============================================================================
# ----------------------------TRANSACTION TRADE DATA----------------------------
# ==============================================================================
def download_trade(args):
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
                    f"Municipality data for this year ({year}) isn't available!"
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


# ==============================================================================
# ------------------------------------INDEX-------------------------------------
# ==============================================================================
def index(args):
    dd = DataDirectory(args.datadir)
    dd.create_index()


# ==============================================================================
# ----------------------------AUXILIARY CODE TABLES-----------------------------
# ==============================================================================
def download_tables(args):
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
    print("\nAvailable code tables:")
    for table in TABLES:
        print(f"\n  {table: <11}{TABLES[table]['name']}")
        description = TABLES[table]["description"]
        len_description = len(description)
        i = 0
        if len_description > 70:
            print(13*" ", end="")
            for word in description.split(" "):
                i += len(word) + 1
                if i < 70:
                    print(word, end=" ")
                else:
                    print(word)
                    print(13*" ", end="")
                    i = 0
            print("")
        else:
            print(12*" ", description)
    print("")


def download_help(args):
    print("\nhelp for sub-command:  comexdown download\n\n"
          "available arguments:\n\n"
          "  trade: download trade data\n"
          "  table: download auxiliary code table\n"
    )


# ==============================================================================
# ------------------------------------PARSERS-----------------------------------
# ==============================================================================
def set_download_trade_subparser(download_subs, default_output):
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
        default=default_output,
        help="Output path directory where files will be saved",
    )
    download_trade_parser.set_defaults(func=download_trade)


def set_download_table_subparser(download_subs, default_output):
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
        default=default_output,
        help="Output path directory where files will be saved",
    )
    download_table_parser.set_defaults(func=download_tables)


def set_index_subparser(command_subparsers):
    index_subparser = command_subparsers.add_parser(
        "index", description="Index data directory.")
    index_subparser.add_argument("datadir", help="Data directory path.")
    index_subparser.set_defaults(func=index)


def set_parser():
    default_output = os.path.join(".", "DATA", "MDIC")

    parser = argparse.ArgumentParser(
        description="Easy access to Brazil's foreign trade data")
    command_subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # * DOWNLOAD DATA
    download_subparser = command_subparsers.add_parser(
        "download",
        description="Download Brazil's foreign trade data",
    )
    download_subparser.set_defaults(func=download_help)
    download_subs = download_subparser.add_subparsers()

    set_download_trade_subparser(download_subs, default_output)
    set_download_table_subparser(download_subs, default_output)

    set_index_subparser(command_subparsers)

    return parser


def main():
    parser = set_parser()
    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as ki:
        print(f"\n\n{ki}\n\n")
        print("\n\n\nEXITING...\n\n\n")
