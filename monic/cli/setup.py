import click
from monic.bootstrap import build_app
from monic.cli.utils import adapt


@click.command()
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    help="Force reinitialization. DANGER: DESTROYS ALL DATA!",
)
def setup(force=False):
    """Initializes the database"""
    app = build_app()
    adapt(lambda: app.setup(force=force))
    app.shutdown()
    click.echo("Initialized the database")
