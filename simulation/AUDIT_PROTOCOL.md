# September pigeonhole audit protocol

Written 5 September 2026 after full manuscript/code inspection and before any
new audit outcomes. This is an exploratory redesign, not preregistration or
replication of the old eight experiments.

## Model and common random inputs

Ten labeled items, seven labeled holes, 500 sequential activations, 30 independent
seed tapes numbered 6000–6029. SeedSequence-derived streams separately determine
two initial placement proposals per item, activated item indices, ordered
candidate permutations and standardized Gaussian noise for each hole/step.
Every condition within a seed receives the same corresponding tape. Candidate
radius means a random sample count, not spatial distance.

Initial uniform placement uses the first proposal, then the second if the first
is closed; if both are closed the item remains unplaced. All-open uniform starts
are independent uniform assignments. Concentrated starts put every item in hole0;
dynamic starts use a balanced cyclic assignment. Closed/misleading holes are
the first k labeled holes. No external dataset or model is downloaded.

## Rules and information

The main greedy rule chooses the lowest reported load and moves if that load
is strictly below its exact current load. An unplaced item accepts any chosen
candidate. Both compared load-based rules exclude the item's current hole from
relocation candidates, so a misleading self-report cannot count as a move.
The arrival-aware rule instead requires reported destination load + 1 to be
strictly below current load. This compares the cost of actually arriving.

The random rule selects the first candidate uniformly, without inspecting loads;
a self-selection is a no-op. Stay-put is the other null. Neither is meant to be
a competitive tuned allocation method. Greedy candidate reporting costs r
observations per activation; random and stay-put use no load observations.

A closed hole rejects admission and retains any existing occupants unless an
explicit eviction occurs. Its report is its actual load (zero if empty), so
availability is not announced by a load report. A misleading hole accepts but
reports zero. The retry control tries the next eligible visible candidate after
rejection within the same activation, with no persistent rejection memory.
It can spend more admission attempts; those are counted.

## Conditions

Healthy uniform and concentrated starts: stay, random, greedy and arrival-aware.

Static closures: greedy with k=0,1,4,5,6 and radius3; for k=5 also radius1,
radius7 and radius3 with within-activation retry. Static greedy k=0 is the
healthy uniform greedy control.

Perception: greedy and arrival-aware at sigma=0, 0.000001 and0.5, using
(a) truncation toward zero then clipping, matching the old noise operator;
(b) nearest-integer rounding then clipping; (c) unquantized signed reports.
The exact current load is unchanged in every variant. Sigma0 uses true integer
loads. Noise tapes are common; the representation and inequality are the
controlled differences. Tiny errors need not be harmless at a strict decision
boundary, even without quantization.

Misleading reports: one zero-reporting accepting hole for greedy and arrival-aware.
Compare each against its healthy uniform control. No crash/Byzantine hierarchy
is inferred from objectives with different admissible states.

Dynamic events from the same balanced start: control, close admission only,
and close admission with eviction. Hole0 closes after activation100 and reopens
after activation300. Record state immediately before and after each event,
unplaced counts and coverage thereafter, and event-specific replacement/coverage
latencies with censoring. Entry-only closure is not eviction.

## Outcomes and mathematical checks

Record unplaced items U, placed items P, occupied holes H, occupied accepting
and closed holes, O=P-H, maximum load, sum of squared loads Q and the original
assigned potential Phi=O+0.5*sum(excess squared)+10*U. Record whether all items are
placed and accepting holes covered. Conditional balance regret Q-Q* is reported
only when U=0 and no item remains in a closed hole. Q* distributes m items as
evenly as possible over accepting holes. A smaller O with U>0 is not better
allocation. No single score silently ranks all three failure semantics.

Record successful assignment changes, admission failures, candidate-load
observations, first coverage/balance times, last overload change and moves
after first coverage. Unreached times remain null. Last metric change is not
called convergence. Retain final assignments and dynamic trajectories.

Enumerate load vectors for m=10,n=7; independently check O=P-H, exact optimum
Q=16 and Phi=4.5, and the two equal-overload examples. Compute surjection and
balanced-assignment counts and the exact uniform-start expectations. For a move
from a to b, check Delta Q=2*(b-a+1): faithful greedy moves cannot raise Q, while
the arrival-aware rule requires strict improvement. This convex-cost identity
does not disappear at larger m,n.

## Declared primary comparisons

One Holm family of 12 paired two-sided t tests across the 30 tapes:

1. Uniform random minus greedy: final Q.
2. Concentrated-start random minus greedy: final Q.
3. Five closed holes, radius7 minus radius3: final U.
4. Five closed holes, retry minus no retry: final U.
5. Greedy tiny truncated noise minus honest greedy: final Q.
6. Greedy tiny rounded noise minus honest greedy: final Q.
7. Greedy tiny unquantized noise minus honest greedy: final Q.
8. Greedy sigma0.5 truncated minus rounded noise: final Q.
9. Arrival-aware tiny truncated noise minus honest arrival-aware: final Q.
10. One misleading hole minus honest, greedy: final O.
11. One misleading hole minus honest, arrival-aware: final O.
12. One misleading hole minus honest, arrival-aware: final Q.

Report paired effects and pointwise95% t intervals. Holm adjusts the test
probabilities, not the intervals. Degenerate paired differences receive the
degenerate sample interval; this is not population equivalence. No equivalence
margin is selected. Other summaries and event curves are descriptive. Uncertainty
concerns seed tapes on this toy model, not human or biological populations.

## Verification and artifacts

Regression tests check legacy semantics and new transitions, exact invariants,
pairing, event timing, censoring, cost accounting, numerical/statistical helpers,
and the noise conversion. The full run fails if required tests fail or results
are nonfinite. Execution success is separate from scientific outcomes.

Write new results and figures under output/september-audit. Refuse an existing
results.json and any destination inside legacy results/. Use the collection
execution recorder with this protocol as an explicit input. Existing legacy
results remain untouched and are not used as the new audit's evidence.
