# Editorial revision: Pigeonhole

Status: complete locally, 5 September 2026. Full original 545-line manuscript read,
alongside the complete core model, perturbations and experiment definitions,
the relevant metrics, CLI, old ledger and referee report.

## Contribution and rival

A small allocation model can expose the difference between a mathematical
constraint, a chosen performance measure, and the information a placement rule
actually receives. The strongest rival to the old pattern-access interpretation
is the implemented transition rule itself. Empty-looking closed holes can trap
the rule; pre-arrival comparisons and integer conversion can magnify tiny
perception errors. These explanations are inspectable and testable.

## Preserve

Keep O = P - H; distinguish coverage from balance and unplaced work. Keep the
contrast between blocked admission and inaccurate load reports, but do not
describe the former as honest or equate either model with consensus under crash
or Byzantine faults. Keep process cost alongside final state. Keep the sorting
paper and Levin as motivation, with no claim to have tested a separate ontology.

## Reverse outline

The 600-plus-word abstract performs most of the argument before the paper starts.
The introduction and related work repeat the Platonic vocabulary and a seven-item
novelty list. Sixteen method/result subdivisions are followed by eight
Classification codas, another taxonomy, a free-lunch table, restated philosophy,
limitations that contradict earlier claims, and a long recap. Replace this
structure with a measurement-led account and a small number of diagnostic
experiments.

## Argument and implementation decisions

The theorem is not an allocation algorithm and forbids no state with unplaced
items. Equal overload can hide unequal concentration. The old convergence
statistic is the last overload change, not the last move or a stable assignment.
The load-seeking rule compares a destination's pre-arrival load with the current
load; at a one-item difference it permits neutral moves. Increasing system size
does not by itself create new local minima of unrestricted convex load cost.

Code uses max(0, int(load + noise)), which truncates toward zero, not nearest
rounding. The agent's own current load remains exact. Exploratory extra samples
bypass noisy/misleading reports; cooperative moves inspect true global potential.
A shared seed does not ensure a shared activation sequence when policies consume
different numbers of random draws. New comparisons must precompute independent
activation, candidate and noise tapes.

The claim that stateless agents rule out history effects is false: assignment
state can retain effects of earlier events. A nonmonotone path does not show
that a detour was necessary or that an agent delayed a reward. The old type
aggregation null does not establish equality or absence of self-organization.

## Separate audit

Before inspecting new outcomes, specify a bounded audit with new seeds,
null policies, a concentrated initial condition, distinct coverage/balance/
placement endpoints, a same-activation retry control, tiny-noise representation
controls, an arrival-cost comparison, and explicit close-versus-evict events.
Preserve the old code's default dynamics and all eight old result files.
The new audit is not a relabeled replication of the eight tables.

## Completed and remaining scope

The separate audit passed 26 regressions, mathematical checks and all required
execution stages on 5 September. Thirty paired tapes over 32 conditions reveal
the closed-hole trap, the separate truncation/decision-boundary effects and the
close-versus-evict distinction. All eight old JSON results and default dynamics
remain unchanged. Full numerical outcomes and an execution receipt are retained.

The revised manuscript has a 198-word abstract, six argument-led sections, two
figures and one compact table. Five primary references have disclosed source
checks; the Holm check is reused from the earlier GPT review in this session.
There are 121 selected, version-bound claim records. Every final PDF page was
rendered, individually inspected and reread. Six voice advisories were reviewed
as necessary technical distinctions, not mechanically removed.

Manuscript SHA-256: 49933f4005bbd6065950f0cf75ea0f08087bbd705bf462b550164168da7ce33b.
PDF SHA-256: 3d9828de2baeeabdc21a60e67120b9949091808212b68353641077ca65803c5f.

No required local editorial or experimental work remains. Commit/push review
is limited to the five finished repositories newly authorized by the user;
unrelated work and existing GPT deletions stay out. No live-site deployment.
