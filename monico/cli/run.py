import click
from typing import Optional
from monico.bootstrap import AppContext
from monico.cli.utils import adapt_exceptions_for_cli


@click.command()
@click.option("-w", "--worker-id", help="Worker ID", default=None, type=str)
@adapt_exceptions_for_cli
def run(worker_id: Optional[str]):
    """Starts both manager and worker processes concurrently."""
    with AppContext.create() as app:
        app.run(worker_id=worker_id)
