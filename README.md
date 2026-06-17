# fusionkit

FusionKit is a uv-managed Python monorepo for local response-level model fusion.
It is designed to orchestrate local MLX/OpenAI-compatible model servers, generate
multiple candidate answers, rank and synthesize them, and evaluate whether the
resulting system is Pareto-front for quality, latency, memory, and energy.

## Packages

- `fusionkit-core`: config, local model clients, panel generation, fusion, routing, metrics
- `fusionkit-server`: FastAPI OpenAI-compatible server
- `fusionkit-evals`: benchmark schemas, scoring, Pareto analysis
- `fusionkit-cli`: `fusionkit serve`, `fusionkit eval`, `fusionkit pareto`
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
