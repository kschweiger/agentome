from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Mapping, cast

ArtifactStoreKind = Literal["local", "s3"]

ENV_ARTIFACT_STORE = "AGENTOME_ARTIFACT_STORE"
ENV_ARTIFACTS_DIR = "AGENTOME_ARTIFACTS_DIR"
ENV_S3_ENDPOINT = "AGENTOME_S3_ENDPOINT"
ENV_S3_ACCESS_KEY = "AGENTOME_S3_ACCESS_KEY"
ENV_S3_SECRET_KEY = "AGENTOME_S3_SECRET_KEY"
ENV_S3_BUCKET = "AGENTOME_S3_BUCKET"
ENV_S3_PREFIX = "AGENTOME_S3_PREFIX"
ENV_S3_REGION = "AGENTOME_S3_REGION"
DEFAULT_S3_REGION = "us-east-1"


@dataclass(frozen=True)
class CliConfigInput:
    artifact_store: str | None = None
    artifacts_dir: str | None = None
    s3_endpoint: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket: str | None = None
    s3_prefix: str | None = None
    s3_region: str | None = None


@dataclass(frozen=True)
class RuntimeConfig:
    artifact_store: ArtifactStoreKind
    artifacts_dir: Path | None
    s3_endpoint: str | None
    s3_access_key: str | None
    s3_secret_key: str | None
    s3_bucket: str | None
    s3_prefix: str
    s3_region: str


def validate_runtime_config(config: RuntimeConfig) -> None:
    if config.artifact_store == "local":
        if config.artifacts_dir is None:
            raise ValueError(
                "Missing required config for local store: AGENTOME_ARTIFACTS_DIR"
            )
        if not config.artifacts_dir.exists() or not config.artifacts_dir.is_dir():
            raise ValueError(
                "AGENTOME_ARTIFACTS_DIR must be an existing "
                f"directory: {config.artifacts_dir}"
            )
        return

    missing_fields: list[str] = []
    if not config.s3_endpoint:
        missing_fields.append(ENV_S3_ENDPOINT)
    if not config.s3_access_key:
        missing_fields.append(ENV_S3_ACCESS_KEY)
    if not config.s3_secret_key:
        missing_fields.append(ENV_S3_SECRET_KEY)
    if not config.s3_bucket:
        missing_fields.append(ENV_S3_BUCKET)

    if missing_fields:
        missing_list = ", ".join(missing_fields)
        raise ValueError(f"Missing required config for s3 store: {missing_list}")


def resolve_runtime_config(
    cli: CliConfigInput,
    environ: Mapping[str, str],
) -> RuntimeConfig:
    artifact_store_input = _first_non_none(
        cli.artifact_store,
        environ.get(ENV_ARTIFACT_STORE),
        "local",
    )
    if artifact_store_input is None:
        raise ValueError("artifact_store must be set")
    artifact_store = _normalize_artifact_store(artifact_store_input)
    artifacts_dir = _as_path(
        _first_non_none(cli.artifacts_dir, environ.get(ENV_ARTIFACTS_DIR))
    )
    s3_endpoint = _first_non_none(cli.s3_endpoint, environ.get(ENV_S3_ENDPOINT))
    s3_access_key = _first_non_none(cli.s3_access_key, environ.get(ENV_S3_ACCESS_KEY))
    s3_secret_key = _first_non_none(cli.s3_secret_key, environ.get(ENV_S3_SECRET_KEY))
    s3_bucket = _first_non_none(cli.s3_bucket, environ.get(ENV_S3_BUCKET))
    s3_prefix = _first_non_none(cli.s3_prefix, environ.get(ENV_S3_PREFIX), "")
    s3_region = _first_non_none(
        cli.s3_region,
        environ.get(ENV_S3_REGION),
        DEFAULT_S3_REGION,
    )
    if s3_prefix is None:
        raise ValueError("s3_prefix must be set")
    if s3_region is None:
        raise ValueError("s3_region must be set")

    return RuntimeConfig(
        artifact_store=artifact_store,
        artifacts_dir=artifacts_dir,
        s3_endpoint=s3_endpoint,
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        s3_region=s3_region,
    )


def _normalize_artifact_store(value: str) -> ArtifactStoreKind:
    normalized_value = value.strip().lower()
    if normalized_value in {"local", "s3"}:
        return cast(ArtifactStoreKind, normalized_value)
    raise ValueError("artifact_store must be one of: local, s3")


def _as_path(value: str | None) -> Path | None:
    if value is None:
        return None
    return Path(value)


def _first_non_none(*values: str | None) -> str | None:
    for value in values:
        if value is not None:
            return value
    return None
