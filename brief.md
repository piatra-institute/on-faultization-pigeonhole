# Brief

## What this paper is

A perturbation study of the pigeonhole principle reinterpreted as a distributed multi-agent system: `m = 10` memoryless pigeons place themselves into `n = 7` holes under four local policies (GREEDY, EXPLORATORY, REPULSIVE, COOPERATIVE), with no central controller. Eight experiments degrade the interface between the agents and the constraint (frozen holes, perceptual noise, view radius, mixed policies, dynamic damage, and deceptive "misleading" holes) and read the results through Levin's (2026) "Platonic space" vocabulary, used as an organizing lens rather than an asserted ontology.

## The claim it actually defends

On this one system (m = 10, n = 7, 500 steps, n = 30 seeds):

1. A short identity governs everything: with all pigeons placed, overload `O = m − H` for `H` occupied holes, so reaching the theoretical minimum `O_min = m − n = 3` is exactly complete coverage of the usable holes, not optimal load balancing. Local load-seeking policies are built to occupy empty holes, which is why they reach `O_min` in 6 of 8 experiments with zero variance.
2. Policies with identical endpoints diverge up to 5-fold in process cost (failed placements, same-target retry from 0.463 to 0.997). The agents are memoryless and do not learn to avoid faulty holes.
3. Deceptive feedback is the sharpest failure mode: a single misleading hole (14% of the substrate) captures 36% of pigeons and 66% of overload. This is the study's strongest result and needs no Platonic reading.

## Honest posture (what the 2026-07 revision enforces)

Two referee passes (`review-2026-06-18.md` and a second, more thorough review) flagged a tendency to dress a coverage result in stronger language ("optimal global coordination," "free lunch," "pattern-channeling") and two internal contradictions. The revision pulls every claim back to what the data show and fixes the concrete problems:

- Establishes `O = m − H` and re-reads "reaching O_min" as complete coverage, not optimal balancing, throughout.
- Corrects the optimal-state count (the surjection count `7!{10 brace 7} = 29,635,200`, about 10.5% of the placed states) and notes that the random start already sits near the target (expected initial overload about 4.5 against a minimum of 3), so the "10^9 states searched for free" framing overstates the work avoided.
- Retracts the Experiment 6 "recovery" and Experiment 7 "stress inoculation" readings: the dynamic freeze blocks new entries but keeps incumbents, so overload never changes (Exp 7 even converges at step 3.9, before damage at step 100). The measured effect is process cost, not recovery or reoptimization.
- Reframes the delayed-gratification index as a statistic of the global trajectory, not agent memory (the agents are memoryless), and marks the absence of stress inoculation as entailed by the architecture, not as evidence for pattern-channeling.
- Fixes statistics (Spearman pseudoreplication caveat with the across-means correction; noise-clipping bias; "no threshold" softened to "no detectable tolerance down to sigma = 0.5"; a single Cohen's d_z definition; the noise regression R^2 corrected from 0.96 to about 0.90) and citations (Aguilera 2000 not 2004; Taining Zhang / Adam Goldstein; Simon 1956 integrated; Wolpert & Macready 1997 added for the No-Free-Lunch disclaimer; "Table 0" removed).

## What it is not

Not a demonstration that a non-physical pattern is causal, and not a load-balancing result (the metric measures coverage). The paper keeps the Platonic vocabulary as an interpretation and states plainly that the experiments do not distinguish it from ordinary distributed computation on a structured state space.
