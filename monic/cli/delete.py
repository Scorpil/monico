import click
from monic.bootstrap import build_app
from monic.cli.utils import adapt
from monic.core.monitor import Monitor


@click.command()
@click.option("--id", help="ID of the monitor", default=None)
def delete(id):
    """Lists configured monitors."""
    app = build_app()
    monitors = adapt(lambda: app.delete_monitor(id))
    app.shutdown()
    click.echo(f"Removed monitor {id}")
