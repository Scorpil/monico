import click
from monico.bootstrap import AppContext
from monico.cli.utils import adapt_exceptions_for_cli


@click.command(name="setup")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    help="Force reinitialization. DANGER: DESTROYS ALL DATA!",
)
@adapt_exceptions_for_cli
def setup(force=False):
    """Initializes the database"""
    with AppContext.create() as app:
        app.setup(force=force)
    click.echo("Initialized the database")
