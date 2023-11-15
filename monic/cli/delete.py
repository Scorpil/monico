import click
from monic.bootstrap import AppContext
from monic.cli.utils import adapt_exceptions_for_cli
from monic.core.monitor import Monitor


@click.command()
@click.option("--id", help="ID of the monitor", default=None)
@adapt_exceptions_for_cli
def delete(id):
    """Deletes a monitor."""
    with AppContext.create() as app:
        monitors = app.delete_monitor(id)
    click.echo(f"Removed monitor {id}")
