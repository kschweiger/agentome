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
@click.option("--port", default=8009, help="The port to run the server on")
@click.option(
    "--transport",
    default="stdio",
    help="The transport protocol to use (http or stdio)",
    type=click.Choice(["http", "stdio"]),
)
def main(artifacts: str, port: int, transport: Literal["http", "stdio"]) -> None:

    mcp = get_server(artifacts_dir=Path(artifacts))
    if transport == "http":
        mcp.run(transport=transport, port=port)
    else:
        mcp.run(transport=transport)


if __name__ == "__main__":
    main()
