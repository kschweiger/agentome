from pathlib import Path

from fastmcp import FastMCP

from agentome.models import PackageList
from agentome.utils import find_symbol, list_package_versions, load_artifact


def get_server(artifacts_dir: Path) -> FastMCP:
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
        packages = {}
        for package_dir in sorted(artifacts_dir.iterdir()):
            if package_dir.is_dir():
                _versions = list_package_versions(artifacts_dir, package_dir.name)
                if _versions:
                    packages[package_dir.name] = _versions
        return PackageList(packages=packages)

    @mcp.tool
    def list_versions(package: str) -> dict:
        """
        List all available artifact versions for a specific package.

        Args:
            package: The pip package name (e.g. "your-data-pipeline")
        """
        versions = list_package_versions(artifacts_dir, package)
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
            return load_artifact(artifacts_dir, package, version)
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
            artifact = load_artifact(artifacts_dir, package, version)
        except FileNotFoundError as e:
            return {"error": str(e)}

        api = artifact.get("api", {})
        members = api.get("members", {})

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
