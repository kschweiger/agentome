import json
from pathlib import Path
from typing import Callable

import pytest


@pytest.fixture
def artifact_root(tmp_path: Path) -> Path:
    root = tmp_path / "artifacts"
    root.mkdir()
    return root


@pytest.fixture
def sample_artifact_payload() -> dict[str, object]:
    return {
        "api": {
            "members": {
                "NormalizationPipeline": {
                    "kind": "class",
                    "members": {
                        "run": {
                            "kind": "function",
                            "parameters": [],
                            "returns": "None",
                        }
                    },
                },
                "top_level_fn": {
                    "kind": "function",
                    "parameters": [],
                    "returns": "int",
                },
            }
        }
    }


def write_artifact(
    root: Path,
    package: str,
    version: str,
    payload: dict[str, object],
) -> Path:
    package_dir = root / package
    package_dir.mkdir(parents=True, exist_ok=True)
    target = package_dir / f"{version}.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


@pytest.fixture
def artifact_writer() -> Callable[[Path, str, str, dict[str, object]], Path]:
    return write_artifact
