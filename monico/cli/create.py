import click
from monico.bootstrap import AppContext
from monico.cli.utils import adapt_exceptions_for_cli


@click.command()
@click.option("--id", help="ID of the monitor", default=None)
@click.option("--name", prompt="Monitor name", help="Name of the monitor")
@click.option("--endpoint", prompt="Endpoint URL", help="URL to monitor")
@click.option("--interval", default=60, help="Monitoring interval in seconds")
@click.option(
    "--body-regexp",
    help="Regular expression to match in the response body",
    default=None,
)
@adapt_exceptions_for_cli
def create(id, name, endpoint, interval, body_regexp):
    """Creates a new monitor"""
    with AppContext.create() as app:
        monitor = app.create_monitor(id, name, endpoint, interval, body_regexp)
    click.echo(
        f'Added monitor {monitor.name} for "{monitor.endpoint}" every {monitor.interval} seconds'
    )
