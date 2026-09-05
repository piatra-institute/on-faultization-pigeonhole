> Historical report for the pre-September draft. It is preserved for provenance,
> not maintained as evidence for the revised manuscript. Use `claims.yaml` at
> the repository root, the September protocol and its new execution record.
> The old interpretation of convergence, noise, capacity and pattern access
> must not be treated as a current finding.

# Claim Ledger

Every numeric claim in `paper/PAPER.md` traced to the committed simulation output.
The experiments are seeded and deterministic; regenerate the entire trail from the
`simulation/` directory with:

```
uv run --script run.py all          # writes results/experiment{1..8}*.json
uv run --script analyze_stats.py all # paired t-tests, Cohen's d, Spearman rho
uv run --script visualize.py         # results/exp*.png
```

Regenerated 2026-05-29; all values below reproduce the paper exactly (the
results had simply never been committed). Base model `m=10, n=7` (so
`O_min = m − n = 3`), `n=30` reps, 500 steps, paired t-tests with matched seeds.
Note on interpretation (2026-07-15 revision): with all pigeons placed `O = m − H`
for `H` occupied holes, so reaching `O_min` is complete coverage of the usable
holes, not optimal load balancing; the rows below keep their values and are
re-read under that identity.

| # | Claim | Source | Value | ✓ |
|---|---|---|---|---|
| 1 | `O_min = m − n = 3` is the irreducible minimum overload | model + `experiment1_frozen_robustness.json` (frozen_0) | 3.00 | [x] |
| 2 | In six of eight experiments every run converges to the configuration's `O_min` with zero-variance final overload; the exceptions are noise (exp 3) and misleading holes (exp 8) | `experiment{1,2,4,5,6,7}*.json` | 3.0 / 4.0 endpoints, zero variance | [x] |
| 3 | Noise: monotonic degradation, no detectable tolerance down to the smallest σ tested (0.5); ρ = +0.638, p < 0.0001; OLS on the five means O ≈ 3.21 + 0.24σ, R² ≈ 0.90 | `experiment3_noisy_perception.json` | +12.2% (p=0.0011, d=0.66) → +43.3% (d=1.85) | [x] |
| 4 | View radius changes convergence speed, not destination (all reach `O_min=3`) | `experiment4_view_radius.json` | conv −49% / −67% / −81% / −83% | [x] |
| 5 | All four policies reach identical overload (4.0 under 1 frozen hole); process cost varies >5×; same-target retry 0.463 (REPULSIVE) → 0.997 (COOPERATIVE) | `experiment2_policy_comparison.json` | failed placements 84.6 → 460.3 | [x] |
| 6 | Chimeric mixed-policy populations reach the same endpoint (4.0); aggregation index 0.738–0.796, but every multiply-occupied hole holds exactly 2 pigeons so the correct chance baseline is 0.75 (not 0.5); no pair differs from 0.75 (one-sample t-test p = 0.56 / 0.54 / 0.84 / 0.10), so there is no self-organization beyond chance | `experiment5_chimeric.json` | 4.0 all pairs; agg vs 0.75 all n.s. | [x] |
| 7 | Recovery: all conditions end at 3.0 because dynamic freeze keeps incumbents (coverage never lost, so no overload recovery is demonstrated); the measured effect is process cost, healing halves wasted actions (49.4 → 24.7 failed placements) | `experiment6_recovery.json` | 3.0 endpoint; 49.4 → 24.7 | [x] |
| 8 | Progressive vs sudden damage: identical 3.0 endpoint (convergence at step 3.9, before damage at step 100, so damage removes no coverage); gradual yields 26% fewer failed placements (173.5 → 128.9); DG index 0 | `experiment7_progressive_damage.json` | 3.0 endpoint; 173.5 → 128.9 | [x] |
| 9 | Misleading holes invert the pattern: overload +25.6% → +46.7%; single misleading hole (14% of substrate) captures 36% of pigeons and 66% of overload; ρ = +0.417, p < 0.0001 | `experiment8_misleading_holes.json` | occupancy bias +0.217 → +0.080 | [x] |
| 10 | Delayed-gratification index = 0.0 only under faithful perception (exp 1, 2, 4, 5, 6, 7); it becomes non-zero when the interface corrupts perception: exp 3 mean DG 0.37 / 0.42 / 0.47 / 0.47 at σ = 0.5 / 1.0 / 2.0 / 5.0 (11 / 13 / 15 / 16 of 30 runs), exp 8 mean DG rising to 0.56 at 5 misleading holes (22 of 30 runs) | all experiments | DG = 0.0 clean; up to 0.56 under corruption | [x] |
