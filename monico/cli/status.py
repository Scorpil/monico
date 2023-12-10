import click
from click import IntRange
import time
from rich.markup import escape
from rich.console import Console
from rich.table import Table
from monico.bootstrap import AppContext
from monico.cli.utils import adapt_exceptions_for_cli
from monico.utils import (
    timestamp_to_human_readable_string,
    seconds_to_human_readable_string,
)
from rich.live import Live


def monitor_header_table(monitor):
    table = Table(show_edge=False, show_header=False, show_lines=False, box=None)
    table.add_column("Header", style="bold")
    table.add_column("Value")

    table.add_row("Monitor ID", escape(monitor.id))
    table.add_row("Name", escape(monitor.name))
    table.add_row("Endpoint", escape(monitor.endpoint))
    table.add_row(
        "Body Regexp",
        "None" if monitor.body_regexp is None else escape(monitor.body_regexp),
    )
    table.add_row(
        "Interval", escape(seconds_to_human_readable_string(monitor.interval))
    )
    return table


def status_table(monitor, probes):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Time")
    table.add_column("Response Time")
    table.add_column("Response Code", justify="right")
    table.add_column("Response Error")
    table.add_column("Content Match")

    for probe in reversed(probes):
        table.add_row(
            timestamp_to_human_readable_string(probe.timestamp),
            seconds_to_human_readable_string(probe.response_time),
            f"{probe.response_code}",
            probe.response_error,
            probe.content_match,
        )
    return table


@click.command()
@click.option("--id", prompt="Monitor ID", help="ID of the monitor")
@click.option("-l", "--live", is_flag=True, help="Live output")
@click.option(
    "-n",
    "--number-of-probes",
    default=10,
    help="Number of probes to display",
    type=IntRange(min=1, max=100),
)
@adapt_exceptions_for_cli
def status(id, live, number_of_probes):
    """Displays status of a monitor"""
    with AppContext.create() as app:
        if live:
            status_live(app, id, number_of_probes)
        else:
            status_static(app, id, number_of_probes)
    app.shutdown()


def status_static(app, monitor_id, number_of_probes):
    """Displays status of a monitor as a single static output"""
    monitor, probes = app.status(monitor_id, limit_probes=number_of_probes)
    console = Console()
    console.print(monitor_header_table(monitor))

    console.print(f"\nLast {number_of_probes} probes:", style="bold")
    console.print(status_table(monitor, probes))


def status_live(app, monitor_id, number_of_probes):
    """Displays status of a monitor as a live output"""
    console = Console()
    console.print("Press Ctrl+C to exit\n")

    monitor, probes = app.status(monitor_id, limit_probes=number_of_probes)
    console.print(monitor_header_table(monitor))

    console.print(f"\nLast {number_of_probes} probes:", style="bold")
    with Live(status_table(monitor, probes)) as live:
        while True:
            monitor, probes = app.status(monitor_id, limit_probes=number_of_probes)
            live.update(status_table(monitor, probes))
            time.sleep(1)
