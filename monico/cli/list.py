import click
from rich.markup import escape
from rich.console import Console
from rich.table import Table
from monico.bootstrap import AppContext
from monico.cli.utils import adapt_exceptions_for_cli
from monico.core.monitor import Monitor
from monico.utils import seconds_to_human_readable_string


def print_monitors(monitors: [Monitor]):
    """Prints a list of monitors"""
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Endpoint")
    table.add_column("Interval")
    for monitor in monitors:
        table.add_row(
            escape(monitor.id),
            escape(monitor.name),
            escape(monitor.endpoint),
            escape(seconds_to_human_readable_string(monitor.interval)),
        )
    console.print(table)


@click.command(name="list")
@adapt_exceptions_for_cli
def list_monitors():  # `list` is a reserved keyword in Python
    """Lists configured monitors."""
    with AppContext.create() as app:
        monitors = app.list_monitors()
    print_monitors(monitors)
