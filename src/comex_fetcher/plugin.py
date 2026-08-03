"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
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
from quantilica.core.http import ProgressCallback
from rich.console import Group
from rich.live import Live
from rich.progress import Progress, TaskID
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


def _file_callback(
    file_progress: Progress,
    task_id: TaskID,
    description: str,
) -> ProgressCallback:
    """Return a ProgressCallback that feeds into a Rich file progress task."""

    def callback(downloaded: int, total_bytes: int) -> None:
        # (0, 0) fires at the start of each download attempt (incl. retries)
        if downloaded == 0 and total_bytes == 0:
            file_progress.reset(task_id)
            file_progress.update(task_id, description=description, visible=True)
            return
        if total_bytes:
            file_progress.update(task_id, total=total_bytes)
        file_progress.update(task_id, completed=downloaded)

    return callback


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
        file_task = file_prog.add_task("", total=None, visible=False)

        ok = 0
        with Live(Group(overall, file_prog), console=console, refresh_per_second=10):
            if do_trade:
                for year in years_list:
                    if year < 1997:
                        overall.update(
                            overall_task, description=f"[cyan]NBM {year}[/cyan]"
                        )
                        cb = _file_callback(file_prog, file_task, f"NBM {year}")
                        get_year_nbm(
                            data_dir=output,
                            year=year,
                            exp=exp,
                            imp=imp,
                            progress=cb,
                        )
                        file_prog.update(file_task, visible=False)
                        adv = (1 if exp else 0) + (1 if imp else 0)
                        ok += adv
                        overall.update(
                            overall_task,
                            advance=adv,
                            description=f"[green]{ok}✓[/green]",
                        )
                    else:
                        overall.update(overall_task, description=f"[cyan]{year}[/cyan]")
                        cb = _file_callback(file_prog, file_task, str(year))
                        get_year(
                            data_dir=output,
                            year=year,
                            exp=exp,
                            imp=imp,
                            mun=municipality,
                            progress=cb,
                        )
                        file_prog.update(file_task, visible=False)
                        adv = ((1 if exp else 0) + (1 if imp else 0)) * (
                            2 if municipality else 1
                        )
                        ok += adv
                        overall.update(
                            overall_task,
                            advance=adv,
                            description=f"[green]{ok}✓[/green]",
                        )

            if do_tables:
                for name in table_names:
                    overall.update(overall_task, description=f"[cyan]{name}[/cyan]")
                    cb = _file_callback(file_prog, file_task, name)
                    get_table(data_dir=output, table=name, progress=cb)
                    file_prog.update(file_task, visible=False)
                    ok += 1
                    overall.update(
                        overall_task,
                        advance=1,
                        description=f"[green]{ok}✓[/green]",
                    )

            if do_repetro:
                repo = storage.DataRepository(output)
                for name in REPETRO_TABLES:
                    overall.update(overall_task, description=f"[cyan]{name}[/cyan]")
                    cb = _file_callback(file_prog, file_task, name)
                    url = urls.get_url(name)
                    date = download._safe_head_date(url)
                    dest = repo.path_repetro(name, last_modified=date)
                    download.download_file(url, dest, progress=cb)
                    file_prog.update(file_task, visible=False)
                    ok += 1
                    overall.update(
                        overall_task,
                        advance=1,
                        description=f"[green]{ok}✓[/green]",
                    )

            if do_validation:
                repo = storage.DataRepository(output)
                for name in TOTAIS_PARA_VALIDACAO:
                    overall.update(overall_task, description=f"[cyan]{name}[/cyan]")
                    cb = _file_callback(file_prog, file_task, name)
                    url = urls.get_url(name)
                    date = download._safe_head_date(url)
                    dest = repo.path_validacao(name, last_modified=date)
                    download.download_file(url, dest, progress=cb)
                    file_prog.update(file_task, visible=False)
                    ok += 1
                    overall.update(
                        overall_task,
                        advance=1,
                        description=f"[green]{ok}✓[/green]",
                    )

            if do_other:
                repo = storage.DataRepository(output)
                name = "tabelas-auxiliares"
                overall.update(overall_task, description=f"[cyan]{name}[/cyan]")
                cb = _file_callback(file_prog, file_task, name)
                url = urls.get_url(name)
                date = download._safe_head_date(url)
                dest = repo.path_other(name, "xlsx", last_modified=date)
                download.download_file(url, dest, progress=cb)
                file_prog.update(file_task, visible=False)
                ok += 1
                overall.update(
                    overall_task,
                    advance=1,
                    description=f"[green]{ok}✓[/green]",
                )

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
