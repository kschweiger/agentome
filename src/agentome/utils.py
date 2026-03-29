import json
from pathlib import Path

from agentome.models import Package


def list_package_versions(artifacts_dir: Path, package: str) -> list[str]:
    package_dir = artifacts_dir / package
    return sorted(p.stem for p in package_dir.glob("*.json"))


def load_artifact(artifacts_dir: Path, package: str, version: str):
    artifact_path = artifacts_dir / package / f"{version}.json"
    if not artifact_path.exists():
        available = list_package_versions(artifacts_dir, package)
        raise FileNotFoundError(
            f"No artifact found for {package}=={version}. "
            f"Available versions: {available or 'none'}. "
            f"Generate one with: llmscribe generate {package} --out {artifacts_dir}"
        )
    return json.loads(artifact_path.read_text())


def find_symbol(members: dict, symbol: str) -> dict | None:
    """Recursively search for a symbol by name across the member tree."""
    for name, obj in members.items():
        if name.lower() == symbol.lower():
            return obj
        # Recurse into classes/modules
        if "members" in obj:
            result = find_symbol(obj["members"], symbol)
            if result:
                return result
    return None
