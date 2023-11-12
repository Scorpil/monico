import click
from monic.bootstrap import build_app
from monic.cli.utils import adapt


@click.command()
@click.option("--id", help="ID of the monitor", default=None)
@click.option("--name", prompt="Monitor name", help="Name of the monitor")
@click.option("--endpoint", prompt="Endpoint URL", help="URL to monitor")
@click.option("--interval", default=60, help="Monitoring interval in seconds")
def create(id, name, endpoint, interval):
    """Creates a new monitor"""
    app = build_app()
    monitor = adapt(lambda: app.create_monitor(id, name, endpoint, interval))
    app.shutdown()
    click.echo(
        f'Added monitor {monitor.name} for "{monitor.endpoint}" every {monitor.interval} seconds'
    )
