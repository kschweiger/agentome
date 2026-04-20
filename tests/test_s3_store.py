import io
from typing import Iterator, Mapping, Sequence

import pytest

from agentome.store import S3ArtifactStore


class _FakePageIterator:
    def __init__(self, pages: Sequence[Mapping[str, object]]) -> None:
        self._pages = pages

    def __iter__(self) -> Iterator[Mapping[str, object]]:
        return iter(self._pages)


class _FakePaginator:
    def __init__(self, pages: Sequence[Mapping[str, object]]) -> None:
        self._pages = pages

    def paginate(self, **_: object) -> _FakePageIterator:
        return _FakePageIterator(self._pages)


class _FakeS3Error(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.response = {"Error": {"Code": code}}


class _FakeS3Client:
    def __init__(self) -> None:
        self.bucket_exists = False
        self.objects: dict[str, bytes] = {}

    def get_paginator(self, operation_name: str) -> _FakePaginator:
        assert operation_name == "list_objects_v2"
        pages = [{"Contents": [{"Key": key} for key in sorted(self.objects.keys())]}]
        return _FakePaginator(pages)

    def head_bucket(self, **_: object) -> dict[str, object]:
        if not self.bucket_exists:
            raise _FakeS3Error("404")
        return {}

    def create_bucket(self, **_: object) -> dict[str, object]:
        self.bucket_exists = True
        return {}

    def put_object(self, **kwargs: object) -> dict[str, object]:
        key = kwargs.get("Key")
        body = kwargs.get("Body")
        if not isinstance(key, str) or not isinstance(body, bytes):
            raise ValueError("invalid put_object args")
        self.objects[key] = body
        return {}

    def list_objects_v2(self, **kwargs: object) -> dict[str, object]:
        prefix = kwargs.get("Prefix", "")
        if not isinstance(prefix, str):
            raise ValueError("Prefix must be str")
        contents = [
            {"Key": key}
            for key in sorted(self.objects.keys())
            if key.startswith(prefix)
        ]
        return {"Contents": contents}

    def get_object(self, **kwargs: object) -> dict[str, object]:
        key = kwargs.get("Key")
        if not isinstance(key, str) or key not in self.objects:
            raise _FakeS3Error("NoSuchKey")
        return {"Body": io.BytesIO(self.objects[key])}


def test_bootstrap_bucket_idempotent_create_if_missing() -> None:
    client = _FakeS3Client()
    store = S3ArtifactStore(
        endpoint="http://localhost:9000",
        access_key="access",
        secret_key="secret",
        bucket="artifacts",
        prefix="team",
        s3_client=client,
    )

    first = store.bootstrap_bucket()
    second = store.bootstrap_bucket()

    assert first["created"] is True
    assert second["created"] is False
    assert first["status"] == "ok"
    assert second["status"] == "ok"


def test_list_packages_and_load_artifact() -> None:
    client = _FakeS3Client()
    client.bucket_exists = True
    client.objects["prefix/pkg/1.0.0.json"] = (
        b'{"api":{"members":{"Thing":{"kind":"class"}}}}'
    )

    store = S3ArtifactStore(
        endpoint="http://localhost:9000",
        access_key="access",
        secret_key="secret",
        bucket="artifacts",
        prefix="prefix",
        s3_client=client,
    )

    packages = store.list_packages()
    payload = store.load_artifact("pkg", "1.0.0")

    assert packages == {"pkg": ["1.0.0"]}
    assert payload["api"] == {"members": {"Thing": {"kind": "class"}}}


def test_missing_artifact_raises_file_not_found() -> None:
    client = _FakeS3Client()
    client.bucket_exists = True
    store = S3ArtifactStore(
        endpoint="http://localhost:9000",
        access_key="access",
        secret_key="secret",
        bucket="artifacts",
        s3_client=client,
    )

    with pytest.raises(FileNotFoundError) as exc_info:
        store.load_artifact("pkg", "9.9.9")

    assert "pkg==9.9.9" in str(exc_info.value)
