import click
from monic.cli.add import add


@click.group()
def cli():
    pass


cli.add_command(add)
