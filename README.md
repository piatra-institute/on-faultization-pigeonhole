# On Faultization: Pigeonhole Principle

Morphogenetic perturbation of the pigeonhole principle, reinterpreted as a distributed multi-agent placement system and read through Levin's (2026) proposal that physical systems are interfaces onto a latent space of mathematical patterns.

## Overview

The pigeonhole principle states that if `m > n` pigeons are placed into `n` holes, at least one hole must hold more than one pigeon. The theoretical minimum overload `O_min = m − n` is therefore a mathematical truth no allocation can beat. We treat this bound as a pattern the system reaches rather than computes: `m = 10` pigeons with local, memoryless policies place themselves into `n = 7` holes with no central controller.

A short identity governs the whole study. With all pigeons placed, overload equals `m − H` where `H` is the number of occupied holes, so reaching `O_min = m − n` is exactly complete coverage of the usable holes, not optimal load balancing. The load-seeking policies are built to occupy empty holes, which is why they reach it.

Eight experiments perturb the interface (removing capacity via frozen holes, blurring perception with noise, restricting information via view radius, mixing policies in chimeras, breaking and restoring holes, and lying about load with misleading holes) to see when coverage holds, degrades, or inverts.

## Key findings

- **Coverage from local rules.** Complete coverage (`O_min`) is reached in 6 of 8 experiments with zero variance, using only local load-seeking, up to 43% substrate loss.
- **Endpoint equals coverage, not balance.** Because `O = m − H`, reaching `O_min` measures hole coverage; two very differently balanced configurations can share the same overload.
- **Process cost diverges.** Policies with identical endpoints differ up to 5-fold in failed placements and in same-target retry (0.463 REPULSIVE to 0.997 COOPERATIVE); the agents are memoryless and do not learn to avoid faulty holes.
- **Discrete fidelity.** Perceptual noise degrades coverage immediately, with no detectable tolerance down to the smallest noise tested (sigma = 0.5).
- **Deceptive feedback is the sharpest failure.** A single misleading hole (14% of the substrate) captures 36% of pigeons and 66% of overload; this deceptive-feedback result is the study's strongest and needs no Platonic reading.
- **Dynamic damage removes no coverage.** In the recovery and progressive-damage experiments the dynamic freeze blocks new entries but keeps incumbents, so overload never changes; the real effect is process cost, with fault duration and schedule changing wasted attempts rather than the endpoint.

## Layout

```
on-faultization-pigeonhole/
├── paper/
│   └── PAPER.md              # the manuscript (PAPER.pdf built via ./papers build)
├── simulation/               # all code, results, and detailed write-ups
│   ├── model.py, perturbations.py, experiments.py, metrics.py
│   ├── run.py, analyze_stats.py, visualize.py
│   ├── results/              # committed JSON (PNG plots gitignored)
│   ├── EXPERIMENTS.md, FINDINGS.md, README.md
│   └── data/                 # reference material (gitignored)
├── CLAIM_LEDGER.md           # every numeric claim traced to committed output
├── metadata.yaml, audit.md, brief.md, sources.md, research.md
└── review-2026-06-18.md      # external referee pass
```

## Quick start

Run from the `simulation/` directory:

```bash
uv run --script run.py test              # smoke test
uv run --script run.py all               # all 8 experiments
uv run --script analyze_stats.py all     # paired t-tests + summary
uv run --script visualize.py             # plots
```

## Documentation

- `paper/PAPER.md` -- the full manuscript, with methods, results, and discussion
- `simulation/FINDINGS.md` -- detailed per-experiment results
- `simulation/EXPERIMENTS.md` -- concise experiment summary
- `CLAIM_LEDGER.md` -- numeric-claim ledger

## References

Levin, M. (2026). A short argument on Platonic Space. Blog post, March 31, 2026.

Zhang, T., Goldstein, A., & Levin, M. (2024). Classical sorting algorithms as a model of morphogenesis: self-sorting arrays reveal unexpected competencies in a minimal model of basal intelligence. arXiv:2401.05375.
