import click
from typing import Optional
from monico.bootstrap import AppContext
from monico.cli.utils import adapt_exceptions_for_cli


@click.command()
@click.option("--id", help="Worker ID", default=None, type=str)
@adapt_exceptions_for_cli
def run_worker(id: Optional[str]):
    """Starts the worker process."""
    with AppContext.create() as app:
        app.run_worker(worker_id=id)
