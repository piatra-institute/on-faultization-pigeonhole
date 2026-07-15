# Detailed Findings

## Setup

- **Base model**: `m = 10`, `n = 7`, 500 steps, asynchronous activation
- **Exception**: Experiment 5 uses `m = 12`, `n = 8`
- **Statistical protocol**: paired t-tests with matched seeds, `n = 30` per condition
- **Primary metrics**: final overload, overload ratio, convergence step, failed placements
- **Learning-like metrics**: post-failure same-target retry, post-failure repeat-failure rate
- **Bias metrics**: misleading-hole occupancy share/bias, misleading-hole overload share/bias, misleading load gap
- **Negative result retained**: DG index is `0.0` in all conditions


## Experiment 1: Frozen Hole Robustness

**Perturbation**: Permanently freeze 0 through 6 holes.

| Condition | Overload | Ratio | Same-Target Retry | Repeat Failure | Classification |
|-----------|----------|-------|-------------------|----------------|----------------|
| frozen_0 | 3.00 | 1.000 | 0.000 | 0.000 | -- |
| frozen_1 | 4.00 | 1.000 | 0.542 | 0.542 | Tolerance |
| frozen_2 | 5.00 | 1.000 | 0.486 | 0.985 | Tolerance |
| frozen_3 | 6.00 | 1.000 | 0.309 | 0.929 | Tolerance |
| frozen_4 | 6.47 | 0.924 | 0.247 | 0.985 | Structural Constraint |
| frozen_5 | 2.50 | 0.313 | 0.198 | 1.000 | Structural Constraint |
| frozen_6 | 1.57 | 0.174 | 0.162 | 1.000 | Structural Constraint |

- **Key finding**: The pattern manifests fully through the interface for 0-3 frozen holes, then the interface bandwidth narrows sharply at frozen_4 and beyond. The system channels the pigeonhole pattern (O_min = m-n) without needing to compute it, receiving optimal allocation as a free lunch from the latent structure.
- **Learning-like finding**: There is little evidence of negative learning from rejection. When only one hole is frozen, pigeons retry the same faulty target on their next attempted move 54% of the time. With multiple frozen holes, repeat failure approaches 100%, meaning agents keep colliding with damaged substrate rather than learning to avoid it.
- **Classification**: Pattern bandwidth / Free lunch (frozen_0 through frozen_3), Pattern bandwidth limit (frozen_4 through frozen_6)


## Experiment 2: Policy Comparison

**Perturbation**: Replace the default policy with GREEDY, EXPLORATORY, REPULSIVE, or COOPERATIVE under `1` frozen hole.

| Policy | Overload | Failed Placements | Same-Target Retry | Repeat Failure | Convergence Step |
|--------|----------|-------------------|-------------------|----------------|-----------------|
| GREEDY | 4.0 | 212.1 | 0.542 | 0.542 | 7.4 |
| EXPLORATORY | 4.0 | 460.3 | 0.940 | 0.940 | 39.8 |
| REPULSIVE | 4.0 | 84.6 | 0.463 | 0.463 | 8.8 |
| COOPERATIVE | 4.0 | 168.3 | 0.997 | 0.997 | 7.6 |

- **Key finding**: All four policies reach identical final overload, but process cost diverges sharply. Failed placements vary by more than 5x, and post-failure persistence varies even more. The pigeonhole pattern is indifferent to which local policy serves as its interface -- it manifests identically through each, a free lunch that every policy receives without paying for it.
- **Learning-like finding**: The strongest evidence against agent-level learning appears here. After rejection, EXPLORATORY retries the same frozen hole 94% of the time and COOPERATIVE nearly 100% of the time. REPULSIVE is the least persistent, but still retries 46% of the time.
- **Classification**: Pattern plurality / Free lunch. The pattern is accessible through multiple interface types; outcome equivalence coexists with sharp differences in fault susceptibility and retry persistence.


## Experiment 3: Noisy Perception

**Perturbation**: Add Gaussian noise (`sigma = 0.5, 1.0, 2.0, 5.0`) to perceived hole loads.

| Condition | Overload Change | p-value | Cohen's d |
|-----------|----------------|---------|-----------|
| noise_0.0 | -- | -- | -- |
| noise_0.5 | +12.2% | 0.0011** | 0.66 |
| noise_1.0 | +17.8% | <0.0001*** | 1.05 |
| noise_2.0 | +28.9% | <0.0001*** | 1.38 |
| noise_5.0 | +43.3% | <0.0001*** | 1.85 |

- **Spearman correlation** (noise vs overload): `rho = +0.638`, `p < 0.0001`
- **Key finding**: Monotonic degradation with no noise buffer. The interface between agents and the pigeonhole pattern is fragile in the discrete-noise regime: any corruption of the sensory channel immediately reduces pattern fidelity, degrading allocation quality.
- **Classification**: Pattern fidelity (discrete). The pattern tolerates zero interface noise before degradation begins.


## Experiment 4: View Radius

**Perturbation**: Restrict visibility to radius `r in {1, 2, 3, 5, 7}`.

| Radius | Overload | Convergence Step | Change vs radius_1 | p-value |
|--------|----------|------------------|--------------------|---------|
| 1 | 3.0 | 11.8 | -- | -- |
| 2 | 3.0 | 6.0 | -49% | 0.0093** |
| 3 | 3.0 | 3.9 | -67% | 0.0001*** |
| 5 | 3.0 | 2.3 | -81% | <0.0001*** |
| 7 | 3.0 | 2.0 | -83% | <0.0001*** |

- **Key finding**: Information scope affects speed, not destination. Even radius_1 reaches the optimum. The pigeonhole pattern manifests regardless of how narrow the local information window is -- a free lunch the system receives even under severe information restriction. The geometry of convergence changes, but the pattern's accessibility does not.
- **Classification**: Information geometry / Free lunch. The interface bandwidth controls trajectory shape, not pattern access.


## Experiment 5: Chimeric Policies

**Perturbation**: Split the population 50/50 between two policies (`m = 12`, `n = 8`).

| Policy Pair | Overload | Aggregation Index |
|------------|----------|-------------------|
| GREEDY + COOPERATIVE | 4.0 | 0.738 |
| GREEDY + EXPLORATORY | 4.0 | 0.738 |
| EXPLORATORY + COOPERATIVE | 4.0 | 0.754 |
| REPULSIVE + COOPERATIVE | 4.0 | 0.796 |

- **Key finding**: Mixed-policy populations are as effective as homogeneous ones, but they self-segregate above chance by policy type. The pigeonhole pattern resonates laterally across policy boundaries -- agents with incompatible local rules still collectively channel the same mathematical truth, while their spatial segregation reveals a secondary emergent structure.
- **Classification**: Lateral pattern resonance. The pattern propagates across heterogeneous interface types within a single system.


## Experiment 6: Recovery After Damage

**Perturbation**: Freeze hole `0` at step `167`, optionally heal it at step `333`.

| Condition | Overload | Failed Placements | Same-Target Retry | Repeat Failure |
|-----------|----------|-------------------|-------------------|----------------|
| control | 3.0 | 0.0 | 0.000 | 0.000 |
| damage_only | 3.0 | 49.4 | 0.257 | 0.257 |
| damage_and_heal | 3.0 | 24.7 | 0.226 | 0.211 |

- **Key finding**: Final overload is unchanged by damage history, and healing halves wasted actions. The interface is bidirectional: the pattern can be disrupted when holes freeze, then fully re-accessed when the interface is restored. The system receives optimal allocation as a free lunch both before damage and after healing.
- **Learning-like finding**: Post-failure persistence is much lower here than in the static frozen-hole experiments, but still not zero. The system reorganizes around damage, yet individual pigeons still show some retry persistence instead of explicit avoidance memory.
- **Classification**: Bidirectional interface / Free lunch. Complete recovery with no hysteresis at the outcome level; the pattern is equally accessible before and after interface restoration.


## Experiment 7: Progressive vs Sudden Damage

**Perturbation**: Freeze 3 holes either all at step `100` (sudden) or one each at steps `100`, `200`, and `300` (gradual).

| Condition | Overload | Failed Placements | Same-Target Retry | Repeat Failure |
|-----------|----------|-------------------|-------------------|----------------|
| sudden | 3.0 | 173.5 | 0.249 | 0.744 |
| gradual | 3.0 | 128.9 | 0.253 | 0.639 |

- **Key finding**: The endpoint is identical, but gradual damage produces 26% fewer failed placements. The system is memoryless yet pattern-driven: it has no record of past damage, yet it channels the pigeonhole pattern with equal fidelity whether damage arrives suddenly or gradually.
- **Learning-like finding**: Same-target retry is unchanged, but repeat failure is significantly lower under gradual damage. The system’s path gets smoother without acquiring actual memory.
- **Classification**: Memoryless = pattern-driven. The temporal profile of interface damage changes disruption cost, not pattern access. The system’s convergence is driven by the pattern, not by learned history.


## Experiment 8: Misleading Holes

**Perturbation**: Mark 0-6 holes as misleading. Misleading holes still accept pigeons but always report load `0`.

| Condition | Overload Change | Occupancy Bias | Overload Bias | Load Gap |
|-----------|----------------|----------------|---------------|----------|
| misleading_1 | +25.6% | +0.217 | +0.518 | +2.533 |
| misleading_2 | +40.0% | +0.274 | +0.559 | +1.920 |
| misleading_3 | +44.4% | +0.265 | +0.511 | +1.544 |
| misleading_4 | +46.7% | +0.219 | +0.418 | +1.275 |
| misleading_5 | +45.6% | +0.156 | +0.286 | +1.090 |
| misleading_6 | +43.3% | +0.080 | +0.143 | +0.928 |

- **Spearman correlation** (misleading count vs overload): `rho = +0.417`, `p < 0.0001`
- **Bias finding**: A single misleading hole occupies just 14% of the substrate but captures 36% of pigeons and 66% of overload. With two misleading holes, deceptive substrate captures 56% of pigeons and 85% of overload.
- **Key finding**: Misleading holes do not just increase overload; they actively corrupt the interface, inverting the pattern. The system no longer channels the pigeonhole optimum -- instead, the deceptive substrate redirects the collective toward a distorted attractor where load concentrates precisely where it should not.
- **Classification**: Pattern corruption / inversion. The interface does not merely degrade (as with noise); it actively misleads, causing the system to channel a corrupted version of the pattern.


## Cross-Experiment Summary

| Pattern | Experiments | Interpretation |
|---------|-------------|----------------|
| Pattern manifestation (free lunch) | 1 (frozen 0-3), 2, 4, 6 | The pigeonhole pattern manifests fully through the interface; the system receives optimal allocation without computing it |
| Pattern plurality | 2, 5 | Multiple interface types (policies, mixed populations) access the same pattern with equal fidelity |
| Pattern fidelity | 3 | The interface tolerates zero noise; any sensory corruption degrades pattern access |
| Pattern corruption | 8 | Deceptive substrate inverts the pattern, redirecting the collective toward a distorted attractor |
| Memoryless pattern-driven convergence | 7 | The system converges without history; the pattern, not learned memory, drives the endpoint |
| Bidirectional interface | 6 | The pattern is re-accessible after interface restoration with no hysteresis |
| Lateral resonance | 5 | The pattern propagates across heterogeneous policy boundaries within a single system |
| Fault persistence | 1, 2, 6, 7 | Rejected pigeons often retry faulty substrate instead of learning to avoid it |

The Platonic Space framing (Levin, 2026) reframes these results: the pigeonhole principle (O_min = m-n) is not computed by the agents but channeled from the latent mathematical structure through the agent-substrate interface. Faultization experiments probe what happens when that interface is narrowed (frozen holes), blurred (noise), restricted (view radius), diversified (policy mixtures), broken and restored (recovery), or actively corrupted (misleading holes). The system is strongly adaptive at the collective level not because agents learn, but because the pattern is robustly accessible through multiple interface configurations.
