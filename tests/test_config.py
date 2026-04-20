from pathlib import Path

import pytest

from agentome.config import (
    CliConfigInput,
    ENV_S3_ACCESS_KEY,
    ENV_S3_BUCKET,
    ENV_S3_ENDPOINT,
    ENV_S3_SECRET_KEY,
    resolve_runtime_config,
    validate_runtime_config,
)


def test_resolve_runtime_config_prefers_cli_over_env(tmp_path: Path) -> None:
    cli_artifacts = tmp_path / "cli-artifacts"
    cli_artifacts.mkdir()

    config = resolve_runtime_config(
        CliConfigInput(
            artifact_store="s3",
            artifacts_dir=str(cli_artifacts),
            s3_endpoint="http://cli-endpoint:9000",
            s3_access_key="cli-access",
            s3_secret_key="cli-secret",
            s3_bucket="cli-bucket",
            s3_prefix="cli-prefix",
            s3_region="eu-central-1",
        ),
        {
            "AGENTOME_ARTIFACT_STORE": "local",
            "AGENTOME_ARTIFACTS_DIR": "/env/path",
            "AGENTOME_S3_ENDPOINT": "http://env-endpoint:9000",
            "AGENTOME_S3_ACCESS_KEY": "env-access",
            "AGENTOME_S3_SECRET_KEY": "env-secret",
            "AGENTOME_S3_BUCKET": "env-bucket",
            "AGENTOME_S3_PREFIX": "env-prefix",
            "AGENTOME_S3_REGION": "us-east-2",
        },
    )

    assert config.artifact_store == "s3"
    assert config.artifacts_dir == cli_artifacts
    assert config.s3_endpoint == "http://cli-endpoint:9000"
    assert config.s3_access_key == "cli-access"
    assert config.s3_secret_key == "cli-secret"
    assert config.s3_bucket == "cli-bucket"
    assert config.s3_prefix == "cli-prefix"
    assert config.s3_region == "eu-central-1"


def test_validate_runtime_config_local_requires_existing_directory(
    tmp_path: Path,
) -> None:
    config = resolve_runtime_config(
        CliConfigInput(artifact_store="local", artifacts_dir=str(tmp_path / "missing")),
        {},
    )

    with pytest.raises(ValueError) as exc_info:
        validate_runtime_config(config)

    assert "AGENTOME_ARTIFACTS_DIR must be an existing directory" in str(exc_info.value)


def test_validate_runtime_config_s3_reports_missing_fields() -> None:
    config = resolve_runtime_config(CliConfigInput(artifact_store="s3"), {})

    with pytest.raises(ValueError) as exc_info:
        validate_runtime_config(config)

    message = str(exc_info.value)
    assert ENV_S3_ENDPOINT in message
    assert ENV_S3_ACCESS_KEY in message
    assert ENV_S3_SECRET_KEY in message
    assert ENV_S3_BUCKET in message
