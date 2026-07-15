# Research notes

## Where the work lives

- `paper/PAPER.md` — the manuscript.
- `CLAIM_LEDGER.md` — every numeric claim in the paper, traced to the result file it comes from (`claims_target: claim-ledger`).
- `simulation/` — the full experimental harness (numpy backend, deterministic, seeded). Entry point `simulation/run.py`; see `simulation/README.md` for commands. Detailed write-ups are in `simulation/EXPERIMENTS.md` and `simulation/FINDINGS.md`.
- `simulation/results/*.json` — committed per-run results (n = 30); PNG plots regenerate via `visualize.py` and are gitignored.

## The system and the experimental program

Base model: `m = 10` pigeons, `n = 7` holes, overload `O = Σ max(0, ℓ_i − 1)`, composite potential `Φ = α·overload + β·squared-excess + γ·unplaced` (α = 1.0, β = 0.5, γ = 10.0). Four local policies and a hook-based perturbation architecture (`pigeon_view`, `pigeon_decision`, `placement_attempt`, `post_step`) let every experiment be a composition of hooks on one base system. Eight experiments: frozen-hole robustness (1), policy comparison (2), noisy perception (3), view radius (4), chimeric policies (5), recovery after damage (6), progressive vs sudden damage (7), misleading holes (8). All at n = 30 seeds, 500 steps, paired t-tests with matched seeds.

## Reproducing

From `simulation/`: `uv run --script run.py all` regenerates the eight result files; `analyze_stats.py all` reproduces the paired-t tables and Spearman correlations; `visualize.py` regenerates the plots. Every headline number reconciles against `CLAIM_LEDGER.md`.

## The freeze semantics (why Experiments 6 and 7 were reframed)

`perturbations.py` freezes a hole by setting its status to FROZEN; `model.py` then rejects incoming placement attempts on frozen holes but does not eject a hole's current occupant. So a hole that is occupied when it freezes keeps contributing to coverage, and dynamic freezing (Experiments 6 and 7) removes no coverage: overload stays at its converged value. Static freezing (Experiment 1) sets frozen holes at initialization, before any pigeon is placed, so it genuinely reduces coverage. The 2026-07 revision makes this asymmetry explicit and retracts the "recovery" and "stress inoculation" readings that assumed dynamic damage perturbed the overload state.

## Open threads (from the referee passes, not run here)

The reviews ask for measurements this study does not make: a load-balance objective (potential regret `Φ − Φ*` or reaching the majorization-optimal vector `(2,2,2,1,1,1,1)`) instead of coverage; null policies (random relocation, stay-put, anti-greedy, a centralized optimum) to separate what random search achieves from what the load bias adds; hard (non-random) initial conditions; a scaling sweep in `n` and `m/n` to turn "pattern bandwidth" into an operational threshold; a freeze semantics that ejects or relocates incumbents so recovery can be measured; and memory-augmented agents to test the transition from structural convergence to learning. These are recorded in the paper's Limitations and Future Work, not performed.
