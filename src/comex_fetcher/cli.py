#!/usr/bin/env python3

"""Command-line interface for downloading Brazil's foreign trade data.

This tool provides access to trade transaction data and auxiliary code tables
from Brazil's Ministry of Economy (SECEX/COMEX).
"""

import argparse
import concurrent.futures
import datetime as dt
import logging
import sys
from pathlib import Path

from quantilica.core.dates import expand_year_range
from quantilica.core.logging import configure_cli_logging

from comex_fetcher import (
    __version__,
    get_other_tables,
    get_repetro,
    get_table,
    get_validation,
    get_year,
    get_year_nbm,
    logger,
)
from comex_fetcher.constants import (
    AUX_TABLES,
    REPETRO_TABLES,
    TABLES,
    TOTAIS_PARA_VALIDACAO,
)

_DEFAULT_OUTPUT = Path("/data/secex-comex")
_MIN_YEAR = 1989


def expand_years(args_years: list[str]) -> list[int]:
    """Expand year arguments into a list of individual years."""
    years: list[int] = []
    for arg in args_years:
        try:
            years.extend(expand_year_range(arg))
        except ValueError:
            print(f"Error: Invalid year or range '{arg}'")
    return years


def handle_sync(args: argparse.Namespace):
    """Handle the 'sync' subcommand."""
    show_progress = not args.verbose
    if not args.exp and not args.imp:
        exp = imp = True
    else:
        exp, imp = args.exp, args.imp

    if args.years:
        years = [y for y in expand_years(args.years) if y >= _MIN_YEAR]
    else:
        years = list(range(_MIN_YEAR, dt.datetime.now().year + 1))

    do_trade = not args.tables_only
    do_tables = not args.no_tables
    do_repetro = args.repetro and not args.tables_only
    do_validation = args.validation and not args.tables_only
    do_other = args.other_tables and not args.no_tables
    table_names = list(AUX_TABLES.keys())

    if args.dry_run:
        n = 0
        if do_trade:
            for year in years:
                if year < 1997:
                    if exp:
                        print(f"transações exp-nbm {year}")
                        n += 1
                    if imp:
                        print(f"transações imp-nbm {year}")
                        n += 1
                else:
                    if exp:
                        print(f"transações exp     {year}")
                        n += 1
                    if imp:
                        print(f"transações imp     {year}")
                        n += 1
                    if args.mun:
                        if exp:
                            print(f"transações exp-mun {year}")
                            n += 1
                        if imp:
                            print(f"transações imp-mun {year}")
                            n += 1
        if do_tables:
            for name in table_names:
                print(f"tabela      {name}")
                n += 1
        if do_repetro:
            for name in REPETRO_TABLES:
                print(f"repetro     {name}")
                n += 1
        if do_validation:
            for name in TOTAIS_PARA_VALIDACAO:
                print(f"validacao   {name}")
                n += 1
        if do_other:
            print("outros      tabelas-auxiliares")
            n += 1
        print(f"Total: {n} item(ns)")
        return

    tasks = []

    if do_trade:
        for year in years:
            if year < 1997:
                tasks.append(
                    (
                        get_year_nbm,
                        {
                            "data_dir": args.output,
                            "year": year,
                            "exp": exp,
                            "imp": imp,
                            "show_progress": show_progress,
                        },
                    )
                )
            else:
                tasks.append(
                    (
                        get_year,
                        {
                            "data_dir": args.output,
                            "year": year,
                            "exp": exp,
                            "imp": imp,
                            "mun": args.mun,
                            "show_progress": show_progress,
                        },
                    )
                )

    if do_tables:
        for table in table_names:
            tasks.append(
                (
                    get_table,
                    {
                        "data_dir": args.output,
                        "table": table,
                        "show_progress": show_progress,
                    },
                )
            )

    if do_repetro:
        tasks.append(
            (
                get_repetro,
                {
                    "data_dir": args.output,
                    "show_progress": show_progress,
                },
            )
        )

    if do_validation:
        tasks.append(
            (
                get_validation,
                {
                    "data_dir": args.output,
                    "show_progress": show_progress,
                },
            )
        )

    if do_other:
        tasks.append(
            (
                get_other_tables,
                {
                    "data_dir": args.output,
                    "show_progress": show_progress,
                },
            )
        )

    def run_cli_task(func, kwargs):
        try:
            func(**kwargs)
        except Exception as e:
            logger.error(f"Error running task: {e}")

    workers = getattr(args, "workers", 4)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(run_cli_task, func, kwargs) for func, kwargs in tasks
        ]
        concurrent.futures.wait(futures)


def handle_list(args: argparse.Namespace):
    """Handle the 'list' subcommand."""
    print("\nAvailable code tables:")
    for table, info in TABLES.items():
        print(f"\n  {table: <11} {info['name']}")
        desc = info["description"]
        words = desc.split()
        line = " " * 13
        for word in words:
            if len(line) + len(word) > 80:
                print(line)
                line = " " * 13 + word
            else:
                line += " " + word
        print(line)
    print()


def get_parser() -> argparse.ArgumentParser:
    """Create and configure the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="comex-fetcher",
        description="Download Brazil's foreign trade data (SECEX/COMEX).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Exibir logs detalhados em vez de barra de progresso",
    )
    parser.set_defaults(func=lambda _: parser.print_help())

    subparsers = parser.add_subparsers(title="commands", dest="command")

    # sync
    sync_parser = subparsers.add_parser(
        "sync",
        help="Sincronizar dados de comércio exterior (transações + tabelas)",
    )
    sync_parser.add_argument(
        "years",
        nargs="*",
        help=(
            "Anos (ex: 2020) ou intervalos (2018:2020)."
            f" Padrão: todos desde {_MIN_YEAR}."
        ),
    )
    sync_parser.add_argument(
        "-exp", "--exports", action="store_true", help="Apenas exportações"
    )
    sync_parser.add_argument(
        "-imp", "--imports", action="store_true", help="Apenas importações"
    )
    sync_parser.add_argument(
        "-mun",
        "--municipality",
        action="store_true",
        dest="municipality",
        default=True,
        help="Dados municipais (1997+)",
    )
    sync_parser.add_argument(
        "--no-municipality",
        action="store_false",
        dest="municipality",
        help="Não baixar dados municipais",
    )
    sync_parser.add_argument(
        "--no-tables",
        action="store_true",
        help="Não baixar as tabelas auxiliares de códigos",
    )
    sync_parser.add_argument(
        "--repetro",
        action="store_true",
        dest="repetro",
        default=True,
        help="Baixar dados do REPETRO",
    )
    sync_parser.add_argument(
        "--no-repetro",
        action="store_false",
        dest="repetro",
        help="Não baixar dados do REPETRO",
    )
    sync_parser.add_argument(
        "--validation",
        action="store_true",
        dest="validation",
        default=True,
        help="Baixar totais para validação",
    )
    sync_parser.add_argument(
        "--no-validation",
        action="store_false",
        dest="validation",
        help="Não baixar totais para validação",
    )
    sync_parser.add_argument(
        "--other-tables",
        action="store_true",
        dest="other_tables",
        default=True,
        help="Baixar outras tabelas (tabelas auxiliares em Excel)",
    )
    sync_parser.add_argument(
        "--no-other-tables",
        action="store_false",
        dest="other_tables",
        help="Não baixar outras tabelas em Excel",
    )
    sync_parser.add_argument(
        "--tables-only",
        action="store_true",
        help="Baixar apenas as tabelas auxiliares",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Listar sem baixar",
    )
    sync_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Downloads paralelos",
    )
    sync_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help="Diretório de saída",
    )
    sync_parser.set_defaults(func=handle_sync)

    # list
    list_parser = subparsers.add_parser(
        "list", help="Listar tabelas auxiliares de códigos disponíveis"
    )
    list_parser.set_defaults(func=handle_list)

    return parser


def main(argv: list[str] | None = None) -> None:
    """Main entry point."""
    parser = get_parser()
    args = parser.parse_args(argv)
    configure_cli_logging(verbose=args.verbose)
    if not args.verbose:
        logging.getLogger("quantilica.core").setLevel(logging.WARNING)
        logging.getLogger("comex_fetcher").setLevel(logging.WARNING)

    # argparse stores the dest as 'exports'/'imports'; expose short aliases.
    args.exp = getattr(args, "exports", False)
    args.imp = getattr(args, "imports", False)
    args.mun = getattr(args, "municipality", True)
    args.repetro = getattr(args, "repetro", True)
    args.validation = getattr(args, "validation", True)
    args.other_tables = getattr(args, "other_tables", True)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
