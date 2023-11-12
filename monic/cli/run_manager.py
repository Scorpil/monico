import click
from monic.bootstrap import build_app
from monic.cli.utils import adapt


@click.command()
def run_manager():
    """Starts the manager process."""
    app = build_app()
    adapt(lambda: app.run_manager())
    app.shutdown()
