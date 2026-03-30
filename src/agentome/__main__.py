from pathlib import Path
from typing import Literal

import click

from agentome.server import get_server


@click.command()
@click.option(
    "--artifacts",
    help="The artifact dir to run",
    type=click.Path(exists=True, file_okay=False),
)
@click.option("--host", default="localhost", help="The host to run the server on")
@click.option("--port", default=8000, help="The port to run the server on")
@click.option(
    "--transport",
    default="stdio",
    help="The transport protocol to use (http or stdio)",
    type=click.Choice(["http", "stdio"]),
)
def main(
    artifacts: str,
    host: str,
    port: int,
    transport: Literal["http", "stdio"],
) -> None:

    mcp = get_server(artifacts_dir=Path(artifacts))
    if transport == "http":
        mcp.run(transport=transport, port=port, host=host)
    else:
        mcp.run(transport=transport)


if __name__ == "__main__":
    main()
