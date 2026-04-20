import os
import json
import time
import uuid
from dataclasses import dataclass
from typing import Generator

import pytest
from dotenv import load_dotenv

from agentome.store import S3ArtifactStore


@dataclass(frozen=True)
class _IntegrationConfig:
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    prefix: str
    region: str


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"Missing required env var for s3 integration test: {name}")


@pytest.fixture
def integration_config() -> _IntegrationConfig:
    load_dotenv(override=False)
    if os.getenv("AGENTOME_RUN_S3_INTEGRATION", "0") != "1":
        pytest.skip("Set AGENTOME_RUN_S3_INTEGRATION=1 to run s3 integration tests")

    run_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    base_prefix = os.getenv("AGENTOME_S3_PREFIX", "").strip("/")
    test_prefix = (
        f"{base_prefix}/agentome-it/{run_id}"
        if base_prefix
        else f"agentome-it/{run_id}"
    )

    return _IntegrationConfig(
        endpoint=_required_env("AGENTOME_S3_ENDPOINT"),
        access_key=_required_env("AGENTOME_S3_ACCESS_KEY"),
        secret_key=_required_env("AGENTOME_S3_SECRET_KEY"),
        bucket=_required_env("AGENTOME_S3_BUCKET"),
        prefix=test_prefix,
        region=os.getenv("AGENTOME_S3_REGION", "us-east-1"),
    )


@pytest.fixture
def s3_store(
    integration_config: _IntegrationConfig,
) -> Generator[S3ArtifactStore, None, None]:
    store = S3ArtifactStore(
        endpoint=integration_config.endpoint,
        access_key=integration_config.access_key,
        secret_key=integration_config.secret_key,
        bucket=integration_config.bucket,
        prefix=integration_config.prefix,
        region=integration_config.region,
    )
    yield store

    paginator = store.client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=store.bucket, Prefix=store.prefix):
        contents = page.get("Contents", [])
        if not isinstance(contents, list):
            continue
        for obj in contents:
            if not isinstance(obj, dict):
                continue
            key = obj.get("Key")
            if isinstance(key, str):
                try:
                    store.client.delete_object(Bucket=store.bucket, Key=key)
                except Exception:
                    pass


@pytest.mark.s3_integration
def test_bootstrap_bucket_idempotent_real_client(s3_store: S3ArtifactStore) -> None:
    store = s3_store

    first = store.bootstrap_bucket()
    second = store.bootstrap_bucket()

    assert first["status"] == "ok"
    assert second["status"] == "ok"
    assert first["probe_key"] == second["probe_key"]


@pytest.mark.s3_integration
def test_roundtrip_real_client(s3_store: S3ArtifactStore) -> None:
    key = f"{s3_store.prefix}pkg/1.2.3.json"
    payload = {
        "api": {
            "members": {
                "MyClass": {
                    "kind": "class",
                    "members": {},
                }
            }
        }
    }
    s3_store.client.put_object(
        Bucket=s3_store.bucket,
        Key=key,
        Body=json.dumps(payload).encode("utf-8"),
    )

    packages = s3_store.list_packages()
    versions = s3_store.list_versions("pkg")
    loaded = s3_store.load_artifact("pkg", "1.2.3")

    assert packages["pkg"] == ["1.2.3"]
    assert versions == ["1.2.3"]
    assert loaded == payload


@pytest.mark.s3_integration
def test_missing_version_real_client_raises_file_not_found(
    s3_store: S3ArtifactStore,
) -> None:
    with pytest.raises(FileNotFoundError) as exc_info:
        s3_store.load_artifact("missing-pkg", "9.9.9")

    assert "missing-pkg==9.9.9" in str(exc_info.value)
