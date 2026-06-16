from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from validate_contract_fixtures import compute_schema_bundle_hash

CONTRACT_ROOT = Path(__file__).resolve().parents[1] / "spec" / "model-fusion-contract"
PACKAGE_JSON = CONTRACT_ROOT / "package.json"
PROTOCOL_PACKAGE_JSON = CONTRACT_ROOT / "protocol-package.json"
PROTO_FILE = CONTRACT_ROOT / "proto" / "velum" / "model_fusion" / "v1" / "protocol.proto"
BUF_YAML = CONTRACT_ROOT / "buf.yaml"
BUF_GEN_YAML = CONTRACT_ROOT / "buf.gen.yaml"

REQUIRED_SERVICES = (
    "HarnessExecutorService",
    "CursorHarnessService",
    "MlxProviderService",
    "BenchmarkJoinService",
)
REQUIRED_MESSAGES = (
    "JsonContractRecord",
    "BenchmarkTaskEnvelope",
    "BenchmarkExecutionEnvelope",
)
PRIVATE_PYTHON_INDEXES = ("Cloudsmith", "AWS CodeArtifact", "Gemfury")
FORBIDDEN_COPIED_RECORD_FIELD_DECLARATIONS = (
    "artifact_id",
    "candidate_id",
    "receipt_id",
    "result_id",
    "run_id",
    "call_id",
    "request_hash",
    "prompt_hash",
    "setup_hash",
)


@dataclass(frozen=True)
class ProtocolPackageSummary:
    schema_bundle_hash: str
    package_name: str
    services: tuple[str, ...]
    messages: tuple[str, ...]


def validate_protocol_package(contract_root: Path = CONTRACT_ROOT) -> ProtocolPackageSummary:
    package_json = _load_json(contract_root / "package.json")
    protocol_package = _load_json(contract_root / "protocol-package.json")
    proto_text = (contract_root / PROTO_FILE.relative_to(CONTRACT_ROOT)).read_text(
        encoding="utf-8"
    )

    _require_file(contract_root / "buf.yaml")
    _require_file(contract_root / "buf.gen.yaml")
    _validate_package_json(package_json)
    _validate_protocol_package_json(protocol_package, contract_root)
    services = _declared_services(proto_text)
    messages = _declared_messages(proto_text)
    _validate_proto_surface(proto_text, services, messages)

    return ProtocolPackageSummary(
        schema_bundle_hash=protocol_package["schema_bundle_hash"],
        package_name=package_json["name"],
        services=tuple(service for service in REQUIRED_SERVICES if service in services),
        messages=tuple(message for message in REQUIRED_MESSAGES if message in messages),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate model-fusion protocol packaging.")
    parser.parse_args()
    summary = validate_protocol_package()
    print(
        json.dumps(
            {
                "schema_bundle_hash": summary.schema_bundle_hash,
                "package_name": summary.package_name,
                "services": list(summary.services),
                "messages": list(summary.messages),
            },
            sort_keys=True,
        )
    )


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def _require_file(path: Path) -> None:
    if not path.exists():
        raise ValueError(f"Missing protocol package file: {path}")


def _validate_package_json(package_json: dict[str, Any]) -> None:
    if package_json.get("name") != "@velum/model-fusion-protocol":
        raise ValueError("package.json must publish @velum/model-fusion-protocol")
    publish_config = package_json.get("publishConfig")
    if not isinstance(publish_config, dict):
        raise ValueError("package.json must include publishConfig")
    if publish_config.get("registry") != "https://npm.pkg.github.com":
        raise ValueError("package.json must target GitHub Packages for npm")
    files = package_json.get("files")
    if not isinstance(files, list):
        raise ValueError("package.json must include a files list")
    for required_file in ("schema", "proto", "buf.yaml", "buf.gen.yaml"):
        if required_file not in files:
            raise ValueError(f"package.json files must include {required_file}")


def _validate_protocol_package_json(
    protocol_package: dict[str, Any],
    contract_root: Path,
) -> None:
    expected_hash = compute_schema_bundle_hash(contract_root / "schema")
    if protocol_package.get("schema_bundle_hash") != expected_hash:
        raise ValueError("protocol-package.json schema_bundle_hash is out of date")
    if protocol_package.get("package_name") != "@velum/model-fusion-protocol":
        raise ValueError("protocol-package.json package_name is incorrect")
    if protocol_package.get("json_schema_format") != "persisted-record-audit-format":
        raise ValueError("protocol-package.json must keep JSON Schema as audit format")
    if protocol_package.get("protobuf_format") != "service-transport-envelope-format":
        raise ValueError("protocol-package.json must keep protobuf as transport format")
    python_config = protocol_package.get("python")
    if not isinstance(python_config, dict):
        raise ValueError("protocol-package.json must include Python package config")
    indexes = python_config.get("preferred_private_indexes")
    if not isinstance(indexes, list):
        raise ValueError("Python package config must list private index options")
    for index in PRIVATE_PYTHON_INDEXES:
        if index not in indexes:
            raise ValueError(f"Python package config must include {index}")


def _validate_proto_surface(
    proto_text: str,
    services: set[str],
    messages: set[str],
) -> None:
    missing_services = sorted(set(REQUIRED_SERVICES) - services)
    if missing_services:
        raise ValueError(f"Missing required services: {missing_services}")
    missing_messages = sorted(set(REQUIRED_MESSAGES) - messages)
    if missing_messages:
        raise ValueError(f"Missing required messages: {missing_messages}")
    if "repeated JsonContractRecord records" not in proto_text:
        raise ValueError("Benchmark execution envelopes must carry JSON contract records")
    for field_name in FORBIDDEN_COPIED_RECORD_FIELD_DECLARATIONS:
        pattern = re.compile(rf"^\s+\w+\s+{re.escape(field_name)}\s*=", re.MULTILINE)
        if pattern.search(proto_text):
            raise ValueError(
                f"Proto IDL must not copy persisted JSON record field {field_name!r}"
            )


def _declared_services(proto_text: str) -> set[str]:
    return set(re.findall(r"^service\s+(\w+)\s+\{", proto_text, flags=re.MULTILINE))


def _declared_messages(proto_text: str) -> set[str]:
    return set(re.findall(r"^message\s+(\w+)\s+\{", proto_text, flags=re.MULTILINE))


if __name__ == "__main__":
    main()
