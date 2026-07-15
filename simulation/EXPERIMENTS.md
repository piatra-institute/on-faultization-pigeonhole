# Experiments Summary

Each experiment probes the interface between local policies and the pigeonhole pattern -- a mathematical truth (O_min = m-n) that the system channels from the latent space (Levin, 2026).

Most experiments use `m = 10` pigeons, `n = 7` holes, 500 steps, and `n = 30` repetitions with paired t-tests on matched seeds. Experiment 5 uses `m = 12`, `n = 8`.

| # | Name | Perturbation | Key Finding | Classification |
|---|------|--------------|-------------|----------------|
| 1 | Frozen Holes | Freeze 0-6 holes permanently | Pattern manifests fully up to 3 frozen holes; beyond that, interface bandwidth narrows and capacity limits dominate | Pattern bandwidth / Free lunch |
| 2 | Policy Comparison | Replace all pigeons with GREEDY, EXPLORATORY, REPULSIVE, or COOPERATIVE | All policies channel the same pattern, but failed placements vary by 5x and same-target retry ranges from 0.46 to 1.00 | Pattern plurality / Free lunch |
| 3 | Noisy Perception | Add Gaussian noise (`sigma = 0.5-5.0`) to perceived loads | Monotonic degradation with no noise buffer; even `sigma = 0.5` raises overload 12.2% (`rho = +0.638`) | Pattern fidelity (discrete) |
| 4 | View Radius | Restrict visibility to `r = 1, 2, 3, 5, 7` | Pattern manifests at all radii; wider radius only accelerates convergence (11.8 steps at `r = 1` vs 2.0 at `r = 7`) | Information geometry / Free lunch |
| 5 | Chimeric Policies | Split the population 50/50 between two policies | Pattern resonates across policy boundaries; same-policy pigeons cluster above chance (`0.738-0.796`) | Lateral pattern resonance |
| 6 | Recovery | Freeze hole `0` at step `167`, optionally heal at step `333` | Complete recovery with no hysteresis; the pattern is re-accessible after interface restoration | Bidirectional interface / Free lunch |
| 7 | Progressive vs Sudden Damage | Freeze 3 holes all at step `100` or one each at `100/200/300` | Both reach identical overload; gradual damage yields 26% fewer failed placements and lower repeat failure | Memoryless = pattern-driven |
| 8 | Misleading Holes | Mark 0-6 holes as misleading (report load `0`) | Most damaging perturbation: the interface actively inverts the pattern, concentrating load on deceptive substrate | Pattern corruption / inversion |

## Classification Key

| Category | Description | Experiments |
|----------|-------------|-------------|
| **Pattern manifestation / Free lunch** | The pattern manifests fully; the system receives optimal allocation without computing it | 1 (0-3 frozen), 2, 4, 6 |
| **Pattern fidelity** | How much interface degradation the pattern tolerates before manifestation degrades | 3 |
| **Pattern corruption / inversion** | The interface actively misleads, causing the system to channel a distorted pattern | 8 |
| **Pattern plurality** | Multiple interface types (policies) access the same pattern with equal fidelity | 2, 5 |
| **Information geometry** | Interface bandwidth controls trajectory shape, not pattern access | 4 |
| **Lateral pattern resonance** | The pattern propagates across heterogeneous interface types within a single system | 5 |
| **Bidirectional interface** | The pattern is re-accessible after interface restoration | 6 |
| **Memoryless = pattern-driven** | Convergence is driven by the pattern, not by learned history | 7 |
