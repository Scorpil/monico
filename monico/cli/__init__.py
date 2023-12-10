import click
from monico.cli.setup import setup
from monico.cli.create import create
from monico.cli.list import list_monitors
from monico.cli.status import status
from monico.cli.delete import delete
from monico.cli.run_manager import run_manager
from monico.cli.run_worker import run_worker
from monico.cli.run import run
from monico.cli.version import version


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
cli.add_command(run)
cli.add_command(version)
