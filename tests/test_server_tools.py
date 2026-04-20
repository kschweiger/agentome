import asyncio
from pathlib import Path
from typing import Callable

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult

from agentome.server import get_local_server


def _call_tool(
    server: FastMCP,
    name: str,
    arguments: dict[str, object] | None = None,
) -> ToolResult:
    return asyncio.run(server.call_tool(name, arguments))


def test_list_packages_returns_packages_with_versions_only(
    artifact_root: Path,
    sample_artifact_payload: dict[str, object],
    artifact_writer: Callable[[Path, str, str, dict[str, object]], Path],
) -> None:
    artifact_writer(artifact_root, "with_versions", "1.0.0", sample_artifact_payload)
    (artifact_root / "empty_pkg").mkdir()

    server = get_local_server(artifact_root)
    result = _call_tool(server, "list_packages")

    assert result.structured_content == {"packages": {"with_versions": ["1.0.0"]}}


def test_list_versions_returns_versions_and_latest(
    artifact_root: Path,
    sample_artifact_payload: dict[str, object],
    artifact_writer: Callable[[Path, str, str, dict[str, object]], Path],
) -> None:
    artifact_writer(artifact_root, "pkg", "2.0.0", sample_artifact_payload)
    artifact_writer(artifact_root, "pkg", "1.0.0", sample_artifact_payload)

    server = get_local_server(artifact_root)
    result = _call_tool(server, "list_versions", {"package": "pkg"})

    assert result.structured_content == {
        "package": "pkg",
        "versions": ["1.0.0", "2.0.0"],
        "latest": "2.0.0",
    }


def test_list_versions_returns_none_latest_when_no_versions(
    artifact_root: Path,
) -> None:
    (artifact_root / "pkg").mkdir()

    server = get_local_server(artifact_root)
    result = _call_tool(server, "list_versions", {"package": "pkg"})

    assert result.structured_content == {
        "package": "pkg",
        "versions": [],
        "latest": None,
    }


def test_get_api_returns_artifact_payload_on_success(
    artifact_root: Path,
    sample_artifact_payload: dict[str, object],
    artifact_writer: Callable[[Path, str, str, dict[str, object]], Path],
) -> None:
    artifact_writer(artifact_root, "pkg", "1.0.0", sample_artifact_payload)

    server = get_local_server(artifact_root)
    result = _call_tool(server, "get_api", {"package": "pkg", "version": "1.0.0"})

    assert result.structured_content == sample_artifact_payload


def test_get_api_returns_error_dict_when_version_missing(artifact_root: Path) -> None:
    server = get_local_server(artifact_root)

    result = _call_tool(server, "get_api", {"package": "pkg", "version": "9.9.9"})

    payload = result.structured_content
    assert "error" in payload  # type: ignore
    assert "pkg==9.9.9" in payload["error"]  # type: ignore


def test_get_symbol_returns_symbol_payload_on_success(
    artifact_root: Path,
    sample_artifact_payload: dict[str, object],
    artifact_writer: Callable[[Path, str, str, dict[str, object]], Path],
) -> None:
    artifact_writer(artifact_root, "pkg", "1.0.0", sample_artifact_payload)

    server = get_local_server(artifact_root)
    result = _call_tool(
        server,
        "get_symbol",
        {
            "package": "pkg",
            "version": "1.0.0",
            "symbol": "NormalizationPipeline",
        },
    )

    assert result.structured_content == {
        "package": "pkg",
        "version": "1.0.0",
        "symbol": "NormalizationPipeline",
        "api": sample_artifact_payload["api"]["members"]["NormalizationPipeline"],
    }


def test_get_symbol_returns_error_and_top_level_symbols_when_missing(
    artifact_root: Path,
    sample_artifact_payload: dict[str, object],
    artifact_writer: Callable[[Path, str, str, dict[str, object]], Path],
) -> None:
    artifact_writer(artifact_root, "pkg", "1.0.0", sample_artifact_payload)

    server = get_local_server(artifact_root)
    result = _call_tool(
        server,
        "get_symbol",
        {
            "package": "pkg",
            "version": "1.0.0",
            "symbol": "does_not_exist",
        },
    )

    payload = result.structured_content
    assert "error" in payload
    assert payload["top_level_symbols"] == ["NormalizationPipeline", "top_level_fn"]
