# Research record

## September 2026 revision

The original manuscript and core model were read in full before redesign. The
most important distinctions were missing placement versus lower overload,
pre-arrival versus arrival-aware costs, integer truncation versus rounding,
and entry-only closure versus eviction. A common random seed was not a common
activation tape when policy-specific operations consumed different draws.

The new audit protocol was written before its outcomes, after inspecting the
old code/results. It is exploratory, not preregistered. Thirty seed tapes
6000–6029, 500 activations and 32 conditions use separate paired random streams.
Twelve primary paired contrasts form one Holm family. Intervals remain pointwise.
Null events are censored, not assigned a false convergence time.

The recorded run on 5 September passed 26 tests and exact mathematical checks.
The original defaults and eight old result files were not changed. New evidence
is in `simulation/output/september-audit/`; its execution receipt identifies
inputs and outputs by hash. README-only changes do not alter execution semantics.

Primary-source scopes and limits are recorded in `source-checks.md`. The
manuscript uses the sorting study as motivation, congestion-game cost accounting
as context, and balanced allocation as a qualified comparison. None is evidence
for this model's newly measured results.

## Open questions

Larger m,n, finite capacities, service/arrival processes and correlated reporting
errors were not tested. Persistent rejection memory may improve placement at a
different information cost. Robustness after prior damage needs a matched later
challenge. No inference about learned intention follows from a score excursion.
These are research extensions, not prerequisites disguised as completed work.
