import click


@click.group()
@click.version_option()
def main() -> None:
    """ff — dynamically generate and execute agentic graphs."""


@main.command()
def generate() -> None:
    """Generate a new graph."""
    click.echo("ff generate: not yet implemented")


@main.command()
def validate() -> None:
    """Validate a graph."""
    click.echo("ff validate: not yet implemented")


@main.command(name="list")
def list_flows() -> None:
    """List available graphs."""
    click.echo("ff list: not yet implemented")


@main.command()
def run() -> None:
    """Run a graph."""
    click.echo("ff run: not yet implemented")


if __name__ == "__main__":
    main()
