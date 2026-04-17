from pathlib import Path
from typing import Callable

import pytest

from agentome.utils import find_symbol, list_package_versions, load_artifact


def test_list_package_versions_returns_sorted_json_stems(
    artifact_root: Path,
    sample_artifact_payload: dict[str, object],
    artifact_writer: Callable[[Path, str, str, dict[str, object]], Path],
) -> None:
    artifact_writer(artifact_root, "pkg", "2.0.0", sample_artifact_payload)
    artifact_writer(artifact_root, "pkg", "1.5.0", sample_artifact_payload)

    versions = list_package_versions(artifact_root, "pkg")

    assert versions == ["1.5.0", "2.0.0"]


def test_list_package_versions_missing_package_returns_empty_list(
    artifact_root: Path,
) -> None:
    versions = list_package_versions(artifact_root, "missing-package")
    assert versions == []


def test_load_artifact_returns_parsed_json(
    artifact_root: Path,
    sample_artifact_payload: dict[str, object],
    artifact_writer: Callable[[Path, str, str, dict[str, object]], Path],
) -> None:
    artifact_writer(artifact_root, "pkg", "1.0.0", sample_artifact_payload)

    artifact = load_artifact(artifact_root, "pkg", "1.0.0")

    assert "api" in artifact
    assert "NormalizationPipeline" in artifact["api"]["members"]


def test_load_artifact_raises_file_not_found_with_available_versions(
    artifact_root: Path,
    sample_artifact_payload: dict[str, object],
    artifact_writer: Callable[[Path, str, str, dict[str, object]], Path],
) -> None:
    artifact_writer(artifact_root, "pkg", "1.0.0", sample_artifact_payload)

    with pytest.raises(FileNotFoundError) as exc_info:
        load_artifact(artifact_root, "pkg", "9.9.9")

    message = str(exc_info.value)
    assert "pkg==9.9.9" in message
    assert "1.0.0" in message
    assert "llmscribe generate pkg" in message


def test_find_symbol_matches_case_insensitively(
    sample_artifact_payload: dict[str, object],
) -> None:
    members = sample_artifact_payload["api"]["members"]

    found = find_symbol(members, "normalizationpipeline")

    assert found is not None
    assert found["kind"] == "class"


def test_find_symbol_recurses_nested_members(
    sample_artifact_payload: dict[str, object],
) -> None:
    members = sample_artifact_payload["api"]["members"]

    found = find_symbol(members, "run")

    assert found is not None
    assert found["kind"] == "function"


def test_find_symbol_returns_none_when_missing(
    sample_artifact_payload: dict[str, object],
) -> None:
    members = sample_artifact_payload["api"]["members"]

    found = find_symbol(members, "does_not_exist")

    assert found is None
