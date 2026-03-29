from pydantic import BaseModel


class PackageList(BaseModel):
    packages: dict[str, list[str]]


class Package(BaseModel):
    name: str
    versions: list[str]
