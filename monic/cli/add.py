import click
from monic.bootstrap import build_app
from monic.cli.utils import adapt


@click.command()
@click.option("--name", prompt="Monitor name", help="Name of the monitor")
@click.option("--endpoint", prompt="Endpoint URL", help="URL to monitor")
@click.option("--interval", default=60, help="Monitoring interval in seconds")
def add(name, endpoint, interval):
    """Creates a new monitor"""
    app = build_app()
    monitor = adapt(lambda: app.add_monitor(name, endpoint, interval))
    click.echo(
        f'Added monitor {monitor.name} for "{monitor.endpoint}" every {monitor.interval} seconds'
    )
