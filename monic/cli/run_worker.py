import click
from typing import Optional
from monic.bootstrap import build_app
from monic.cli.utils import adapt


@click.command()
@click.option("--id", help="Worker ID", default=None, type=str)
def run_worker(id: Optional[str]):
    """Starts the manager process."""
    app = build_app()
    adapt(lambda: app.run_worker(worker_id=id))
    app.shutdown()
