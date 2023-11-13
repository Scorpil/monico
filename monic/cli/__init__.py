import click
from monic.cli.setup import setup
from monic.cli.create import create
from monic.cli.list import list_monitors
from monic.cli.status import status
from monic.cli.delete import delete
from monic.cli.run_manager import run_manager
from monic.cli.run_worker import run_worker


@click.group()
def cli():
    pass


cli.add_command(setup)
cli.add_command(create)
cli.add_command(list_monitors)
cli.add_command(status)
cli.add_command(delete)

cli.add_command(run_manager)
cli.add_command(run_worker)
