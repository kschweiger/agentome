import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class UploadConfig:
    artifacts_dir: Path
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    prefix: str
    region: str
    dry_run: bool
    skip_existing: bool
    fail_fast: bool


@dataclass(frozen=True)
class ArtifactFile:
    package: str
    version: str
    file_path: Path


@dataclass(frozen=True)
class UploadSummary:
    discovered: int
    uploaded: int
    skipped: int
    failed: int


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Upload llmscribe artifacts from local directory to "
        "S3-compatible store"
    )
    parser.add_argument(
        "--artifacts-dir",
        default=os.getenv("AGENTOME_ARTIFACTS_DIR"),
        help="Path to artifacts directory (env: AGENTOME_ARTIFACTS_DIR)",
    )
    parser.add_argument(
        "--endpoint",
        default=os.getenv("AGENTOME_S3_ENDPOINT"),
        help="S3 endpoint URL (env: AGENTOME_S3_ENDPOINT)",
    )
    parser.add_argument(
        "--access-key",
        default=os.getenv("AGENTOME_S3_ACCESS_KEY"),
        help="S3 access key (env: AGENTOME_S3_ACCESS_KEY)",
    )
    parser.add_argument(
        "--secret-key",
        default=os.getenv("AGENTOME_S3_SECRET_KEY"),
        help="S3 secret key (env: AGENTOME_S3_SECRET_KEY)",
    )
    parser.add_argument(
        "--bucket",
        default=os.getenv("AGENTOME_S3_BUCKET"),
        help="S3 bucket name (env: AGENTOME_S3_BUCKET)",
    )
    parser.add_argument(
        "--prefix",
        default=os.getenv("AGENTOME_S3_PREFIX", ""),
        help="Optional key prefix (env: AGENTOME_S3_PREFIX)",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("AGENTOME_S3_REGION", "us-east-1"),
        help="S3 region (env: AGENTOME_S3_REGION)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show uploads without sending data",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip object when key already exists (default: true)",
    )
    parser.add_argument(
        "--overwrite",
        dest="skip_existing",
        action="store_false",
        help="Overwrite existing objects",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop at first upload error",
    )
    return parser


def _normalize_prefix(prefix: str) -> str:
    normalized = prefix.strip("/")
    if not normalized:
        return ""
    return f"{normalized}/"


def _require_str(name: str, value: str | None) -> str:
    if value is None or not value.strip():
        raise ValueError(f"Missing required value: {name}")
    return value


def _load_config(args: argparse.Namespace) -> UploadConfig:
    artifacts_raw = _require_str(
        "--artifacts-dir / AGENTOME_ARTIFACTS_DIR", args.artifacts_dir
    )
    artifacts_dir = Path(artifacts_raw)
    if not artifacts_dir.exists() or not artifacts_dir.is_dir():
        raise ValueError(f"Artifacts directory does not exist: {artifacts_dir}")

    return UploadConfig(
        artifacts_dir=artifacts_dir,
        endpoint=_require_str("--endpoint / AGENTOME_S3_ENDPOINT", args.endpoint),
        access_key=_require_str(
            "--access-key / AGENTOME_S3_ACCESS_KEY", args.access_key
        ),
        secret_key=_require_str(
            "--secret-key / AGENTOME_S3_SECRET_KEY", args.secret_key
        ),
        bucket=_require_str("--bucket / AGENTOME_S3_BUCKET", args.bucket),
        prefix=_normalize_prefix(args.prefix),
        region=_require_str("--region / AGENTOME_S3_REGION", args.region),
        dry_run=bool(args.dry_run),
        skip_existing=bool(args.skip_existing),
        fail_fast=bool(args.fail_fast),
    )


def _iter_artifacts(artifacts_dir: Path) -> Iterable[ArtifactFile]:
    package_dirs = sorted(path for path in artifacts_dir.iterdir() if path.is_dir())
    for package_dir in package_dirs:
        json_files = sorted(path for path in package_dir.glob("*.json"))
        for json_file in json_files:
            yield ArtifactFile(
                package=package_dir.name,
                version=json_file.stem,
                file_path=json_file,
            )


def _object_key(prefix: str, package: str, version: str) -> str:
    return f"{prefix}{package}/{version}.json"


def _build_s3_client(config: UploadConfig) -> object:
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError(
            "boto3 required for uploader. Install with: pip install boto3"
        ) from exc

    return boto3.client(
        "s3",
        endpoint_url=config.endpoint,
        aws_access_key_id=config.access_key,
        aws_secret_access_key=config.secret_key,
        region_name=config.region,
    )


def _object_exists(client: object, bucket: str, key: str) -> bool:
    try:
        getattr(client, "head_object")(Bucket=bucket, Key=key)
        return True
    except Exception as exc:
        response = getattr(exc, "response", None)
        if not isinstance(response, dict):
            raise
        error = response.get("Error")
        if not isinstance(error, dict):
            raise
        code = error.get("Code")
        if isinstance(code, str) and code in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise


def _upload(config: UploadConfig, client: object) -> UploadSummary:
    uploaded = 0
    skipped = 0
    failed = 0
    artifacts = list(_iter_artifacts(config.artifacts_dir))

    for artifact in artifacts:
        key = _object_key(config.prefix, artifact.package, artifact.version)
        try:
            if config.skip_existing and _object_exists(client, config.bucket, key):
                skipped += 1
                print(f"skip existing: s3://{config.bucket}/{key}")
                continue

            if config.dry_run:
                print(
                    f"dry-run upload: {artifact.file_path} -> s3://{config.bucket}/{key}"
                )
                uploaded += 1
                continue

            payload = artifact.file_path.read_bytes()
            getattr(client, "put_object")(
                Bucket=config.bucket,
                Key=key,
                Body=payload,
                ContentType="application/json",
            )
            uploaded += 1
            print(f"uploaded: {artifact.file_path} -> s3://{config.bucket}/{key}")
        except Exception as exc:
            failed += 1
            print(
                f"upload failed: {artifact.file_path} -> "
                f"s3://{config.bucket}/{key}: {exc}"
            )
            if config.fail_fast:
                break

    return UploadSummary(
        discovered=len(artifacts),
        uploaded=uploaded,
        skipped=skipped,
        failed=failed,
    )


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        config = _load_config(args)
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    client = _build_s3_client(config)
    summary = _upload(config, client)
    print(json.dumps(summary.__dict__, sort_keys=True))
    return 1 if summary.failed > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
