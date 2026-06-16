from __future__ import annotations

from importlib.resources import files
from pathlib import Path

__version__ = "0.1.0"
SCHEMA_BUNDLE_HASH = "sha256:75792f89c091b6ab4fd317a15fb03fd73438563dceff5ccf9f5d7c752dbf35f3"


def package_root() -> Path:
    return Path(str(files(__name__)))


def schema_dir() -> Path:
    return package_root() / "schema"


def openapi_dir() -> Path:
    return package_root() / "openapi"


def openapi_path() -> Path:
    return openapi_dir() / "model-fusion.v1.openapi.json"


__all__ = [
    "SCHEMA_BUNDLE_HASH",
    "__version__",
    "openapi_dir",
    "openapi_path",
    "package_root",
    "schema_dir",
]
