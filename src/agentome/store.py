import json
from pathlib import Path
from typing import Iterable, Mapping, Protocol

from agentome.utils import list_package_versions, load_artifact


class ArtifactStore(Protocol):
    def list_packages(self) -> dict[str, list[str]]: ...

    def list_versions(self, package: str) -> list[str]: ...

    def load_artifact(self, package: str, version: str) -> dict[str, object]: ...


class S3Paginator(Protocol):
    def paginate(self, **kwargs: object) -> Iterable[Mapping[str, object]]: ...


class S3Client(Protocol):
    def get_paginator(self, operation_name: str) -> S3Paginator: ...

    def head_bucket(self, **kwargs: object) -> dict[str, object]: ...

    def create_bucket(self, **kwargs: object) -> dict[str, object]: ...

    def put_object(self, **kwargs: object) -> dict[str, object]: ...

    def delete_object(self, **kwargs: object) -> dict[str, object]: ...

    def list_objects_v2(self, **kwargs: object) -> dict[str, object]: ...

    def get_object(self, **kwargs: object) -> dict[str, object]: ...


class LocalArtifactStore:
    def __init__(self, artifacts_dir: Path) -> None:
        self.artifacts_dir = artifacts_dir

    def list_packages(self) -> dict[str, list[str]]:
        packages: dict[str, list[str]] = {}
        for package_dir in sorted(self.artifacts_dir.iterdir()):
            if not package_dir.is_dir():
                continue
            versions = self.list_versions(package_dir.name)
            if versions:
                packages[package_dir.name] = versions
        return packages

    def list_versions(self, package: str) -> list[str]:
        return list_package_versions(self.artifacts_dir, package)

    def load_artifact(self, package: str, version: str) -> dict[str, object]:
        return load_artifact(self.artifacts_dir, package, version)


class S3ArtifactStore:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        prefix: str = "",
        region: str = "us-east-1",
        s3_client: S3Client | None = None,
    ) -> None:
        self.bucket = bucket
        self.prefix = _normalize_prefix(prefix)
        self.region = region
        self.client = s3_client or _build_s3_client(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            region=region,
        )

    def bootstrap_bucket(self) -> dict[str, object]:
        created = False
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except Exception as exc:
            if not _is_not_found_error(exc):
                raise
            create_kwargs: dict[str, object] = {"Bucket": self.bucket}
            if self.region != "us-east-1":
                create_kwargs["CreateBucketConfiguration"] = {
                    "LocationConstraint": self.region
                }
            self.client.create_bucket(**create_kwargs)
            created = True

        probe_key = f"{self.prefix}agentome-bootstrap-probe.json"
        probe_payload = b'{"ok":true}'
        self.client.put_object(Bucket=self.bucket, Key=probe_key, Body=probe_payload)

        get_response = self.client.get_object(Bucket=self.bucket, Key=probe_key)
        body = get_response.get("Body")
        if body is None or not hasattr(body, "read"):
            raise ValueError(
                f"Probe object at s3://{self.bucket}/{probe_key} unreadable"
            )

        returned = body.read()
        if returned != probe_payload:
            raise ValueError(
                f"Probe object at s3://{self.bucket}/{probe_key} payload mismatch"
            )

        list_response = self.client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=probe_key,
            MaxKeys=1,
        )
        contents = list_response.get("Contents", [])
        if not isinstance(contents, list) or not contents:
            raise ValueError(f"Probe key {probe_key} not visible in list_objects_v2")

        first_entry = contents[0]
        if not isinstance(first_entry, dict) or first_entry.get("Key") != probe_key:
            raise ValueError(f"Probe key {probe_key} mismatch in list_objects_v2")

        return {
            "bucket": self.bucket,
            "prefix": self.prefix,
            "created": created,
            "probe_key": probe_key,
            "status": "ok",
        }

    def list_packages(self) -> dict[str, list[str]]:
        packages: dict[str, list[str]] = {}
        paginator = self.client.get_paginator("list_objects_v2")
        pagination_kwargs = {"Bucket": self.bucket}
        if self.prefix:
            pagination_kwargs["Prefix"] = self.prefix

        for page in paginator.paginate(**pagination_kwargs):
            contents = page.get("Contents", [])
            if not isinstance(contents, list):
                continue
            for obj in contents:
                key = obj.get("Key") if isinstance(obj, dict) else None
                if not isinstance(key, str):
                    continue
                package_name, version = _package_and_version_from_key(key, self.prefix)
                if package_name is None or version is None:
                    continue
                packages.setdefault(package_name, []).append(version)

        return {
            package: sorted(set(versions))
            for package, versions in sorted(packages.items(), key=lambda item: item[0])
        }

    def list_versions(self, package: str) -> list[str]:
        return self.list_packages().get(package, [])

    def load_artifact(self, package: str, version: str) -> dict[str, object]:
        key = _artifact_key(self.prefix, package, version)
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
        except Exception as exc:
            if _is_not_found_error(exc):
                available = self.list_versions(package)
                raise FileNotFoundError(
                    f"No artifact found for {package}=={version}. "
                    f"Available versions: {available or 'none'}. "
                    "Generate and upload matching artifact JSON."
                ) from exc
            raise

        body = response.get("Body")
        if body is None or not hasattr(body, "read"):
            raise ValueError(
                f"Artifact at s3://{self.bucket}/{key} has no readable body"
            )

        raw_bytes = body.read()
        if not isinstance(raw_bytes, bytes):
            raise ValueError(f"Artifact at s3://{self.bucket}/{key} is not bytes")

        artifact = json.loads(raw_bytes.decode("utf-8"))
        if isinstance(artifact, dict):
            return artifact
        raise ValueError(f"Artifact at s3://{self.bucket}/{key} is not a JSON object")


def _build_s3_client(
    endpoint: str,
    access_key: str,
    secret_key: str,
    region: str,
) -> S3Client:
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError(
            "S3 artifact store requires optional dependency. Install with: pip install "
            "'agentome[s3]'"
        ) from exc

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )


def _normalize_prefix(prefix: str) -> str:
    normalized = prefix.strip("/")
    if not normalized:
        return ""
    return f"{normalized}/"


def _artifact_key(prefix: str, package: str, version: str) -> str:
    key = f"{package}/{version}.json"
    if not prefix:
        return key
    return f"{prefix}{key}"


def _package_and_version_from_key(
    key: str,
    prefix: str,
) -> tuple[str | None, str | None]:
    normalized_key = key
    if prefix:
        if not key.startswith(prefix):
            return None, None
        normalized_key = key[len(prefix) :]

    key_parts = normalized_key.split("/")
    if len(key_parts) != 2:
        return None, None

    package_name, version_filename = key_parts
    if not version_filename.endswith(".json"):
        return None, None

    return package_name, version_filename.removesuffix(".json")


def _is_not_found_error(exc: Exception) -> bool:
    response = getattr(exc, "response", None)
    if not isinstance(response, dict):
        return False
    error = response.get("Error")
    if not isinstance(error, dict):
        return False
    code = error.get("Code")
    return isinstance(code, str) and code in {
        "404",
        "NoSuchBucket",
        "NoSuchKey",
        "NotFound",
    }
