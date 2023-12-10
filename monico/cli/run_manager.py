import click
from monico.bootstrap import AppContext
from monico.cli.utils import adapt_exceptions_for_cli


@click.command()
@adapt_exceptions_for_cli
def run_manager():
    """Starts the manager process."""
    with AppContext.create() as app:
        app.run_manager()
