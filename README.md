# fusionkit

FusionKit is a uv-managed Python monorepo for local response-level model fusion.
It is designed to orchestrate local MLX/OpenAI-compatible model servers, generate
multiple candidate answers, rank and synthesize them, and evaluate whether the
resulting system is Pareto-front for quality, latency, memory, and energy.

## Install

The CLI is published to PyPI as the `fusionkit` distribution. Run it without a
checkout via `uvx` (this is how HandoffKit's `fusionkit codex` boots the
synthesizer), or install it directly:

```bash
uvx fusionkit serve --config configs/models.example.yaml   # no install needed
# or
pip install fusionkit && fusionkit serve --config configs/models.example.yaml
```

MLX support is an Apple-Silicon-only extra (`mlx-lm`), so non-macOS installs
succeed without it. Install the local-model helpers with `pip install
fusionkit[mlx]` on Apple Silicon.

## Packages

- `fusionkit-core`: config, local model clients, panel generation, fusion, routing, metrics
- `fusionkit-server`: FastAPI OpenAI-compatible server (+ single-model OpenAI shim)
- `fusionkit-evals`: benchmark schemas, scoring, Pareto analysis
- `fusionkit` (`packages/fusionkit-cli`): `fusionkit serve`, `serve-endpoint`, `eval`, `pareto`
- `fusionkit-mlx`: optional MLX helper utilities

## Development

```bash
uv sync --all-packages
uv run pytest
uv run ruff check .
```

## Project Notes

- [Model fusion learnings](docs/model-fusion-learnings.md): durable architecture notes
  from the contract, native run, tool, provider, and benchmark implementation work.
- [Local MLX panel demo](docs/local-mlx-panel-demo.md): reproducible Apple Silicon proof
  for three real local MLX models through `/v1/fusion/runs`.
- [HandoffKit fusion bench integration](docs/handoffkit-fusion-bench.md): record-contract
  seam for governed coding harnesses.

## Example

Start one or more local MLX servers, then point FusionKit at them:

```bash
mlx_lm.server --model mlx-community/Qwen3.5-9B-MLX-4bit --port 8101
uv run fusionkit serve --config configs/models.example.yaml
```
