import click
from monic.cli.add import add
from monic.cli.setup import setup


@click.group()
def cli():
    pass


cli.add_command(add)
cli.add_command(setup)
