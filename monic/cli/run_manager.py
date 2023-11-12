import click
from rich.console import Console
from rich.table import Table
from monic.bootstrap import build_app
from monic.cli.utils import adapt
from monic.core.monitor import Monitor


@click.command()
def run_manager():
    """Starts the manager process."""
    app = build_app()
    adapt(lambda: app.run_manager())
    app.shutdown()
