# On Faultization: Pigeonhole Principle (simulation)

Morphogenetic perturbation experiments on the pigeonhole principle reinterpreted as a distributed multi-agent placement system (numpy backend). This is the paper's `simulation/` directory; run all commands from here.

## Running commands

Always use `uv run --script` to execute scripts (picks up inline dependencies), from this `simulation/` directory:

```
uv run --script run.py <command> [--num-reps N] [--num-steps N] [--result-suffix SUFFIX]
```

## Key commands

```
uv run --script run.py test              # Quick smoke test
uv run --script run.py experiment1       # Single experiment (1-8)
uv run --script run.py all               # All 8 experiments
uv run --script run.py experiment3       # Noisy perception
```

Statistical analysis:

```
uv run --script analyze_stats.py all     # All experiments
uv run --script analyze_stats.py exp1    # Single experiment
uv run --script analyze_stats.py summary # Cross-experiment summary
```

Visualization:

```
uv run --script visualize.py             # Generate all plots
```

## Project structure

- `model.py` — core pigeonhole system (numpy backend)
- `perturbations.py` — hook-based perturbations (freeze, noise, misleading, etc.)
- `experiments.py` — 8 experiment functions
- `metrics.py` — statistical metrics (DG index, robustness curves, etc.)
- `run.py` — CLI dispatcher
- `analyze_stats.py` — paired t-tests and summary tables
- `visualize.py` — matplotlib plotting functions
- `results/` — JSON result files (committed) plus PNG plots (gitignored)
- `EXPERIMENTS.md`, `FINDINGS.md` — detailed experiment and findings write-ups
- `../paper/PAPER.md` — the manuscript; `../CLAIM_LEDGER.md` — the numeric-claim ledger

## Model

`m = 10` pigeons, `n = 7` holes. Overload `O = Σ max(0, ℓ_i − 1)`. When all pigeons are placed, `O = m − H` for `H` occupied holes, so `O_min = m − n = 3` is reached exactly when every hole is occupied (complete coverage of the usable holes, not optimal load balancing). Four local policies (GREEDY, EXPLORATORY, REPULSIVE, COOPERATIVE); a composite potential `Φ` additionally penalizes concentration and unplaced pigeons. Frozen holes silently reject new placements and do not eject their current occupant; misleading holes accept placement but report load 0.

## Experiments

1. Frozen hole robustness curve — coverage under substrate loss (pattern bandwidth)
2. Policy comparison (GREEDY, EXPLORATORY, REPULSIVE, COOPERATIVE) — identical endpoints, divergent process cost
3. Noisy perception (Gaussian noise on reported loads) — pattern fidelity in a discrete interface
4. View radius sweep (pigeon visibility range) — information geometry; visibility buys speed, not reachability
5. Chimeric policies (mixed-policy populations) — aggregation tested against the correct 0.75 baseline
6. Recovery after damage (freeze then heal) — process cost of fault duration (dynamic freeze keeps incumbents, so overload is unchanged)
7. Progressive vs sudden damage — schedule affects failed attempts, not the overload endpoint
8. Misleading holes (deceptive substrate) — pattern corruption and deceptive-feedback capture
