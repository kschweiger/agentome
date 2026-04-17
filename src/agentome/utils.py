import json
from pathlib import Path


def list_package_versions(artifacts_dir: Path, package: str) -> list[str]:
    package_dir = artifacts_dir / package
    return sorted(p.stem for p in package_dir.glob("*.json"))


def load_artifact(artifacts_dir: Path, package: str, version: str) -> dict[str, object]:
    artifact_path = artifacts_dir / package / f"{version}.json"
    if not artifact_path.exists():
        available = list_package_versions(artifacts_dir, package)
        raise FileNotFoundError(
            f"No artifact found for {package}=={version}. "
            f"Available versions: {available or 'none'}. "
            f"Generate one with: llmscribe generate {package} --out {artifacts_dir}"
        )
    artifact = json.loads(artifact_path.read_text())
    if isinstance(artifact, dict):
        return artifact
    raise ValueError(f"Artifact at {artifact_path} is not a JSON object")


def find_symbol(
    members: dict[str, dict[str, object]], symbol: str
) -> dict[str, object] | None:
    """Recursively search for a symbol by name across the member tree."""
    for name, obj in members.items():
        if name.lower() == symbol.lower():
            return obj
        nested_members = obj.get("members")
        if isinstance(nested_members, dict):
            result = find_symbol(nested_members, symbol)
            if result:
                return result
    return None
