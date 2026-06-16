# Model Fusion Protocol Consumption

FusionKit remains the contract and IDL origin for the model-fusion platform. Do not
copy contract shapes into HandoffKit, CursorKit, MLX provider integrations, or future
benchmark tooling. Consume a versioned protocol artifact from this repo instead.

## Artifact split

- JSON Schema in `spec/model-fusion-contract/schema/` is the persisted record and
  audit/benchmark format. Rows, receipts, artifacts, benchmark tasks, model calls,
  and harness results should continue to validate against these schemas.
- Buf/protobuf in `spec/model-fusion-contract/proto/` is the source of truth for
  service and SDK boundaries. The proto uses `JsonContractRecord` envelopes that
  carry JSON Schema records plus their `schema_bundle_hash`; it intentionally does
  not re-declare the persisted record fields.
- OpenAPI, if needed for HTTP clients or documentation, must be generated from the
  Buf/protobuf service IDL. Do not hand-author OpenAPI specs for these boundaries.

## Service boundaries

The initial IDL prepares these minimum service seams:

- `HarnessExecutorService`: FusionKit evals ask HandoffKit to execute coding tasks.
- `CursorHarnessService`: CursorKit maps adapter output into harness contract records.
- `MlxProviderService`: MLX provider adapters describe model capabilities and model-call
  metadata.
- `BenchmarkJoinService`: benchmark execution envelopes are joined into auditable row
  records.

## Package targets

TypeScript consumers should target the npm package name
`@velum/model-fusion-protocol`, published to GitHub Packages while the repo remains
private. The package should contain JSON Schemas, Buf/protobuf IDL, and generated
TypeScript SDK/protocol bindings once generation is wired in CI.

Python consumers need a private PyPI-compatible path. Prefer Cloudsmith, AWS
CodeArtifact, or Gemfury for private wheels. Short term, publish wheels to GitHub
Releases or pin `uv` git dependencies by commit. GitHub Packages is not enough for
private Python package consumption. Python repos should consume generated protocol
bindings from that package path rather than copying Pydantic or JSON Schema shapes.

## CI drift checks

CI should run:

```bash
uv run python scripts/validate_contract_fixtures.py
uv run python scripts/validate_protocol_package.py
uv run pytest
```

When Buf is installed in CI, add:

```bash
buf lint spec/model-fusion-contract
buf generate spec/model-fusion-contract
git diff --exit-code spec/model-fusion-contract/gen
```

The first two checks ensure JSON Schema fixture hashes, package metadata, required
service names, generated-only OpenAPI policy, and envelope-only proto boundaries do
not drift. The generated-code diff check should be enabled when generated TS/Python
bindings are committed or published from CI.

## Follow-up outside this PR

- HandoffKit should replace any copied protocol models with generated
  `HarnessExecutorService` bindings and JSON Schema validation from the package.
- CursorKit should emit `CursorHarnessService` records through generated bindings
  and keep Cursor-specific persisted records validated by JSON Schema.
- MLX provider integrations should consume `MlxProviderService` bindings for
  provider metadata instead of cloning FusionKit types.
- Release automation should publish the npm package and a private Python wheel from
  this FusionKit contract origin, then optionally generate OpenAPI from Buf for docs.
