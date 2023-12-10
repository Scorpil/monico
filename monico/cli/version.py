import click


@click.command()
def version():
    """Prints the version"""
    click.echo("0.1.0-dev")
