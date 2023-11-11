import click
from monic.cli.list import list_monitors
from monic.cli.create import create
from monic.cli.setup import setup
from monic.cli.delete import delete


@click.group()
def cli():
    pass


cli.add_command(create)
cli.add_command(setup)
cli.add_command(list_monitors)
cli.add_command(delete)
