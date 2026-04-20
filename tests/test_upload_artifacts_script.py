from pathlib import Path
import importlib.util
from typing import Iterable, Protocol, cast


class _ArtifactFile(Protocol):
    package: str
    version: str


class _UploaderModule(Protocol):
    def _normalize_prefix(self, prefix: str) -> str: ...

    def _object_key(self, prefix: str, package: str, version: str) -> str: ...

    def _iter_artifacts(self, artifacts_dir: Path) -> Iterable[_ArtifactFile]: ...


def _load_uploader_module() -> _UploaderModule:
    script_path = (
        Path(__file__).resolve().parents[1] / "scripts" / "upload_artifacts_to_s3.py"
    )
    spec = importlib.util.spec_from_file_location("upload_artifacts_to_s3", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load uploader script module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast(_UploaderModule, module)


uploader = _load_uploader_module()


def test_normalize_prefix() -> None:
    assert uploader._normalize_prefix("") == ""
    assert uploader._normalize_prefix("team") == "team/"
    assert uploader._normalize_prefix("/team/") == "team/"


def test_object_key_building() -> None:
    assert uploader._object_key("", "pkg", "1.2.3") == "pkg/1.2.3.json"
    assert uploader._object_key("team/", "pkg", "1.2.3") == "team/pkg/1.2.3.json"


def test_iter_artifacts_sorted(tmp_path: Path) -> None:
    (tmp_path / "b").mkdir()
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "2.0.0.json").write_text("{}", encoding="utf-8")
    (tmp_path / "a" / "1.0.0.json").write_text("{}", encoding="utf-8")
    (tmp_path / "b" / "3.0.0.json").write_text("{}", encoding="utf-8")

    found = list(uploader._iter_artifacts(tmp_path))
    identifiers = [(item.package, item.version) for item in found]

    assert identifiers == [
        ("a", "1.0.0"),
        ("a", "2.0.0"),
        ("b", "3.0.0"),
    ]
