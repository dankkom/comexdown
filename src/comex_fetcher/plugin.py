"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer
from quantilica.core.cli import (
    expand_years_cli,
    get_console,
    make_batch_progress,
    make_download_progress,
    setup_rich_logging,
)
from rich.console import Group
from rich.live import Live
from rich.table import Table

from comex_fetcher import (
    download,
    get_table,
    get_year,
    get_year_nbm,
    storage,
    urls,
)
from comex_fetcher.constants import (
    AUX_TABLES,
    REPETRO_TABLES,
    TOTAIS_PARA_VALIDACAO,
)

app = typer.Typer(help="Dados de comércio exterior (SECEX/COMEX).")
console = get_console()

_DEFAULT_OUTPUT = Path("/data/secex-comex")
_MIN_YEAR = 1989


@app.command("sync")
def sync(
    years: Annotated[
        list[str] | None,
        typer.Argument(
            help=(
                "Anos (ex: 2020) ou intervalos (2018:2020)."
                f" Padrão: todos desde {_MIN_YEAR}."
            ),
        ),
    ] = None,
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de saída")
    ] = _DEFAULT_OUTPUT,
    exports: Annotated[
        bool,
        typer.Option("--exports/--no-exports", help="Apenas exportações"),
    ] = False,
    imports: Annotated[
        bool,
        typer.Option("--imports/--no-imports", help="Apenas importações"),
    ] = False,
    municipality: Annotated[
        bool,
        typer.Option(
            "--municipality/--no-municipality",
            "-mun/-no-mun",
            help="Dados municipais (1997+)",
        ),
    ] = True,
    no_tables: Annotated[
        bool,
        typer.Option("--no-tables", help="Não baixar as tabelas auxiliares de códigos"),
    ] = False,
    tables_only: Annotated[
        bool,
        typer.Option("--tables-only", help="Baixar apenas as tabelas auxiliares"),
    ] = False,
    repetro: Annotated[
        bool,
        typer.Option("--repetro/--no-repetro", help="Baixar dados do REPETRO"),
    ] = True,
    validation: Annotated[
        bool,
        typer.Option(
            "--validation/--no-validation",
            help="Baixar totais para validação",
        ),
    ] = True,
    other_tables: Annotated[
        bool,
        typer.Option(
            "--other-tables/--no-other-tables",
            help="Baixar outras tabelas (tabelas auxiliares em Excel)",
        ),
    ] = True,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Listar sem baixar")
    ] = False,
    workers: Annotated[int, typer.Option("--workers", help="Downloads paralelos")] = 4,
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Sincronizar dados de comércio exterior (transações + tabelas)."""
    setup_rich_logging(verbose, console=console)
    exp = imp = True
    if exports or imports:
        exp, imp = exports, imports

    current_year = dt.datetime.now().year
    if years:
        years_list = [
            y for y in expand_years_cli(years, console=console) if y >= _MIN_YEAR
        ]
    else:
        years_list = list(range(_MIN_YEAR, current_year + 1))

    if not tables_only and not years_list:
        console.print("[yellow]Nenhum ano válido informado.[/yellow]")
        raise typer.Exit(code=1)

    do_trade = not tables_only
    do_tables = not no_tables
    do_repetro = repetro and not tables_only
    do_validation = validation and not tables_only
    do_other = other_tables and not no_tables
    table_names = list(AUX_TABLES.keys())

    trade_count = 0
    if do_trade:
        for year in years_list:
            if year < 1997:
                trade_count += (1 if exp else 0) + (1 if imp else 0)
            else:
                base = (1 if exp else 0) + (1 if imp else 0)
                trade_count += base * 2 if municipality else base

    total = (
        trade_count
        + (len(table_names) if do_tables else 0)
        + (len(REPETRO_TABLES) if do_repetro else 0)
        + (len(TOTAIS_PARA_VALIDACAO) if do_validation else 0)
        + (1 if do_other else 0)
    )

    if dry_run:
        t = Table(show_header=True, header_style="bold")
        t.add_column("Tipo", style="cyan")
        t.add_column("Item")
        if do_trade:
            for year in years_list:
                if year < 1997:
                    if exp:
                        t.add_row("transações exp-nbm", str(year))
                    if imp:
                        t.add_row("transações imp-nbm", str(year))
                else:
                    if exp:
                        t.add_row("transações exp", str(year))
                    if imp:
                        t.add_row("transações imp", str(year))
                    if municipality:
                        if exp:
                            t.add_row("transações exp-mun", str(year))
                        if imp:
                            t.add_row("transações imp-mun", str(year))
        if do_tables:
            for name in table_names:
                t.add_row("tabela", name)
        if do_repetro:
            for name in REPETRO_TABLES:
                t.add_row("repetro", name)
        if do_validation:
            for name in TOTAIS_PARA_VALIDACAO:
                t.add_row("validacao", name)
        if do_other:
            t.add_row("outros", "tabelas-auxiliares")
        console.print(t)
        console.print(f"[bold]Total:[/bold] {total} item(ns)")
        return

    try:
        overall = make_batch_progress(console)
        file_prog = make_download_progress(console)
        overall_task = overall.add_task("[cyan]Iniciando...[/cyan]", total=total)

        tasks: list[tuple[str, Callable, dict, int]] = []

        if do_trade:
            for year in years_list:
                if year < 1997:
                    adv = (1 if exp else 0) + (1 if imp else 0)
                    tasks.append(
                        (
                            f"NBM {year}",
                            get_year_nbm,
                            {"data_dir": output, "year": year, "exp": exp, "imp": imp},
                            adv,
                        )
                    )
                else:
                    adv = ((1 if exp else 0) + (1 if imp else 0)) * (
                        2 if municipality else 1
                    )
                    tasks.append(
                        (
                            str(year),
                            get_year,
                            {
                                "data_dir": output,
                                "year": year,
                                "exp": exp,
                                "imp": imp,
                                "mun": municipality,
                            },
                            adv,
                        )
                    )

        if do_tables:
            for name in table_names:
                tasks.append((name, get_table, {"data_dir": output, "table": name}, 1))

        if do_repetro:
            for name in REPETRO_TABLES:

                def _dl_repetro(name=name, data_dir=output, progress=None):
                    repo = storage.DataRepository(data_dir)
                    url = urls.get_url(name)
                    date = download._safe_head_date(url)
                    dest = repo.path_repetro(name, last_modified=date)
                    download.download_file(url, dest, progress=progress)

                tasks.append((name, _dl_repetro, {}, 1))

        if do_validation:
            for name in TOTAIS_PARA_VALIDACAO:

                def _dl_validation(name=name, data_dir=output, progress=None):
                    repo = storage.DataRepository(data_dir)
                    url = urls.get_url(name)
                    date = download._safe_head_date(url)
                    dest = repo.path_validacao(name, last_modified=date)
                    download.download_file(url, dest, progress=progress)

                tasks.append((name, _dl_validation, {}, 1))

        if do_other:
            name_other = "tabelas-auxiliares"

            def _dl_other(name=name_other, data_dir=output, progress=None):
                repo = storage.DataRepository(data_dir)
                url = urls.get_url(name)
                date = download._safe_head_date(url)
                dest = repo.path_other(name, "xlsx", last_modified=date)
                download.download_file(url, dest, progress=progress)

            tasks.append((name_other, _dl_other, {}, 1))

        ok = 0
        lock = threading.Lock()

        worker_task_ids = [
            file_prog.add_task("[dim]Inativo[/dim]", total=1) for _ in range(workers)
        ]
        available_tasks = worker_task_ids.copy()

        def run_task(desc: str, func: Callable, kwargs: dict, adv: int) -> int:
            with lock:
                task_id = available_tasks.pop(0)

            def cb(downloaded: int, total_bytes: int) -> None:
                if downloaded == 0 and total_bytes == 0:
                    file_prog.update(task_id, completed=0)
                    return
                file_prog.update(
                    task_id,
                    description=f"[cyan]{desc}[/cyan]",
                    completed=downloaded,
                    total=total_bytes or None,
                )

            try:
                func(**kwargs, progress=cb)
                return adv
            finally:
                with lock:
                    file_prog.update(
                        task_id, description="[dim]Inativo[/dim]", completed=0, total=1
                    )
                    available_tasks.append(task_id)

        with Live(Group(overall, file_prog), console=console, refresh_per_second=10):
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_task = {
                    executor.submit(run_task, desc, func, kwargs, adv): (desc, adv)
                    for desc, func, kwargs, adv in tasks
                }
                for future in concurrent.futures.as_completed(future_to_task):
                    desc, adv = future_to_task[future]
                    try:
                        future.result()
                        with lock:
                            ok += adv
                            overall.update(
                                overall_task,
                                advance=adv,
                                description=f"[green]{ok}✓[/green]",
                            )
                    except Exception:
                        # Log the exception or handle it
                        pass

        console.print(
            f"[green]✓[/green] [bold]{ok}[/bold]"
            f" item(ns) sincronizados em [dim]{output}[/dim]"
        )
    except KeyboardInterrupt:
        console.print("[yellow]Download cancelado pelo usuário.[/yellow]")
        raise typer.Exit(code=130) from None


@app.command("list")
def list_cmd(
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Listar as tabelas auxiliares de códigos disponíveis."""
    setup_rich_logging(verbose, console=console)
    rich_table = Table(title="Tabelas auxiliares disponíveis", show_header=True)
    rich_table.add_column("Nome", style="cyan")
    for name in AUX_TABLES:
        rich_table.add_row(name)
    console.print(rich_table)
