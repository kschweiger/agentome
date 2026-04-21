import json
import os
from pathlib import Path
from typing import Literal

import click
from dotenv import load_dotenv

from agentome.config import (
    CliConfigInput,
    RuntimeConfig,
    resolve_runtime_config,
    validate_runtime_config,
)
from agentome.server import get_server
from agentome.store import LocalArtifactStore, S3ArtifactStore


def _build_store(config: RuntimeConfig) -> LocalArtifactStore | S3ArtifactStore:
    if config.artifact_store == "local":
        if config.artifacts_dir is None:
            raise ValueError(
                "AGENTOME_ARTIFACTS_DIR must be set for local artifact store"
            )
        return LocalArtifactStore(config.artifacts_dir)

    if (
        config.s3_endpoint is None
        or config.s3_access_key is None
        or config.s3_secret_key is None
        or config.s3_bucket is None
    ):
        raise ValueError("Missing required S3 configuration values")

    return S3ArtifactStore(
        endpoint=config.s3_endpoint,
        access_key=config.s3_access_key,
        secret_key=config.s3_secret_key,
        bucket=config.s3_bucket,
        prefix=config.s3_prefix,
        region=config.s3_region,
    )


@click.group()
def cli() -> None:
    """Agentome CLI."""
    pass


@click.command("serve")
@click.option(
    "--artifact-store",
    type=click.Choice(["local", "s3"]),
    envvar="AGENTOME_ARTIFACT_STORE",
    default="local",
    show_default=True,
    help="Artifact backend to use",
)
@click.option(
    "--artifacts",
    help="Artifact directory path for local backend",
    type=click.Path(file_okay=False, path_type=Path),
    envvar="AGENTOME_ARTIFACTS_DIR",
)
@click.option(
    "--s3-endpoint",
    help="S3-compatible endpoint URL",
    envvar="AGENTOME_S3_ENDPOINT",
)
@click.option(
    "--s3-access-key",
    help="S3 access key",
    envvar="AGENTOME_S3_ACCESS_KEY",
)
@click.option(
    "--s3-secret-key",
    help="S3 secret key",
    envvar="AGENTOME_S3_SECRET_KEY",
)
@click.option(
    "--s3-bucket",
    help="S3 bucket name",
    envvar="AGENTOME_S3_BUCKET",
)
@click.option(
    "--s3-prefix",
    help="S3 key prefix",
    envvar="AGENTOME_S3_PREFIX",
    default="",
    show_default=True,
)
@click.option(
    "--s3-region",
    help="S3 region",
    envvar="AGENTOME_S3_REGION",
    default="us-east-1",
    show_default=True,
)
@click.option("--host", default="localhost", help="The host to run the server on")
@click.option("--port", default=8000, help="The port to run the server on")
@click.option(
    "--transport",
    default="stdio",
    help="The transport protocol to use (http or stdio)",
    type=click.Choice(["http", "stdio"]),
)
def serve(
    artifact_store: Literal["local", "s3"],
    artifacts: Path | None,
    s3_endpoint: str | None,
    s3_access_key: str | None,
    s3_secret_key: str | None,
    s3_bucket: str | None,
    s3_prefix: str,
    s3_region: str,
    host: str,
    port: int,
    transport: Literal["http", "stdio"],
) -> None:
    load_dotenv(override=False)
    config = resolve_runtime_config(
        CliConfigInput(
            artifact_store=artifact_store,
            artifacts_dir=str(artifacts) if artifacts is not None else None,
            s3_endpoint=s3_endpoint,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix,
            s3_region=s3_region,
        ),
        os.environ,
    )
    validate_runtime_config(config)

    store = _build_store(config)
    mcp = get_server(store=store)
    if transport == "http":
        mcp.run(transport=transport, port=port, host=host)
    else:
        mcp.run(transport=transport)


@click.command("bootstrap-bucket")
@click.option(
    "--s3-endpoint",
    help="S3-compatible endpoint URL",
    envvar="AGENTOME_S3_ENDPOINT",
)
@click.option(
    "--s3-access-key",
    help="S3 access key",
    envvar="AGENTOME_S3_ACCESS_KEY",
)
@click.option(
    "--s3-secret-key",
    help="S3 secret key",
    envvar="AGENTOME_S3_SECRET_KEY",
)
@click.option(
    "--s3-bucket",
    help="S3 bucket name",
    envvar="AGENTOME_S3_BUCKET",
)
@click.option(
    "--s3-prefix",
    help="S3 key prefix",
    envvar="AGENTOME_S3_PREFIX",
    default="",
    show_default=True,
)
@click.option(
    "--s3-region",
    help="S3 region",
    envvar="AGENTOME_S3_REGION",
    default="us-east-1",
    show_default=True,
)
def bootstrap_bucket(
    s3_endpoint: str | None,
    s3_access_key: str | None,
    s3_secret_key: str | None,
    s3_bucket: str | None,
    s3_prefix: str,
    s3_region: str,
) -> None:
    load_dotenv(override=False)
    config = resolve_runtime_config(
        CliConfigInput(
            artifact_store="s3",
            s3_endpoint=s3_endpoint,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix,
            s3_region=s3_region,
        ),
        os.environ,
    )
    validate_runtime_config(config)
    store = _build_store(config)
    if not isinstance(store, S3ArtifactStore):
        raise ValueError("bootstrap-bucket only supports s3 store")

    result = store.bootstrap_bucket()
    click.echo(json.dumps(result, sort_keys=True))


cli.add_command(serve)
cli.add_command(bootstrap_bucket)


def bootstrap_bucket_entrypoint() -> None:
    load_dotenv(override=False)
    bootstrap_bucket.main(standalone_mode=True)
