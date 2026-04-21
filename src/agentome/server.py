from pathlib import Path

from fastmcp import FastMCP

from agentome.models import PackageList
from agentome.store import ArtifactStore, LocalArtifactStore
from agentome.utils import find_symbol

ApiMembers = dict[str, dict[str, object]]


def get_server(store: ArtifactStore) -> FastMCP:
    mcp = FastMCP(
        name="agentome",
        instructions="""
            Serves versioned API reference artifacts for Python libraries.
            Use list_packages() to discover what is available, then get_symbol() or
            get_api() to retrieve documentation. Always pass the exact version string
            as reported by importlib.metadata, pip freeze, pip list or uv pip list in
            the target environment.
            """,
    )

    @mcp.tool
    def list_packages() -> PackageList:
        """
        List all packages that have API artifacts available on this server.
        Returns package names and their available versions.
        """
        return PackageList(packages=store.list_packages())

    @mcp.tool
    def list_versions(package: str) -> dict:
        """
        List all available artifact versions for a specific package.

        Args:
            package: The pip package name (e.g. "your-data-pipeline")
        """
        versions = store.list_versions(package)
        return {
            "package": package,
            "versions": versions,
            "latest": versions[-1] if versions else None,
        }

    @mcp.tool
    def get_api(package: str, version: str) -> dict:
        """
        Return the full API reference for a package version.
        Prefer get_symbol() when you know what you're looking for —
        this can be large for packages with many symbols.

        Args:
            package: The pip package name (e.g. "your-data-pipeline")
            version: Exact version string (e.g. "1.8.0")
        """
        try:
            return store.load_artifact(package, version)
        except FileNotFoundError as e:
            return {"error": str(e)}

    @mcp.tool
    def get_symbol(package: str, version: str, symbol: str) -> dict:
        """
        Return the API reference for a single class or function.
        More token-efficient than get_api() when you know what you need.

        Args:
            package: The pip package name (e.g. "your-data-pipeline")
            version: Exact version string (e.g. "1.8.0")
            symbol: Class or function name (e.g. "NormalizationPipeline")
        """
        try:
            artifact = store.load_artifact(package, version)
        except FileNotFoundError as e:
            return {"error": str(e)}

        api = artifact.get("api", {})
        if not isinstance(api, dict):
            return {
                "error": f"Artifact for {package}=={version} has invalid api payload."
            }
        members_obj = api.get("members", {})
        if not isinstance(members_obj, dict):
            return {
                "error": f"Artifact for {package}=={version} has invalid "
                "members payload."
            }

        members: ApiMembers = {}
        for key, value in members_obj.items():
            if isinstance(key, str) and isinstance(value, dict):
                members[key] = value

        result = find_symbol(members, symbol)
        if result is None:
            # Give the agent a useful list of top-level symbols to try
            top_level = list(members.keys())
            return {
                "error": f"Symbol '{symbol}' not found in {package}=={version}.",
                "top_level_symbols": top_level,
            }

        return {"package": package, "version": version, "symbol": symbol, "api": result}

    return mcp


def get_local_server(artifacts_dir: Path) -> FastMCP:
    return get_server(LocalArtifactStore(artifacts_dir))
