---
title: |
  On Faultization:\
  Pigeonhole Principle.\
  What Perturbation Reveals About Pattern\
  Access Under Irreducible Constraint
author: PIATRA . INSTITUTE
date: March 2026
---

## Abstract

We apply faultization (a systematic regime of morphogenetic perturbation) to the pigeonhole principle reinterpreted as a distributed multi-agent system, asking which patterns from the latent space (Levin, 2026) the system accesses under irreducible constraint. The pigeonhole principle is itself a pattern in the Platonic Space: the theoretical minimum overload $O_{\min} = m - n$ is a mathematical truth that the system channels without computing. In our model, $m = 10$ autonomous pigeons self-organize into $n = 7$ holes under four local placement policies (GREEDY, EXPLORATORY, REPULSIVE, COOPERATIVE), with no centralized controller. Because $m > n$, overload $O \geq m - n = 3$ is irreducible; the system cannot solve the problem, only manage it. We subject this system to eight perturbation experiments ($n = 30$ replications, 500 steps, paired $t$-tests with matched seeds): frozen-hole robustness, policy comparison, noisy perception, view-radius sweep, chimeric mixed-policy populations, dynamic damage and recovery, progressive versus sudden damage, and misleading (deceptive) holes. We classify findings into four categories. *Pattern manifestation*: every run reaches $O_{\min}$ in six of eight experiments. Because $O = \sum_i \max(0, \ell_i - 1) = m - H$ whenever all pigeons are placed (with $H$ the number of occupied holes), reaching $O_{\min} = m - n$ is exactly complete coverage of the usable holes rather than optimal load balancing, and the load-seeking policies are built to cover empty holes. *Pattern fidelity*: perceptual noise causes immediate monotonic degradation with no detectable tolerance down to the smallest noise tested ($\sigma = 0.5$; $\rho = +0.638$, $p < 0.0001$), revealing that this discrete interface requires high-fidelity perception to transmit the pattern. *Pattern corruption*: misleading holes invert the pattern-seeking mechanism, with a single misleading hole capturing 36\% of pigeons and 66\% of overload and increasing total overload by 25.6\%; this deceptive-feedback result is the study's strongest. *Free lunch*: we use Levin's (2026) philosophical sense of "free lunch," distinct from the technical No-Free-Lunch theorem (Wolpert and Macready, 1997); $O_{\min}$ is computable in constant time and the local dynamics are themselves a distributed computation over the shared occupancy field, so what the system exhibits is efficient exploitation of problem structure rather than optimization at no cost. Policies that are identical at the endpoint differ dramatically in failure persistence, with same-target retry after rejection ranging from 0.463 (REPULSIVE) to 0.997 (COOPERATIVE), indicating that convergence is driven by the funnel structure of the state space and the load-seeking policies rather than by agent-level learning (the agents are memoryless). Delayed gratification, a trajectory statistic rather than a sign of agent memory, is zero whenever perception is faithful (the six clean structural experiments, where convergence is monotone) and becomes non-zero precisely when the interface corrupts perception, with the mean DG Index rising from 0 to between 0.37 and 0.47 under noisy perception (non-zero in 11 to 16 of 30 runs) and up to 0.56 under misleading holes (non-zero in 22 of 30 runs). Because the agents are memoryless, this non-zero DG index reflects path-dependence of the global state under corrupted perception rather than accumulated agent experience: convergence is monotone when perception is faithful and passes through transiently worse states when it is not. We further find that the apparent chimeric self-organization in mixed-policy populations is a baseline artifact: every multiply-occupied hole holds exactly two pigeons, for which the correct chance level of same-policy co-location is 0.75 rather than 0.5, and the observed aggregation scores (0.738 to 0.796) do not differ significantly from 0.75.


## 1. Introduction

Levin (2026) argues that physical systems serve as interfaces for a non-physical space of patterns, the Platonic Space, whose denizens are discovered rather than created and are causal in physics, biology, and computer science. Under this framework, evolution exploits mathematical patterns as affordances it does not need to pay for: "once you find a voltage-gated ion channel, you have a transistor which can make logic gates, and truth tables are yours for free." The Platonic Space offers what Levin calls "free lunches": useful patterns for which the physical processes of learning, evolution, and engineering do not need to pay, or pay some but receive much more than the effort they put in.

The pigeonhole principle provides the cleanest possible test of this framework. The principle states that if $m$ items are placed into $n$ containers and $m > n$, then at least one container must hold more than one item. Formally, for any function $f: A \to B$ with $|A| > |B|$, $f$ cannot be injective. The theoretical minimum overload $O_{\min} = m - n$ is a mathematical truth, a pattern in the Platonic Space. Under the Platonic Space framework, the question becomes: when a distributed system of memoryless agents faces this irreducible constraint, does the mathematical truth $O_{\min}$ manifest through the physical interface? And if so, what does that manifestation cost?

The answer, as we show, is that local policies reliably reach $O_{\min} = 3$ in six of eight experimental conditions with no representation of the global optimum, no communication channel, and no memory. This is a free lunch in Levin's sense, and we mean his broad philosophical sense rather than the technical No-Free-Lunch theorem (Wolpert and Macready, 1997), which concerns performance averaged over a class of objective functions. We are careful about what "for free" can mean here. Reaching $O_{\min} = m - n$ turns out to be equivalent to covering every usable hole at least once (Section 3.1), $O_{\min}$ itself is computable in constant time, and the sequence of local queries, moves, and rejections is itself a distributed computation over the shared occupancy field. What the system demonstrates is that ordinary load-seeking rules exploit this structure without any agent representing it, not that global coordination arrives at zero cost.

Yet the pigeonhole principle describes a situation ubiquitous in distributed systems: too many agents competing for too few resources. Cells competing for niches in a tissue, packets competing for bandwidth in a network, vehicles competing for lanes on a highway, job seekers competing for positions in a labor market, all face pigeonhole-type constraints where some degree of conflict is structurally inevitable. In each of these settings, the mathematical impossibility of conflict-free allocation is a given. The operationally important question is: how faithfully does the physical interface transmit the mathematical truth $O_{\min}$, and what happens when we degrade that interface?

Faultization, systematic morphogenetic perturbation, is the methodology for answering this question. We use the term in the sense of Zhang, Goldstein, and Levin (2024): systematically breaking the assumptions of a nominal algorithm to read out the latent competencies of the underlying collective. It is related to fault injection and mutation testing in software engineering, but the aim differs. Those methods inject faults to measure defect detection or test-suite adequacy, whereas faultization injects them to observe what problem-solving behavior survives, degrades, or inverts. By perturbing the interface between algorithm and pattern space, we probe what patterns survive degradation, what fidelity the interface requires, and what happens when the interface actively misleads. The morphogenetic perturbation protocol, developed by Zhang, Goldstein, and Levin (2024) for sorting algorithms, proceeds in three stages: (1) formalize the target process as a decentralized system with explicit local policies, (2) systematically perturb the system by breaking assumptions of the nominal process, and (3) classify the resulting behaviors. We apply all three stages to the pigeonhole principle across eight experiments.

The unique advantage of the pigeonhole system for testing the Platonic Space framework is that the pattern is a known theorem. In sorting, the "pattern" is the correct permutation, which is complex and domain-specific. In the pigeonhole system, the pattern is $O_{\min} = m - n$: a single number derived from a theorem every undergraduate knows. This makes free-lunch quantification precise. We can state what the system receives (optimal overload) and what it pays (local greedy computation with no global information). The gap between payment and receipt is the free lunch.

We classify findings into four categories that map directly onto the Platonic Space framework:

1. **Pattern manifestation**: the mathematical pattern $O_{\min}$ successfully manifests through the interface. The system converges to the theoretical minimum overload using only local rules, channeling a global mathematical truth without computing it.
2. **Pattern fidelity**: how much interface degradation the pattern tolerates before failing to manifest. Different interface types (discrete vs continuous) have different fidelity requirements for the same kind of pattern.
3. **Pattern corruption**: the interface actively misleads, inverting the pattern-seeking mechanism. The same machinery that efficiently finds the optimum now efficiently finds the wrong target.
4. **Free lunch**: what the system receives without paying for. Optimal overload, damage compensation, recovery, and self-organization all arrive without global optimization.

Our contributions are as follows:

- To our knowledge, this is the first test of Levin's Platonic Space framework using a system where the pattern is a known mathematical theorem ($O_{\min} = m - n$).
- We formalize the pigeonhole principle as a distributed multi-agent system with four local placement policies, a composite potential function, and a hook-based perturbation architecture that enables systematic intervention at every decision point.
- We conduct eight systematic experiments spanning substrate damage, perceptual noise, information radius, policy heterogeneity, dynamic damage/recovery, and substrate deception, with paired statistical analysis and new process metrics for post-failure persistence and deceptive-substrate bias.
- We show that local policies reach the minimum overload $O_{\min}$, equivalently complete coverage of the usable holes, in six of eight conditions without any agent computing it.
- We show that pattern corruption (misleading holes) is categorically more harmful than pattern unavailability (frozen holes), and that the same pattern-seeking mechanism that produces the free lunch becomes a liability under deception.
- We characterize the delayed-gratification index as a property of the global trajectory rather than of agent memory: it is zero when convergence is monotone (faithful perception) and non-zero when corrupted perception (noisy and misleading conditions) forces the collective through transiently worse states. Because the agents are memoryless, the absence of stress inoculation is entailed by the architecture rather than being independent evidence for pattern-channeling.
- To our knowledge, this is the first morphogenetic perturbation analysis of an impossibility theorem, extending the framework from solvable problems (sorting, training) to fundamentally unsolvable ones.


## 2. Related Work

### 2.1 Levin's Platonic Space Framework

Levin (2026) proposes that physical systems serve as interfaces for a Platonic Space of non-physical patterns that are discovered, not created, and are causal in physics, biology, and computer science. The framework rests on several claims. (1) Some facts are not physical facts (truths of topology, the distribution of primes, the contents of discrete mathematics) and cannot be found using the tools of physics. (2) These patterns are causal in Judea Pearl's counterfactual sense: if the prime distribution were otherwise, cicadas would emerge at different years. (3) Physical bodies (embryos, cyborgs, computers) function as interfaces through which the patterns manifest. (4) The Platonic Space offers "free lunches": useful patterns for which physical processes do not need to pay, because "no free lunch" commitments are derived from the laws of the physical world, not from the pattern space.

The framework suggests a specific research program: build interfaces and study what unexpected patterns ingress through them that are not well-explained by their history of selection, engineering, or learning from experience. Levin notes that "biology offers the most sophisticated patterns, but it's very hard to prove anything in biology, so we're also making minimal computational models where we can more easily quantify the effort put in and the outcome we observed." Our pigeonhole system is such a minimal computational model: the effort put in (local greedy policies with no global information) and the outcome observed (convergence to the theoretical minimum $O_{\min} = m - n$) are both quantifiable, making free-lunch measurement possible.

### 2.2 Morphogenetic Perturbation of Algorithms

Zhang, Goldstein, and Levin (2024) introduced the methodology of treating classical algorithms as morphogenetic systems: decentralized collectives of elements executing local policies under imperfect conditions. Applied to sorting, this approach revealed that even minimal systems exhibit error correction, damage compensation, delayed gratification, and chimeric self-organization behaviors not specified by the original algorithm. Under the Platonic Space framework, these competencies can be reinterpreted as pattern manifestation: the correct sort order is a pattern that the system channels through the interface of local comparison-swap rules, and faultization probes how faithfully the interface transmits that pattern under degradation. The morphogenetic perturbation protocol they establish proceeds by systematically breaking assumptions of the nominal process, recording full trajectories, and classifying the resulting behaviors.

Our work extends this line to a qualitatively different setting: an impossibility theorem where the pattern is a known mathematical truth. While sorting is a solvable problem (there exists a correct sort), the pigeonhole principle with $m > n$ is inherently unsolvable. The pattern $O_{\min} = m - n$ is not a solution but a constraint, a mathematical fact about the minimum achievable conflict. This extension tests whether the Platonic Space framework produces meaningful results when the pattern is not a target to reach but a boundary that cannot be crossed. A loss minimum in gradient-based training would be a further solvable case; the pigeonhole boundary is not.

### 2.3 Multi-Agent Resource Allocation

The pigeonhole system is formally a congestion game (Rosenthal, 1973): agents select resources (holes), and payoffs decrease with congestion. Nash equilibria of congestion games are well-characterized, and the price of anarchy provides worst-case bounds on decentralized performance relative to the social optimum (Roughgarden and Tardos, 2002). Our system differs in that the social optimum itself represents an irreducible conflict state, not a conflict-free solution. In standard congestion games, the social optimum is typically conflict-free or conflict-minimal; in the pigeonhole system, even the optimal state has overload $\geq m - n$.

Load balancing in distributed systems (Azar et al., 1999) addresses the allocation of $m$ tasks to $n$ processors under local information. The "power of two choices" result shows that sampling just two random processors (rather than one) and choosing the less loaded one reduces maximum load from $\Theta(\log n / \log \log n)$ to $\Theta(\log \log n)$. Our view-radius experiment (Experiment 4) is loosely analogous: even a small increase in the number of visible holes accelerates convergence. The parallel is an analogy rather than the same theorem. The power-of-two-choices result concerns sequential one-pass allocation and asymptotic maximum load, whereas our system permits repeated relocation and measures overload, which becomes fixed once every hole is occupied.

The distributed task allocation literature also addresses fault tolerance (Aguilera et al., 2000), where processors may crash or behave adversarially. Our frozen-hole and misleading-hole experiments map directly onto crash faults (silent failure) and Byzantine faults (deceptive failure), respectively. Under the Platonic Space framework, these map onto pattern unavailability (the interface loses capacity but does not mislead) and pattern corruption (the interface actively inverts the pattern-seeking mechanism).

### 2.4 Basal Cognition Framework

Levin (2019) argues that cognitive competencies exist on a continuum: from molecular networks solving constraint satisfaction problems, through cellular collectives achieving morphogenetic goals, to neural systems supporting behavioral intelligence, and later work (Levin, 2022) develops this into an experimentally grounded framework spanning diverse bodies and minds. The key claim is that goal-directedness, error correction, and adaptive replanning are not exclusive to neural systems but appear at every scale of biological organization. Under the Platonic Space framework (Levin, 2026), these competencies can be understood as pattern manifestation: the "goal" is a pattern in the Platonic Space, and the biological system is an interface through which that pattern manifests with varying degrees of fidelity.

Our pigeonhole system instantiates this framework at the simplest possible level: agents with no memory, no communication channel, and no model of other agents, channeling a known mathematical truth ($O_{\min} = m - n$) through purely local policies. The impossibility constraint adds a distinctive feature: the target state (zero overload) is unreachable, so the system must manifest a pattern (minimum overload) that it has no explicit representation of. If the system reliably reaches $O_{\min}$ despite having no mechanism to compute it, that constitutes evidence for pattern-channeling in Levin's sense.


## 3. Methods

### 3.1 System Specification

The system consists of $m = 10$ pigeons and $n = 7$ holes. Each pigeon $k \in \{1, \ldots, m\}$ occupies a hole $x_k \in \{0, 1, \ldots, n\}$, where $x_k = 0$ denotes the unplaced state. The load of hole $i$ is $\ell_i = |\{k : x_k = i\}|$. The overload is defined as:

$$O(\mathbf{x}) = \sum_{i=1}^{n} \max(0, \ell_i - 1)$$

Since all pigeons must be placed and $m > n$, we have $O \geq m - n = 3$ for any fully-placed state. Under the Platonic Space framework, this bound is the pattern that the system channels: a mathematical truth about the irreducible minimum conflict.

**Overload equals resource coverage.** A short identity governs the interpretation of every result below. Writing $P = m - U$ for the number of placed pigeons and $H = |\{i : \ell_i > 0\}|$ for the number of occupied holes,

$$O = \sum_i \max(0, \ell_i - 1) = \sum_{\ell_i > 0} (\ell_i - 1) = \left(\sum_i \ell_i\right) - H = P - H.$$

When all pigeons are placed, $P = m$, so $O = m - H$, and therefore $O = m - n$ if and only if every hole is occupied. Reaching $O_{\min}$ is thus equivalent to touching every usable hole at least once. It does not measure how evenly the excess is spread: the balanced configuration $(2,2,2,1,1,1,1)$ and the concentrated one $(4,1,1,1,1,1,1)$ both have $O = 3$. This is why load-seeking policies reach $O_{\min}$ so reliably. They are built to move toward empty and low-load holes, which is exactly the behavior that maximizes $H$. Throughout the paper, then, "reaching the minimum overload" should be read as complete coverage of the usable holes, not as optimal load balancing. A genuine load-balancing target would be the majorization-optimal vector (here $(2,2,2,1,1,1,1)$), which additionally minimizes the maximum load and the sum of squared loads; we return to it in the potential function below and in the Limitations.

**Hole statuses.** Each hole has one of three statuses:
- ACTIVE: accepts pigeons and reports true load.
- FROZEN: silently rejects all placement attempts (pattern unavailability, the interface loses capacity).
- MISLEADING: accepts pigeons but reports load as 0 regardless of true occupancy (pattern corruption, the interface actively misleads).

**Potential function.** The system minimizes:

$$\Phi(\mathbf{x}) = \alpha \sum_{i=1}^{n} \max(0, \ell_i - 1) + \beta \sum_{i=1}^{n} [\max(0, \ell_i - 1)]^2 + \gamma \cdot U(\mathbf{x})$$

where $U(\mathbf{x}) = |\{k : x_k = 0\}|$ is the count of unplaced pigeons, and $\alpha = 1.0$, $\beta = 0.5$, $\gamma = 10.0$. The first term penalizes total overload, the second penalizes concentrated overload (encouraging even distribution of excess), and the third strongly penalizes leaving pigeons unplaced.

The potential $\Phi$ and the overload $O$ are not the same objective, and it matters which one a result is about. The two configurations above make the gap concrete: $(2,2,2,1,1,1,1)$ and $(4,1,1,1,1,1,1)$ share $O = 3$ but have squared-excess terms of 3 and 9, giving $\Phi = 4.5$ and $\Phi = 7.5$. $O$ measures coverage alone; $\Phi$ additionally measures concentration and unplaced pigeons. Three of the four policies act only on local load, and we report $O$ as the primary outcome throughout, so most results below speak to coverage rather than to $\Phi$-optimal balance. Reporting potential regret $\Phi - \Phi^\star$ would be the way to measure balance directly; we flag this as a limitation rather than change the primary metric mid-study.

**Local policies.** Each pigeon executes one of four policies based on local information. These are four different access methods for the same underlying pattern, four ways the interface can channel $O_{\min}$:

1. *GREEDY*: Inspect visible holes (determined by view radius $r$), move to the hole with lowest observed load if it is lower than the load of the pigeon's current hole. This is the simplest reasonable policy: purely self-interested, myopic load minimization. It is a satisficing rule in Simon's (1956) sense, accepting any strictly better hole rather than searching for the globally best one.
2. *EXPLORATORY*: Sample twice as many holes as the view radius permits ($\min(2r, n)$), then select the best. This policy trades computation (more sampling) for information, analogous to the "exploration vs exploitation" tradeoff in multi-armed bandits.
3. *REPULSIVE*: If the pigeon's current hole has load $\ell_i > 1$, escape with probability $(\ell_i - 1)/\ell_i$ and relocate greedily. If $\ell_i = 1$, stay. This policy implements a stochastic crowd-avoidance heuristic: the more crowded the hole, the more likely the pigeon is to flee.
4. *COOPERATIVE*: Evaluate the change in global potential $\Delta\Phi$ for each candidate move; move only if $\Delta\Phi < 0$. This is the only policy that considers the system-wide effect of its action, though it still acts locally (it cannot coordinate with other pigeons).

**Architecture.** The system uses a hook-based perturbation architecture that intercepts the nominal process at well-defined points, following the morphogenetic perturbation methodology of Zhang, Goldstein, and Levin (2024). Four named hook points provide interception at every stage of the pigeon decision cycle:
- `pigeon_view`: intercepts the list of visible (hole, load) pairs, enabling perturbations to perceived loads (noise, blindness, inversion).
- `pigeon_decision`: intercepts the chosen target hole, enabling perturbations to policy output (stubbornness, randomization, contrarianness).
- `placement_attempt`: intercepts the (pigeon, hole) pair before the frozen-hole check, enabling perturbations to the placement mechanism itself.
- `post_step`: intercepts the full system state after each step, enabling dynamic substrate changes (hole breaking, healing, progressive damage).

Each hook receives the current value and the step number, and returns either a modified value or `None` (pass-through). Multiple hooks can be chained on the same hook point. A probe records the complete trajectory: overload, potential, maximum load, unplaced count, load snapshots, and all move attempts with success/failure status. This architecture ensures that every experiment is implemented as a composition of hooks on the same base system, guaranteeing that all conditions share identical core dynamics.

**Dynamics.** At each step, one pigeon is activated uniformly at random, inspects a subset of holes determined by its view radius, applies its policy, and attempts placement. Frozen holes reject silently; misleading holes accept but misreport. The system runs for 500 steps after an initial random placement. This asynchronous activation scheme models real-world distributed systems where agents act independently and without synchronization.

**Theoretical minimum overload.** For a system with $n_u$ usable (non-frozen) holes and $m$ pigeons, the theoretical minimum overload is:

$$O_{\min}^{\text{theo}} = \max(0, m - n_u)$$

This follows from the observation that the maximum number of holes that can each hold exactly one pigeon is $\min(m, n_u)$, leaving $m - \min(m, n_u)$ excess pigeons when $m > n_u$. Misleading holes remain usable even though they corrupt perception. All experiments use this quantity as the normalization baseline for the overload ratio. Under the Platonic Space framework, $O_{\min}^{\text{theo}}$ is the pattern, the mathematical truth that the system either channels successfully or fails to channel.

This bound is conditional on all pigeons being placed. The state space explicitly permits unplaced pigeons ($x_k = 0$), and over that space the unconditional minimum of $O$ is zero, reached by leaving every pigeon unplaced. So $O_{\min}^{\text{theo}} = m - n_u$ is a lower bound given $U = 0$, not a floor the dynamics cannot pass. When heavy freezing forces $U > 0$ (Experiment 1 at five and six frozen holes), the overload ratio $O / O_{\min}^{\text{theo}}$ falls below 1 not because the system beat a mathematical bound but because the denominator is computed for full placement while the observed state leaves pigeons unplaced. Once $U > 0$, $O$ alone stops measuring allocation quality, so we report $U$ and $H$ alongside it.

**State space size.** The full state space has $(n + 1)^m$ configurations (each pigeon in one of $n$ holes or unplaced). For $m = 10$, $n = 7$, this is $8^{10} \approx 1.07 \times 10^9$. The minimum-overload states are exactly those in which all $n$ holes are occupied. Counting labelled pigeons placed onto $n$ nonempty labelled holes is the number of surjections from $m$ pigeons onto $n$ holes, $n!\,\lbrace{m \atop n}\rbrace$, where $\lbrace{m \atop n}\rbrace$ is a Stirling number of the second kind. For $m = 10$, $n = 7$ this is $7!\,\lbrace{10 \atop 7}\rbrace = 29{,}635{,}200$, about 2.8\% of the full $8^{10}$ space and about 10.5\% of the fully-placed $7^{10}$ space. We caution against reading this fraction as the difficulty of the problem. The dynamics do not sample states uniformly, and the initial random placement already starts close to the target: under independent uniform placement into 7 holes the expected initial overload is $10 - 7\,[1 - (6/7)^{10}] \approx 4.5$, only about 1.5 above the minimum of 3, and roughly one run in ten begins already at $O_{\min}$. Comparing the local process against exhaustive search over $\sim 10^9$ states therefore overstates the work avoided. $O_{\min} = m - n$ is computable in constant time, an optimal assignment is constructible in $O(m)$ time by placing one pigeon per hole and distributing the remainder, and the system begins near the target rather than at a representative hard state.

### 3.2 Statistical Protocol

All experiments use $n_{\text{rep}} = 30$ replications with matched random seeds across conditions. The primary statistical test is the paired $t$-test (two-tailed), which exploits seed-matching to control for initialization variance. Effect sizes are reported as Cohen's $d_z$ for paired designs: the mean difference divided by the standard deviation of the differences. For the seed-locked deterministic comparisons the difference variance is often near zero, which inflates $d_z$ to values in the tens (for example $d_z = +21.692$ in Experiment 2); we read those as almost non-overlapping distributions rather than as conventional effect magnitudes, and rely on the mean differences and raw counts for interpretation. Monotonic relationships are summarized with Spearman's rank correlation $\rho$. These $\rho$ values are computed over the pooled per-run observations, which share seeds across conditions, so we report them descriptively as trend summaries rather than as independent-sample tests. Where the condition means are themselves monotone, the across-means rank correlation is stronger than the pooled value: in Experiment 4 the five condition means are strictly decreasing, so the across-means $\rho$ is $-1$ while the pooled $\rho$ is $-0.494$. Significance thresholds follow convention: $* \; p < 0.05$, $** \; p < 0.01$, $*** \; p < 0.001$.

For Experiment 5 (chimeric policies), where different conditions involve different random policy assignments, we use Welch's independent $t$-test for between-pair comparisons.

The choice of paired $t$-tests (rather than independent-samples tests) is motivated by the seed-matching design: each condition is run with seeds $0, 1, \ldots, 29$, and the same seed produces the same initial random placement and activation sequence across conditions. This eliminates between-run variance due to initialization, substantially increasing statistical power. The pairing is particularly important for experiments where the effect of interest is small (e.g., Experiment 7, where overload is identical across conditions but failed placements differ).

We do not apply multiple-comparison corrections (e.g., Bonferroni) across experiments because each experiment tests a distinct hypothesis with distinct data. Within-experiment multiple comparisons (e.g., the 6 comparisons in Experiment 1) are noted but not corrected, as the primary findings involve effects with $p < 0.0001$ that would survive any reasonable correction.

All statistical computations use SciPy 1.x (`scipy.stats.ttest_rel` for paired tests, `scipy.stats.ttest_ind` with `equal_var=False` for Welch's test, `scipy.stats.spearmanr` for rank correlations).

### 3.3 Metrics

**Overload** $O$: the primary outcome metric, counting excess pigeons beyond one-per-hole capacity. Formally, $O = \sum_{i=1}^{n} \max(0, \ell_i - 1)$. For a fully-placed state with $m > n_u$ (usable holes), the minimum achievable overload is $m - n_u$.

**Overload ratio** $O / O_{\min}^{\text{theo}}$: final overload normalized by the theoretical minimum given the number of usable (non-frozen) holes. A ratio of 1.0 indicates that the mathematical pattern $O_{\min}$ has fully manifested through the interface.

**Post-failure same-target retry**: for every failed placement that is followed by another attempted placement by the same pigeon, we ask whether the next attempted target is the same faulty hole. High values indicate retry persistence and argue against agent-level learning from rejection.

**Post-failure repeat failure rate**: for every failed placement that is followed by another attempted placement by the same pigeon, we ask whether that next attempt also fails. This captures persistence on faulty substrate even when the pigeon switches from one frozen hole to another.

**Convergence step**: the last simulation step at which overload changes, indicating when the system reaches its final configuration.

**Failed placements**: the total number of placement attempts rejected by frozen holes over the full run. A process-level metric that distinguishes policies even when outcomes are identical.

**Misleading occupancy share / bias**: the fraction of pigeons occupying misleading holes at the end of the run, and that share minus the fraction of holes that are misleading. Positive bias means the corrupted interface attracts more load than its spatial share would predict.

**Misleading overload share / bias**: the fraction of total overload concentrated on misleading holes, and that share minus the fraction of holes that are misleading. This measures whether the corruption merely perturbs the system or actively captures the excess load it creates.

**Misleading load gap**: mean load on misleading holes minus mean load on honest holes.

**Policy aggregation score**: for chimeric (mixed-policy) populations, the fraction of co-located pigeons sharing the majority policy in each multiply-occupied hole. Computed as follows: for each hole with $\geq 2$ pigeons, count the pigeons belonging to the majority policy; sum these across all such holes and divide by the total number of pigeons in multiply-occupied holes. The correct chance baseline depends on hole occupancy, not on the naive $1/k$. For $k = 2$ policies and holes containing exactly $L$ pigeons assigned independently with equal probability, the expected same-policy fraction is the expectation of $\max(a, L-a)/L$ for $a \sim \text{Binomial}(L, 0.5)$: 0.75 for $L = 2$ or $L = 3$, 0.6875 for $L = 4$ or $L = 5$, and 0.6562 for $L = 6$. In our system the maximum hole load is 2 in every run, so the relevant chance baseline is 0.75, not 0.5. We test the observed scores against 0.75 with a one-sample $t$-test.

**Delayed Gratification (DG) Index**: retained for compatibility with the sorting literature, measuring episodes where overload temporarily increases and later falls below the prior local minimum. It is a statistic of the global overload trajectory, not a sign of agent memory, since the agents are memoryless. It is uniformly zero in the six experiments with faithful perception (Experiments 1, 2, 4, 5, 6, 7), where convergence is monotone, but it becomes non-zero precisely in the two experiments that corrupt perception (Experiment 3, noisy perception, and Experiment 8, misleading holes), where the system must climb out of a worse configuration to reach its final state.

### 3.4 Experiment Design

The eight experiments are designed to probe the interface between algorithm and pattern space along five perturbation axes: substrate integrity (Experiments 1, 6, 7), policy diversity (Experiments 2, 5), perceptual accuracy (Experiments 3, 8), information scope (Experiment 4), and temporal dynamics (Experiments 6, 7). Each experiment varies one axis while holding others constant, enabling attribution of effects to specific interface degradation types. The paragraphs that follow specify each experiment in turn.

**Experiment 1, Frozen Hole Robustness.** Freeze 0 through 6 holes (of 7 total), measuring overload ratio together with post-failure persistence. Tests the pattern bandwidth of the interface: how much substrate loss before the pattern $O_{\min}$ fails to manifest.

**Experiment 2, Policy Comparison.** All four policies under identical conditions ($m = 10$, $n = 7$, 1 frozen hole). Tests pattern plurality: whether different access methods channel the same underlying pattern.

**Experiment 3, Noisy Perception.** Add Gaussian noise $\mathcal{N}(0, \sigma^2)$ to perceived hole loads, with $\sigma \in \{0, 0.5, 1.0, 2.0, 5.0\}$. The noise is applied via the `pigeon_view` hook, adding independent Gaussian noise to each perceived load and clamping to non-negative integers. Tests pattern fidelity: what perceptual accuracy the discrete pigeonhole interface requires to transmit the pattern.

**Experiment 4, View Radius Sweep.** Vary the number of holes each pigeon can inspect per step: $r \in \{1, 2, 3, 5, 7\}$. At $r = 1$, each pigeon sees exactly one randomly sampled hole per step; at $r = 7$ (the total number of holes), each pigeon has full information. Tests the information geometry of pattern access: how much of the interface must be visible for the pattern to manifest, and how visibility affects convergence speed.

**Experiment 5, Chimeric Policies.** Mixed-policy populations ($m = 12$, $n = 8$), with each pigeon independently assigned one of two policies with equal probability. Four policy pairs are tested: GREEDY+COOPERATIVE, GREEDY+EXPLORATORY, EXPLORATORY+COOPERATIVE, and REPULSIVE+COOPERATIVE. Tests lateral pattern resonance: whether mixed-policy populations access the same pattern and whether same-policy agents cluster spatially as a free lunch.

**Experiment 6, Recovery After Damage.** Three conditions on the same system ($m = 10$, $n = 7$): (a) control with no damage, (b) freeze hole 0 at step 167, (c) freeze hole 0 at step 167 and heal it at step 333. Tests the bidirectionality of the pattern-substrate interface: whether the pattern re-manifests after both damage and healing.

**Experiment 7, Progressive vs Sudden Damage.** Freeze 3 holes (of 7) either all simultaneously at step 100 (sudden) or one at each of steps 100, 200, and 300 (gradual). Tests whether gradual exposure smooths disruption cost, and whether the absence of stress inoculation confirms pure pattern-channeling.

**Experiment 8, Misleading Holes.** Holes that report their load as 0 regardless of true occupancy, implemented via the MISLEADING hole status in the model. Vary from 0 to 6 misleading holes (of 7 total). Tests pattern corruption: what happens when the interface does not merely degrade but actively inverts the pattern-seeking mechanism.


## 4. Results

We present results for all eight experiments. Each experiment was run with $n = 30$ replications, 500 steps per run, and matched random seeds across conditions. We report means, significance levels ($p$-values from paired $t$-tests), and effect sizes (Cohen's $d$). For monotonic relationships, we report Spearman's rank correlation $\rho$. Each subsection concludes with a classification under the Platonic Space framework. Table 1 provides a cross-experiment summary; detailed results follow in subsections 4.1--4.8.

**Table 1. Cross-experiment summary.** All tests: two-tailed paired $t$-test, $n = 30$, seeds matched across conditions. Overload ratio $= 1.0$ indicates optimal performance.

| Experiment | Key Condition | Primary Metric | Value | $\Delta$\% | $p$ | $d$ |
|------------|--------------|----------------|-------|-----------|-----|-----|
| 1: Frozen Robustness | frozen\_3 | Overload ratio | 1.000 | $0.0$ | n.s. | $0.0$ |
| 1: Frozen Robustness | frozen\_5 | Repeat failure | 1.000 |, |, |, |
| 2: Policy Comparison | EXPLORATORY | Same-target retry | 0.940 | $+73.3$ | $< 0.0001$ | $+10.377$ |
| 3: Noisy Perception | $\sigma = 1.0$ | Overload | 3.53 | $+17.8$ | $< 0.0001$ | $+1.051$ |
| 4: View Radius | $r = 2$ | Convergence | 6.0 | $-48.7$ | $0.0093$ | $-0.509$ |
| 5: Chimeric | REP+COOP | Aggregation | 0.796 |, |, |, |
| 6: Recovery | damage\_and\_heal | Same-target retry | 0.226 |, |, |, |
| 7: Progressive | gradual | Repeat failure | 0.639 | $-14.1$ | $< 0.0001$ | $-2.153$ |
| 8: Misleading | misleading\_2 | Occupancy bias | 0.274 | +27.4pp | $< 0.0001$ | $+1.920$ |

### 4.1 Experiment 1, Frozen Hole Robustness: Pattern Bandwidth

Freezing holes reduces the number of usable holes from $n$ to $n - k$, raising the theoretical minimum overload from $m - n$ to $m - (n - k) = m - n + k$. The system must redistribute pigeons across fewer usable holes. Under the Platonic Space framework, this experiment probes the bandwidth of the interface: how much substrate can be removed before the pattern $O_{\min}$ fails to manifest.

| Condition | Final Overload | Overload Ratio | Same-Target Retry | Repeat Failure |
|-----------|---------------|----------------|-------------------|----------------|
| frozen\_0 | 3.0 | 1.000 | 0.000 | 0.000 |
| frozen\_1 | 4.0 | 1.000 | 0.542 | 0.542 |
| frozen\_2 | 5.0 | 1.000 | 0.486 | 0.985 |
| frozen\_3 | 6.0 | 1.000 | 0.309 | 0.929 |
| frozen\_4 | 6.47 | 0.924 | 0.247 | 0.985 |
| frozen\_5 | 2.50 | 0.313 | 0.198 | 1.000 |
| frozen\_6 | 1.57 | 0.174 | 0.162 | 1.000 |

**Key finding.** The system reaches full coverage of the usable holes (overload ratio $= 1.0$) for 0 through 3 frozen holes, so complete coverage survives up to 43\% substrate loss. No agent computes the global optimum; local load-seeking suffices to occupy every remaining hole even when nearly half the substrate is destroyed. At 4 frozen holes (57\% damage) coverage becomes incomplete (ratio $= 0.924$); at 5--6 frozen holes the ratio collapses because pigeons can no longer place (Section 3.1), not because a bound was crossed. The pooled Spearman correlation between frozen holes and overload ratio is $\rho = -0.1498$ ($p = 0.030$), but it pools per-run observations and the ratio is itself non-monotone (holding at 1 through frozen\_3, then falling), so it should be read as a descriptive summary only.

The process metrics show that this pattern manifestation is not driven by agent-level learning. With one frozen hole, pigeons retry the same faulty target on their next attempted move 54.2\% of the time. As more holes freeze, same-target retry falls because there are fewer distinct usable targets, but repeat failure rises to nearly 1.0: the system keeps colliding with faulty substrate even when it no longer insists on the same hole. The pattern channels the convergence to $O_{\min}$; agent-level learning does not.

Note on the overload ratio. The ratio falls below 1 at five and six frozen holes, and this is a denominator artifact rather than the system beating a bound. At frozen\_5 the conditional bound $O_{\min}^{\text{theo}} = m - (n - 5) = 10 - 2 = 8$ assumes all ten pigeons are placed, but the observed overload is only 2.50 because many pigeons never place at all: frozen holes silently reject placement, so $U > 0$ and $O$ stops measuring coverage (Section 3.1). The holes have no capacity cap. A single active hole can legally hold all ten pigeons, giving $O = 9$, so nothing physical prevents placement at frozen\_6. What fails is algorithmic: an empty frozen hole still reports a low load and so looks attractive to load-seeking pigeons, which attempt it and are rejected, cycling without settling. The collapse at five and six frozen holes is this silent-rejection mismatch, not a physical impossibility of placing ten pigeons into one hole.

The robustness curve changes character between frozen\_3 (full coverage) and frozen\_4 (partial coverage). At frozen\_3, the system still has 4 usable holes for 10 pigeons, giving a density of $10/4 = 2.5$ pigeons per hole and conditional minimum overload of 6. At frozen\_4, only 3 usable holes remain ($10/3 = 3.33$ density), and coverage becomes incomplete. We call this a change rather than a true phase transition. With only seven holes and a 500-step horizon, the drop at frozen\_4 could be a finite-horizon artifact, with pigeons still cycling against silent rejections when the run ends, rather than a genuine threshold; establishing a threshold would require the scaling sweep we describe in Future Work.

**Classification.** Perfect pattern manifestation at 0--3 frozen holes constitutes a *free lunch*: local policies channel the global mathematical truth $O_{\min}$ despite substrate damage, with no global computation. The degradation at 4+ frozen holes marks the *pattern bandwidth limit*: the interface has lost too much capacity to transmit the pattern faithfully. The critical threshold at approximately 43\% substrate damage defines the system's pattern bandwidth.


### 4.2 Experiment 2, Policy Comparison: Pattern Plurality

All four policies were tested with $m = 10$, $n = 7$, and 1 frozen hole (theoretical minimum overload $= 4$). Under the Platonic Space framework, this experiment tests pattern plurality: whether different access methods channel the same underlying mathematical truth.

| Policy | Final Overload | Failed Placements | Same-Target Retry | Convergence Step |
|--------|---------------|-------------------|-------------------|------------------|
| GREEDY | 4.0 | 212.1 | 0.542 | 7.4 |
| EXPLORATORY | 4.0 | 460.3 | 0.940 | 39.8 |
| REPULSIVE | 4.0 | 84.6 | 0.463 | 8.8 |
| COOPERATIVE | 4.0 | 168.3 | 0.997 | 7.6 |

**Same-target retry vs GREEDY baseline:**

| Policy | $\Delta$\% | $p$ | $d$ |
|--------|-----------|-----|-----|
| EXPLORATORY | $+73.3$\% | $< 0.0001$*** | $+10.377$ |
| REPULSIVE | $-14.6$\% | $< 0.0001$*** | $-1.437$ |
| COOPERATIVE | $+83.8$\% | $< 0.0001$*** | $+12.963$ |

**Key finding.** All four policies reach the identical final overload of 4.0 (the theoretical minimum) with zero variance across all 30 replications, every single run, regardless of policy, converges to exactly $O_{\min}$. The pattern is invariant to the access method. Four different interfaces, four different local rules with radically different process signatures, all channel the same mathematical truth with probability 1. This is pattern plurality: the pattern exists independently of the access method, and any reasonable local policy can manifest it. The free lunch is identical regardless of how the system accesses it.

However, the process differs enormously. EXPLORATORY generates 117\% more failed placements than GREEDY ($d = +21.692$), because its wider sampling increases the probability of encountering the frozen hole. REPULSIVE generates 60\% fewer failures ($d = -11.116$) because its crowd-avoidance heuristic naturally steers away from frozen holes. The failure-persistence metric sharpens this story: after rejection, EXPLORATORY retries the same frozen hole 94.0\% of the time and COOPERATIVE 99.7\% of the time, whereas REPULSIVE falls to 46.3\%.

The extraordinarily large effect sizes for failed placements ($d = +21.692$ for EXPLORATORY) deserve comment. In most behavioral experiments, $d > 0.8$ is considered "large." The values here exceed that threshold by an order of magnitude, indicating that the policies produce almost non-overlapping distributions of failed placements. This extreme separation occurs because the failure mechanism is deterministic given the seed: once the initial placement and activation sequence are fixed, the number of times a policy directs a pigeon toward the frozen hole is a stable function of the policy's sampling behavior.

The convergence speed difference between EXPLORATORY (39.8 steps) and the other policies (7.4--8.8 steps) is also notable. EXPLORATORY converges slowly not because it fails to find the optimum, but because its broader sampling means it continues to detect and respond to small load imbalances for longer. Once overload reaches the minimum, EXPLORATORY pigeons still see alternative holes and repeatedly attempt moves that fail at the frozen hole, prolonging the convergence tail. The COOPERATIVE policy is even more revealing: it reaches the optimum quickly, but once it has identified the frozen hole as the locally best-looking low-load option, it nearly always retries it after rejection. This is pattern manifestation without agent-level learning: the pattern provides the optimum for free, but the agents pay wasteful process costs because they have no memory of past failures.

**Classification.** The outcome equivalence across policies constitutes *pattern plurality*: the mathematical truth $O_{\min}$ manifests through four different access methods, confirming that the pattern is invariant to the interface's local policy. The dramatic divergence in failed placements and post-failure persistence reveals that different access methods have different process costs for the same free lunch.


### 4.3 Experiment 3, Noisy Perception: Pattern Fidelity in Discrete Domains

Gaussian noise $\mathcal{N}(0, \sigma^2)$ was added to all perceived hole loads, rounding to non-negative integers. Under the Platonic Space framework, this experiment probes pattern fidelity: how much perceptual degradation the interface tolerates before the pattern fails to manifest.

| Noise $\sigma$ | Final Overload | $\Delta$\% vs $\sigma = 0$ | $p$ | $d$ |
|----------------|---------------|----------------------------|-----|-----|
| 0.0 | 3.0 |, |, |, |
| 0.5 | 3.37 | $+12.2$\% | $0.0011$** | $+0.659$ |
| 1.0 | 3.53 | $+17.8$\% | $< 0.0001$*** | $+1.051$ |
| 2.0 | 3.87 | $+28.9$\% | $< 0.0001$*** | $+1.378$ |
| 5.0 | 4.30 | $+43.3$\% | $< 0.0001$*** | $+1.851$ |

Spearman correlation (noise level vs overload): $\rho = +0.638$, $p < 0.0001$***.

**Key finding.** The discrete pigeonhole interface requires high-fidelity perception to transmit the pattern $O_{\min}$. There is no detectable noise tolerance down to the smallest level we tested: even $\sigma = 0.5$ produces a statistically significant 12.2\% increase in overload ($p = 0.0011$). We cannot rule out a tolerance band below $\sigma = 0.5$; the data show sensitivity already at $\sigma = 0.5$, not the absence of any threshold. Under the Platonic Space framework, this reflects the interface type: a discrete placement system with only 7 holes has no averaging mechanism, even small noise can redirect a pigeon to the wrong hole, and there is no smoothing to recover. We expect continuous interfaces (such as gradient descent on a loss landscape), whose averaging across parameters and batches absorbs small perturbations, to provide a noise buffer that the discrete interface lacks; the same kind of pattern (a mathematical optimum) would then require different fidelity from different interface types. We do not test a continuous interface here, so this contrast is a hypothesis rather than a measured comparison.

One caveat about the noise model. The Gaussian perturbation is rounded and clamped to non-negative integers, so it is not symmetric: for an empty or low-load hole the negative side is clipped while positive deviations survive, biasing perceived load upward exactly where the true load is smallest. Part of the degradation we attribute to noise may therefore come from this clamping rather than from symmetric noise alone. A signed or unclamped noise model would separate the two, and we flag it as a refinement for future runs.

**Delayed gratification under noise.** Unlike every clean experiment, noisy perception produces non-zero delayed gratification. The DG Index is 0 at $\sigma = 0$ but rises to a mean of 0.37 at $\sigma = 0.5$ (11 of 30 runs), 0.42 at $\sigma = 1.0$ (13 of 30), and 0.47 at both $\sigma = 2.0$ (15 of 30) and $\sigma = 5.0$ (16 of 30). In these runs the system passes through a configuration worse than a previously visited one before reaching its final state. This is direct evidence that convergence here is not pure pattern-channeling: the corrupted perception forces the system off the monotone funnel, and reaching $O_{\min}$ requires traversing transiently worse states, the operational signature of delayed gratification.

The effect sizes grow from medium ($d = +0.659$ at $\sigma = 0.5$) to large ($d = +1.851$ at $\sigma = 5.0$), following a concave trajectory: the marginal degradation per unit of noise decreases at higher noise levels. This is consistent with a floor effect: as noise increases, the system's placement decisions approach random assignment, and there is a limit to how bad random placement can be (the expected overload under uniform random assignment is finite and bounded).

The degradation is approximately linear in $\sigma$: an ordinary-least-squares fit of final overload on the five condition means yields $O \approx 3.21 + 0.24\sigma$ ($R^2 \approx 0.90$). Each unit of noise standard deviation adds roughly 0.24 units of overload, about one-quarter of the noise magnitude. The fit is over five points and is descriptive rather than a tested functional form.

**Classification.** The absence of a noise-tolerance threshold reveals a *pattern fidelity constraint* of discrete interfaces: the pigeonhole system has no noise buffer for pattern transmission. The monotonic relationship ($\rho = +0.638$) confirms that fidelity degradation is smooth and predictable. Under the Platonic Space framework, this demonstrates that different interface types (discrete vs continuous) impose categorically different fidelity requirements for channeling the same kind of mathematical pattern.


### 4.4 Experiment 4, View Radius Sweep: Information Geometry of Pattern Access

The view radius $r$ determines how many holes each pigeon can inspect per step. Under the Platonic Space framework, this experiment probes the information geometry of pattern access: how much of the interface must be visible for the pattern to manifest.

| Radius | Final Overload | Convergence Step | $\Delta$\% Conv. vs $r = 1$ | $p$ | $d$ |
|--------|---------------|------------------|-----------------------------|-----|-----|
| 1 | 3.0 | 11.8 |, |, |, |
| 2 | 3.0 | 6.0 | $-49$\% | $0.0093$** | $-0.509$ |
| 3 | 3.0 | 3.9 | $-67$\% | $0.0001$*** | $-0.838$ |
| 5 | 3.0 | 2.3 | $-81$\% | $< 0.0001$*** | $-0.943$ |
| 7 (full) | 3.0 | 2.0 | $-83$\% | $< 0.0001$*** | $-0.965$ |

Spearman correlation (radius vs convergence step): $\rho = -0.494$, $p < 0.0001$*** (computed over pooled per-run points; across the five condition means, which decrease strictly, the rank correlation is $-1$, see Section 3.2).

**Key finding.** The pattern $O_{\min}$ is accessible even with radius $= 1$ (near-blind agents), but convergence speed scales with visibility. All view radii achieve the theoretical minimum overload of 3.0. This is a remarkable free lunch: even agents that see only one hole per step, agents with minimal information about the interface, channel the global mathematical truth $O_{\min} = 3$. The pattern manifests regardless of how much of the interface is visible; only the speed of manifestation varies.

Convergence speed varies by nearly 6$\times$: full visibility ($r = 7$) converges in 2.0 steps versus 11.8 steps for minimal visibility ($r = 1$). This parallels the "power of two choices" result in load balancing (Azar et al., 1999): even a small increase in information access (from $r = 1$ to $r = 2$) produces a 49\% speedup. The diminishing returns of additional visibility are striking: going from $r = 1$ to $r = 2$ saves 5.8 steps (49\%), while going from $r = 5$ to $r = 7$ saves only 0.3 steps (13\%). The relationship between radius and convergence step follows an approximate power law: $\text{conv} \propto r^{-0.9}$.

That even $r = 1$ (minimal information) reaches full coverage reflects two things: the objective is coverage, which any load-seeking rule pursues by construction, and the random initial placement already starts near the target (expected initial overload about 4.5 against a minimum of 3, Section 3.1). The landscape has no local optima to trap a nearly blind agent, so more visibility buys speed, not reachability. We read this as a low-difficulty coverage task solved quickly, rather than as strong evidence for a non-physical pattern.

**Classification.** Universal convergence to $O_{\min}$ across all radii constitutes a strong *free lunch*: the mathematical pattern manifests even through a near-blind interface. The convergence-speed gradient reveals the *information geometry* of pattern access, more visibility accelerates manifestation but is not required for it. The system never fails to channel the pattern; it only channels it more slowly with less information.


### 4.5 Experiment 5, Chimeric Policies: Lateral Pattern Resonance

Mixed populations of $m = 12$ pigeons and $n = 8$ holes, with each pigeon randomly assigned one of two policies. Under the Platonic Space framework, this experiment tests lateral pattern resonance: whether mixed-policy populations access the same pattern and whether self-organization emerges as an additional free lunch.

| Policy Pair | Final Overload | Aggregation Score | $p$ vs 0.75 |
|-------------|---------------|-------------------|-------------|
| GREEDY + COOPERATIVE | 4.0 | 0.738 | 0.56 (n.s.) |
| GREEDY + EXPLORATORY | 4.0 | 0.738 | 0.54 (n.s.) |
| EXPLORATORY + COOPERATIVE | 4.0 | 0.754 | 0.84 (n.s.) |
| REPULSIVE + COOPERATIVE | 4.0 | 0.796 | 0.10 (n.s.) |

No pairwise overload differences between any pair (all $p = \text{n.s.}$).

**Key finding.** All chimeric combinations reach identical final overload, extending the pattern plurality result from homogeneous to heterogeneous populations: the mathematical truth $O_{\min}$ manifests regardless of whether the interface is uniform or mixed. The pattern is invariant to the composition of access methods.

**No self-organization beyond chance.** The aggregation scores (0.738--0.796) do not, however, indicate self-organization by policy type. The correct chance baseline is not 0.5. In every run, the maximum hole load is exactly 2, so each multiply-occupied hole holds exactly two pigeons; for two pigeons each independently assigned one of two policies with equal probability, the two share a policy half the time, giving an expected same-policy fraction of exactly 0.75, not 0.5. Tested against this correct baseline with a one-sample $t$-test, none of the four pairs differs significantly from 0.75: GREEDY+COOPERATIVE and GREEDY+EXPLORATORY fall slightly below ($p = 0.56$ and $p = 0.54$), EXPLORATORY+COOPERATIVE is indistinguishable ($p = 0.84$), and even the highest score, REPULSIVE+COOPERATIVE at 0.796, is not significant ($p = 0.10$). The apparent "aggregation free lunch" reported against a 0.5 baseline is therefore a baseline artifact: once the correct 0.75 null is used, the observed clustering is exactly what random policy assignment to two-pigeon holes predicts.

The scale of this experiment ($m = 12$, $n = 8$) differs from the others to allow pigeons to share holes. Despite the larger system, the pattern invariance persists: all pairs reach identical overload.

**Classification.** The outcome invariance across chimeric compositions extends the *pattern plurality* result: the mathematical truth $O_{\min}$ manifests through any composition of access methods. There is no additional free lunch of policy-type self-organization: against the correct 0.75 chance baseline, same-policy co-location is not above chance, so this experiment provides no evidence of lateral pattern resonance.


### 4.6 Experiment 6, Recovery After Damage: Bidirectional Pattern-Substrate Interface

A hole is frozen at step 167 and healed at step 333 (out of 500 total steps). Under the Platonic Space framework, this experiment tests the bidirectionality of the pattern-substrate interface: whether the pattern re-manifests after both damage and healing.

| Condition | Final Overload | Failed Placements | Same-Target Retry | Repeat Failure |
|-----------|---------------|-------------------|-------------------|----------------|
| control | 3.0 | 0.0 | 0.000 | 0.000 |
| damage\_only | 3.0 | 49.4 | 0.257 | 0.257 |
| damage\_and\_heal | 3.0 | 24.7 | 0.226 | 0.211 |

All overload comparisons: $p = \text{n.s.}$, $d = 0.0$.

**Key finding.** Final overload is 3.0 in all three conditions, including damage\_only, and this is the opposite of what a genuine capacity loss would produce. Freezing one hole should raise the conditional minimum from $O_{\min} = 3$ (7 holes) to $O_{\min} = 4$ (6 holes), so a fully-placed system would have to settle at overload 4. It settles at 3. The reason is the freeze semantics. Freezing blocks new entries but does not eject the hole's current occupant (Section 3.1: the `placement_attempt` hook rejects incoming moves, it does not remove residents). The freeze fires at step 167, long after convergence at about step 8, when all seven holes are already occupied. Hole 0 therefore keeps its resident, still counts toward coverage $H = 7$, and the overload never leaves 3. There is no reduction from seven usable holes to six at the level of coverage, so there is nothing for the system to recover from. The damage\_and\_heal condition also ends at 3, but since overload never departed 3, this is not evidence of re-optimization.

What the experiment does show is a process-cost difference. Under damage\_only the system logs 49.4 failed placements as pigeons repeatedly target the frozen hole and are rejected; healing the hole at step 333 roughly halves this to 24.7, because the second half of the run no longer rejects attempts on hole 0. Same-target retry stays non-zero under damage (0.257) and after healing (0.226), confirming that pigeons form no durable avoidance memory. The defensible reading is that fault duration governs wasted effort, not that the overload state was damaged and repaired.

**Classification.** The equal endpoints across conditions follow from the freeze semantics, not from bidirectional recovery: because freezing does not eject incumbents, the converged coverage is never lost, so overload has nothing to recover. What the experiment measures is *process cost*, with failed placements scaling with the duration of the fault (49.4 under sustained damage, 24.7 when the hole is healed halfway through). A genuine test of bidirectional recovery would require a freeze semantics that ejects or relocates incumbents so that coverage actually drops and must be rebuilt (Section 5.7). We flag Levin's (2026) two-way-interface claim as the motivating idea here, not as something this experiment establishes.


### 4.7 Experiment 7, Progressive vs Sudden Damage: Memoryless Equals Pattern-Driven

Three holes are frozen either all at step 100 (sudden) or one every 100 steps (gradual: steps 100, 200, 300). The experiment was designed to test whether gradual exposure smooths the cost of disruption and whether the memoryless system shows any stress inoculation.

| Condition | Final Overload | Convergence Step | Failed Placements | Same-Target Retry | Repeat Failure |
|-----------|---------------|------------------|-------------------|-------------------|----------------|
| sudden | 3.0 | 3.9 | 173.5 | 0.249 | 0.744 |
| gradual | 3.0 | 3.9 | 128.9 | 0.253 | 0.639 |

Overload comparison: $p = 1.0$, $d = 0.0$. Convergence comparison: $p = 1.0$, $d = 0.0$.
Failed placements: gradual $-26$\% vs sudden, $p < 0.0001$***, $d = -4.116$. Repeat failure: gradual $-14.1$\% vs sudden, $p < 0.0001$***, $d = -2.153$.

**Key finding.** The overload never responds to the damage, so this experiment cannot speak to stress inoculation in the way we first intended. Convergence occurs at step 3.9, while the first freeze occurs at step 100. By the paper's own convergence definition (the last step at which overload changes), overload reached its final value about 96 steps before any hole was frozen and never changed afterward, in either condition. The reason is again the freeze semantics (Section 3.1 and Experiment 6): by step 4 all seven holes are occupied at $O = 3$, and freezing three of them from step 100 onward blocks new entries but keeps their incumbents, so coverage stays at $H = 7$ and overload stays at 3. Both schedules end at overload 3.0 not because the system re-optimized around the damage but because the damage removed no coverage.

The absence of stress inoculation then follows trivially and is not independent evidence for pattern-channeling. The agents are memoryless, so there is no state in which a prior stressor could be recorded, and inoculation is impossible by construction whatever the substrate. More concretely here, overload never changed in response to the damage at all, so there was no disruption for gradual exposure to soften. Showing that gradual and sudden schedules reach the same overload therefore restates the freeze semantics rather than revealing a property of pattern access. The biological contrast with stress-tolerance effects (Levin, 2022) is a motivation for the experiment, not a finding it supports.

What does differ between the schedules is process cost. Sudden freezing produces 173.5 failed placements against 128.9 for gradual, a 26\% reduction ($d = -4.116$), and repeat failure falls from 0.744 to 0.639 ($d = -2.153$). Same-target retry is essentially unchanged (0.249 vs 0.253, n.s.). Spreading the freezes over 300 steps rather than imposing them at once gives pigeons fewer simultaneous rejections to collide with, which lowers wasted attempts without changing the endpoint. This is a process-cost effect of the perturbation's timing, not learning and not reoptimization.

**Classification.** The equal endpoints are a consequence of the freeze semantics and the timing: overload converges before any damage and is never disturbed by it, because freezing does not eject the incumbents that hold coverage. The absence of stress inoculation is entailed by the memoryless architecture and cannot serve as evidence for pattern-channeling. The one real effect is *process cost*: gradual freezing wastes about a quarter fewer placement attempts than sudden freezing (128.9 vs 173.5). Testing inoculation properly would require both agents with memory and a damage schedule that actually perturbs the overload state (Sections 5.7 and 5.8).


### 4.8 Experiment 8, Misleading Holes: Pattern Corruption

Misleading holes report their load as 0 regardless of true occupancy, actively corrupting the interface between the system and the pattern. Under the Platonic Space framework, this experiment tests pattern corruption: what happens when the interface does not merely degrade (as in frozen holes) but actively inverts the pattern-seeking mechanism.

| Misleading Holes | Final Overload | Occupancy Bias | Overload Bias | Load Gap |
|-----------------|---------------|----------------|---------------|----------|
| 0 | 3.0 | 0.000 | 0.000 | 0.000 |
| 1 | 3.77 | 0.217 | 0.518 | 2.533 |
| 2 | 4.20 | 0.274 | 0.559 | 1.920 |
| 3 | 4.33 | 0.265 | 0.511 | 1.544 |
| 4 | 4.40 | 0.219 | 0.418 | 1.275 |
| 5 | 4.37 | 0.156 | 0.286 | 1.090 |
| 6 | 4.30 | 0.080 | 0.143 | 0.928 |

Spearman correlation (misleading holes vs overload): $\rho = +0.417$, $p < 0.0001$***.

**Key finding.** Misleading holes produce pattern corruption, which is categorically different from pattern unavailability (frozen holes). Frozen holes remove capacity: the pattern-seeking mechanism routes around the absent substrate. Misleading holes invert the pattern-seeking mechanism: the same machinery that efficiently finds $O_{\min}$ now efficiently finds the wrong target. A single misleading hole occupies 14\% of the substrate but captures 36\% of pigeons and 66\% of overload, yielding occupancy bias $= 0.217$ and overload bias $= 0.518$. With two misleading holes, deceptive substrate captures 56\% of pigeons and 84.5\% of overload.

Under the Platonic Space framework, this is a free-lunch reversal: the same load-seeking mechanism that efficiently reaches $O_{\min}$ under honest feedback now efficiently converges toward the corrupted attractor. The system's efficiency becomes a liability when the interface reports false loads. This is the clearest empirical result in the study, and it needs no Platonic reading. It is an ordinary and sharp demonstration that a load-sensitive policy becomes vulnerable when its observations are systematically biased.

As with noisy perception, corruption also recruits delayed gratification. The DG Index is 0 with no misleading holes but rises monotonically with the number of deceptive holes: mean 0.25 at 1 hole (8 of 30 runs), 0.29 at 2 (13 of 30), 0.41 at 3 (16 of 30), 0.48 at 4 (18 of 30), 0.56 at 5 (22 of 30), and 0.55 at 6 (22 of 30). The corrupted interface lures pigeons into deceptive holes, and the system must subsequently climb out of these worse configurations, traversing transiently higher overload, which is exactly the delayed-gratification signature. This, together with Experiment 3, shows that delayed gratification is not absent from the pigeonhole system; it is absent only when perception is faithful and emerges whenever the interface corrupts the signal.

A plateau-and-reversal effect is visible: degradation is steepest for the first 1--2 misleading holes (25.6\% and 40.0\%), peaks at 4 misleading holes (46.7\%), and then decreases slightly at 5--6 misleading holes (45.6\% and 43.3\%). This suggests that once a critical fraction of holes is deceptive, additional deception has diminishing marginal effect and may even slightly reduce overload, likely because when nearly all holes are misleading, the deception becomes uniform and ceases to create differential attraction.

The comparison between Experiments 1 and 8 maps onto the classical distributed systems distinction between crash faults and Byzantine faults (Lamport et al., 1982). A crashed node is simply absent; a Byzantine node sends arbitrary (potentially malicious) messages. Under the Platonic Space framework, crash faults correspond to pattern unavailability (the interface loses capacity but does not mislead), while Byzantine faults correspond to pattern corruption (the interface actively inverts the pattern-seeking mechanism). The result that Byzantine faults are categorically harder to tolerate, both in classical distributed computing and in our experiments, reflects a deep asymmetry: a degraded interface merely reduces the bandwidth for pattern transmission, but a corrupted interface turns the transmission mechanism against itself.

**Classification.** Misleading holes constitute *pattern corruption*: the interface actively misleads, inverting the pattern-seeking mechanism. The system's efficiency at load-seeking becomes a vulnerability under corruption, a *free-lunch reversal*. Stated without the framework, this is the study's strongest result: deceptive low-load feedback captures disproportionate occupancy and overload, a clean failure mode of efficient feedback-following policies.


## 5. Discussion

### 5.1 The Pigeonhole Principle as a Platonic Space Pattern

The pigeonhole principle provides what may be the most direct test of Levin's (2026) Platonic Space framework. The framework claims that physical systems serve as interfaces for non-physical patterns, and that these patterns are causal, they determine the behavior of the physical system. In most applications, the "pattern" is implicit, complex, or debatable: in biology, the morphogenetic target; in transformer training, the loss landscape structure; in sorting, the correct permutation. In each case, one might argue that the pattern is merely an emergent property of the physical dynamics rather than a pre-existing mathematical truth.

The pigeonhole principle eliminates this ambiguity. The pattern is $O_{\min} = m - n$: a theorem that every undergraduate knows, derivable from first principles, invariant across implementations, and causally determinative. Under the Platonic Space framework, this theorem is a pattern in the latent space, a mathematical truth that pre-exists any particular pigeonhole system. The physical system (10 pigeons, 7 holes, local policies) is the interface through which this pattern manifests.

What the experiments establish is narrower than the framework's vocabulary suggests, and worth stating plainly. No agent computes $O_{\min}$, represents the global overload, or communicates with another agent, yet the system reaches complete coverage (overload $O_{\min} = 3$) in six of eight conditions, across four policies, five view radii including near-blind $r = 1$, and homogeneous and heterogeneous populations. This is a real and clean fact about local load-seeking on a funnel-shaped objective. Calling it pattern manifestation adds an interpretation on top of that fact. Every interpretation we know of, mathematical Platonism, structuralism, or ordinary algorithmic dynamics, predicts that a fully-placed allocation obeys $O \geq m - n$; no run here could violate the pigeonhole bound without a coding error. What varies across experiments is whether the local algorithm reaches the bound, and that is explained by the policies and the absence of local optima rather than by positing a separate causal pattern. We keep the Platonic vocabulary as an organizing lens and hold it apart from the empirical claims, which are about coverage, process cost, and the asymmetry between honest and deceptive faults.

### 5.2 What Faultization Reveals

Faultization, systematic perturbation of the interface, reveals four categories of behavior that map directly onto the Platonic Space framework:

**Pattern manifestation.** The system reaches $O_{\min}$ (complete coverage) in Experiments 1 (frozen\_0 through frozen\_3), 2 (all four policies), 4 (all view radii), and 5 (all chimeric pairs). Experiments 6 and 7 also end at $O_{\min}$, but as Sections 4.6 and 4.7 show, the dynamic freeze does not remove coverage, so these demonstrate that the endpoint is undisturbed rather than re-established after genuine loss. Coverage is robust to substrate loss up to 43\%, to policy choice, to information scope, and to population heterogeneity; the dynamic-damage experiments show robustness of the freeze semantics rather than of recovery.

**Pattern fidelity.** Experiment 3 (noisy perception) reveals that the discrete pigeonhole interface requires high-fidelity perception, there is no noise buffer. Experiment 4 (view radius) reveals that the pattern manifests even with minimal information, but convergence speed depends on visibility. Together, these experiments characterize the interface's fidelity requirements: accuracy matters, but completeness does not.

**Pattern corruption.** Experiment 8 (misleading holes) reveals that corruption is categorically different from damage. Frozen holes reduce interface capacity; misleading holes invert the pattern-seeking mechanism. The same machinery that channels $O_{\min}$ now channels the wrong target.

**Free lunch.** In the clean structural experiments the system reaches complete coverage from local computation with no global information. We are careful about the accounting (Sections 3.1 and 5.6): the receipt is coverage, not verified load balance, and the damage-compensation and recovery framings do not survive the freeze-semantics analysis of Experiments 6 and 7. We also record a free lunch we expected but did not find: policy-type self-organization in chimeric populations (Experiment 5) does not exceed the correct 0.75 chance baseline, so mixed-policy clustering is not an additional free lunch.

### 5.3 Free Lunch Quantification

Under the Platonic Space framework, the central question is: what does the system receive without paying for? The following table quantifies the free lunch for each experiment.

| Experiment | What was specified | What was received (free lunch) |
|------------|-------------------|-------------------------------|
| 1: Frozen Robustness | Local greedy policies, damaged substrate | Optimal overload despite 43\% damage |
| 2: Policy Comparison | Four different local rules | Identical global optimum from all four |
| 3: Noisy Perception | Noisy load perception | Near-optimal overload at low noise |
| 4: View Radius | Minimal visibility ($r = 1$) | Global optimum from single-hole observations |
| 5: Chimeric | Mixed-policy populations | Optimal overload from any mix (no clustering beyond chance) |
| 6: Recovery | Local policies, dynamic substrate | No overload loss to recover (freeze keeps incumbents); process cost scales with fault duration |
| 7: Progressive vs Sudden | Memoryless agents, temporal perturbation | Endpoint unchanged (damage removes no coverage); gradual schedule wastes 26\% fewer attempts |
| 8: Misleading | Pattern-seeking local policies | Free lunch reversal: efficient convergence to wrong target |

Experiment 8 is the informative inverse. The same load-seeking efficiency that reaches coverage cheaply under honest feedback (Experiments 1--5) drives the system toward false attractors when feedback is deceptive. When the interface reports false loads, the system's efficiency becomes a liability. This is a failure of the interface, not of the underlying constraint: $O_{\min}$ is unchanged, and the corrupted feedback simply points the policies the wrong way.

### 5.4 The Discrete Interface and Its Fidelity Requirement

The pigeonhole system has no noise buffer: even $\sigma = 0.5$ causes statistically significant degradation (Experiment 3), and overload rises smoothly with noise ($\rho = +0.638$). Under the Platonic Space framework, this reflects the interface type. The pattern (a mathematical optimum) is fixed, but the discrete interface offers no averaging mechanism: a pigeon choosing among 7 holes has no way to smooth a noise-induced redirection, and any misdirected placement produces immediate overload. The interface itself, rather than the pattern, sets the fidelity requirement.

This invites a hypothesis about continuous interfaces. A continuous optimization process such as gradient descent has smoothing mechanisms (averaging across parameters, batched gradients) and a stateful optimizer (momentum) that the memoryless pigeonhole system lacks. We would therefore expect a continuous interface to tolerate more perceptual noise before degrading, to converge only approximately rather than exactly, and to support history-dependent effects such as stress inoculation that a memoryless discrete system cannot. The pigeonhole results are consistent with the discrete half of this contrast: exact convergence (zero variance), no detectable noise tolerance down to $\sigma = 0.5$, and, because the agents are memoryless, no stress inoculation. We do not run a continuous interface in this study, so the continuous half remains a prediction for future work rather than a measured comparison.

This suggests a practical principle for the Platonic Space research program: when probing pattern access, the interface type constrains what perturbations are informative. Noise experiments are most revealing in discrete systems (where there is no buffer), while stress-inoculation experiments are expected to be most revealing in continuous, stateful systems (where history-dependent access is possible). Substrate damage and information restriction are informative across both. A direct test of this principle, running the same perturbation battery against a continuous interface, is the natural next step.

### 5.5 Pattern Corruption: Crash vs Byzantine Faults

The sharp distinction between frozen holes (Experiment 1) and misleading holes (Experiment 8) maps onto a fundamental asymmetry in the Platonic Space framework. Frozen holes correspond to pattern unavailability: the interface loses capacity, and the pattern adapts, $O_{\min}$ increases with the number of frozen holes, and the system channels the new, higher $O_{\min}$. The pattern is still accessible; it is simply a different (less favorable) pattern for the degraded substrate.

Misleading holes correspond to pattern corruption: the interface does not merely lose capacity but actively sends false signals. The system's pattern-seeking mechanism, the same local policies that efficiently channel $O_{\min}$ under honest conditions, is activated toward false attractors. The load of 0 reported by a misleading hole is a corrupted signal from the interface, and the system's efficient response to signals becomes its vulnerability.

Under the Platonic Space framework, this distinction is predicted. Levin (2026) argues that physical systems are interfaces for patterns, and that the interface can degrade in different ways. A degraded interface (crash fault) reduces the bandwidth for pattern transmission but does not corrupt it. A deceptive interface (Byzantine fault) turns the transmission mechanism against itself. The result that Byzantine faults are categorically harder to tolerate is not merely an engineering observation, it reflects a fundamental asymmetry in how interfaces can fail to transmit patterns.

### 5.6 Connection to Levin's Platonic Space

Our results can be read against several claims in Levin's (2026) framework, with the caveats of Section 5.7 in mind:

**"Patterns are causal."** Levin (2026) treats patterns as causal in Pearl's counterfactual sense. We can illustrate the idea but not establish it here. Changing $m$ or $n$ does change the final overload, but $m$ and $n$ are parameters of the physical system, so this is parameter dependence, not an intervention that holds the physical and algorithmic system fixed while varying a separate Platonic entity. The model contains no independent pattern variable to manipulate, so the counterfactual illustrates Levin's claim rather than testing it. Within the model, the policy and the funnel structure of the objective are what determine the outcome.

**"Physical systems are interfaces."** The pigeons and holes constitute an interface through which the pattern $O_{\min}$ manifests. The interface can be degraded (frozen holes), corrupted (misleading holes), or restricted (limited view radius), and the pattern's manifestation changes accordingly. But the pattern itself is invariant, it is the interface that varies.

**"Free lunches."** The system reaches complete coverage from local load-seeking without any agent representing the global objective. We are deliberately careful with "for free" (Section 3.1). $O_{\min}$ is computable in constant time, an optimal assignment in $O(m)$, and the local queries, moves, and rejections are themselves a distributed computation, so the $\sim 10^9$-state exhaustive-search comparison overstates the work avoided. In Levin's philosophical sense the structure of the problem is exploited without being represented; in the technical sense of Wolpert and Macready (1997) there is no free lunch, because the advantage comes entirely from matching the policy to the problem's structure.

**"We need to build interfaces and study what unexpected patterns ingress through them."** Our hook-based faultization architecture is such a methodology. By systematically perturbing the interface, we observe what patterns survive degradation, what fidelity the interface requires, and what happens when the interface corrupts. The pigeonhole system is the simplest interface we can build for a known mathematical pattern, making it the ideal starting point for the research program Levin describes.

### 5.7 Limitations

Several limitations of the current study should be noted.

**Scale.** Our system is small ($m = 10$, $n = 7$). Larger systems might exhibit qualitatively different behaviors, such as phase transitions in convergence or emergent delayed gratification driven by longer coordination chains. In particular, the "funnel-shaped" landscape property (no local optima) might break down at larger scales, where the combinatorial state space grows exponentially and the fraction of optimal states shrinks.

**Policy simplicity.** All four policies are stateless and memoryless. Policies with memory (e.g., reinforcement learning agents, or pigeons that remember which holes rejected them) might exhibit richer adaptation. We note that even with memoryless policies, delayed gratification is not universally absent: it is absent under faithful perception but appears whenever the interface corrupts perception (Experiments 3 and 8), where reaching $O_{\min}$ requires traversing transiently worse states. The clean-condition absence of DG therefore reflects the monotone funnel under faithful perception, not an architectural inability of the system to exhibit DG.

**Spatial structure.** Our system has no spatial layout; any pigeon can attempt any hole (subject to view radius constraints). A 2D spatial version with local connectivity might exhibit richer phenomena, including traveling waves of redistribution, spatial phase separation, and boundary effects at the edges of pigeon territories.

**Potential function specificity.** The results may depend on the particular values of $\alpha = 1.0$, $\beta = 0.5$, $\gamma = 10.0$. We did not sweep these hyperparameters, which could reveal sensitivity boundaries. In particular, the relative weight of the concentration penalty ($\beta$) versus the overload penalty ($\alpha$) likely affects whether the system prefers to distribute excess evenly or consolidate it.

**Fixed $m/n$ ratio.** We tested only $m/n = 10/7 \approx 1.43$. More extreme ratios (higher overload density, e.g., $m/n = 3$) or near-critical ratios ($m = n + 1$, minimal impossibility) might produce qualitatively different behaviors. Near the critical ratio, the system might exhibit fluctuations between feasibility and infeasibility that could enable DG-like transients.

**Sample size.** While $n = 30$ replications provide adequate power for the large effects observed (most effect sizes $|d| > 0.8$), smaller effects (e.g., the Spearman correlation in Experiment 1, $\rho = -0.15$) are at the edge of detectability and should be interpreted cautiously.

**Freeze semantics.** Our dynamic freeze (Experiments 6 and 7) blocks new entries but does not eject a hole's current occupant, whereas the static freeze (Experiment 1) removes capacity at initialization, before any pigeon is placed. The two are therefore not comparable: static freezing genuinely reduces coverage, while dynamic freezing of an already-occupied hole leaves coverage intact. This asymmetry is why Experiments 6 and 7 show no overload response to damage (Sections 4.6 and 4.7). A cleaner design would fix one semantics, for instance ejecting or relocating incumbents on freeze, so that dynamic damage actually perturbs coverage and recovery can be measured.

**The objective measures coverage, not balance.** Our primary metric $O$ measures hole coverage, not load balance (Section 3.1): configurations that differ sharply in concentration can share the same $O$. We report $O$ for continuity with the impossibility-theorem framing, but a study of balancing would report potential regret $\Phi - \Phi^\star$ or whether the system reaches the majorization-optimal load vector, and would add null policies (random relocation, stay-put, anti-greedy, and a centralized optimum) to separate what any ongoing random search achieves from what the load bias adds.

**Platonic Space interpretation.** The Platonic Space framework provides a productive interpretation of our results, but the results do not require this interpretation. The phenomena we observe (complete coverage from local rules) can also be explained by the funnel-shaped structure of the potential landscape without invoking a non-physical pattern space. Under the Platonic Space framework, the funnel shape itself is a pattern that the system channels; under a purely physicalist interpretation, the funnel shape is an emergent property of the dynamics. Our experiments do not distinguish between these interpretations. What the experiments do establish is that the system exhibits behaviors consistent with pattern-channeling, and that the Platonic Space framework provides a productive vocabulary for classifying and predicting those behaviors.

### 5.8 Future Work

Several directions emerge from the Platonic Space interpretation of our results.

**Mapping the pattern space.** Varying $m$, $n$, and the $m/n$ ratio would map how the pattern $O_{\min} = m - n$ scales and whether the free lunch persists at larger scales. At what system size does the funnel-shaped landscape break down? Does the free lunch grow or shrink with scale?

**Varying the constraint type.** The pigeonhole principle is the simplest impossibility constraint ($m > n$). Applying faultization to other impossibility theorems, graph coloring with too few colors, bin packing with too few bins, the party problem (Ramsey theory), would test whether free-lunch pattern access generalizes across different mathematical patterns.

**Adding memory.** Policies with memory would test whether the system transitions from pure pattern-channeling to learning-augmented channeling. If memoryful agents exhibit stress inoculation and delayed gratification, this would confirm that our memoryless results isolate the pattern contribution from the learning contribution.

**Richer corruption models.** Our misleading holes report load as 0 uniformly. More sophisticated corruption models (noisy reporting, strategic deception, time-varying corruption) would map the boundary between pattern fidelity degradation and pattern corruption.

**Cross-interface comparison.** Systematically comparing the pigeonhole system, sorting arrays, and transformer training under identical perturbation types would characterize how different interface types transmit the same kinds of patterns. This comparative approach is central to the research program Levin (2026) describes.


## 6. Conclusion

The pigeonhole principle provides the cleanest test of the Platonic Space framework: the pattern is a known mathematical theorem ($O_{\min} = m - n$), the interface is a distributed multi-agent system of memoryless agents with local policies, and the system channels the theorem without computing it. Faultization reveals what happens when we degrade this interface.

Our eight experiments show that local load-seeking policies reach complete coverage of the usable holes, the minimum overload $O_{\min}$, in six of eight conditions, with no agent computing or representing it. The same endpoint appears across four policies, five visibility levels including near-blind $r = 1$, and homogeneous and heterogeneous populations. We are careful with the free-lunch language: reaching $O_{\min}$ is equivalent to covering every usable hole (Section 3.1), $O_{\min}$ is computable in constant time, and the dynamics are themselves a distributed computation, so what the system demonstrates is efficient exploitation of the problem's structure rather than global optimization at no cost.

The strongest finding is the asymmetry between honest and deceptive faults. Static frozen holes (crash faults) reduce capacity, and the system covers the holes that remain. Misleading holes (Byzantine faults) report false low loads, and the same load-seeking efficiency that reaches coverage cheaply now drives the system toward the false attractors, capturing disproportionate occupancy and overload. Efficiency at following feedback becomes a liability when the feedback lies. This deceptive-feedback result needs no Platonic reading and is the study's most robust contribution.

The delayed-gratification and stress-inoculation results are best read as properties of the global trajectory, not of agent memory. The agents are memoryless, so the absence of stress inoculation (Experiment 7) is entailed by the architecture, and the DG index measures whether the collective passes through transiently worse global states. It is zero in the six clean structural experiments, where convergence is monotone, and becomes non-zero precisely when corrupted perception forces the collective off the monotone funnel: the mean DG Index rises from 0 to between 0.37 and 0.47 under noisy perception (Experiment 3, non-zero in 11 to 16 of 30 runs) and up to 0.56 under misleading holes (Experiment 8, non-zero in 22 of 30 runs). Because there is no agent memory, this is path-dependence of the global state under corruption, not accumulated experience. What the pigeonhole system does show cleanly is that the onset of non-monotone dynamics sits exactly at the point where the interface stops transmitting the signal faithfully.

Three directions for future work emerge naturally. First, scaling to larger systems ($m, n \gg 10$) would test whether the free lunch persists or diminishes at scale. Second, adding memory to the pigeon policies would test whether the system transitions from pure pattern-channeling to learning-augmented channeling, potentially enabling stress inoculation and delayed gratification. Third, applying faultization to other impossibility theorems (graph coloring, bin packing, Ramsey theory) would map whether free-lunch pattern access generalizes across different mathematical patterns in the Platonic Space.

The central message is narrower than the framework's vocabulary. Local load-seeking rules reach complete coverage under moderate faults, deceptive feedback causes disproportionate concentration, and policies with equal endpoints differ greatly in process cost. These results are consistent with a Platonic reading, in which mathematical structure is exploited without being represented, but they do not distinguish it from ordinary distributed computation on a structured state space (Section 5.7). Because the pattern is a known theorem, the pigeonhole system makes that gap unusually explicit: it shows exactly where the empirical results end and the interpretation begins.


## References

Aguilera, M. K., Chen, W., and Toueg, S. (2000). Failure detection and consensus in the crash-recovery model. *Distributed Computing*, 13(2), 99--125.

Azar, Y., Broder, A. Z., Karlin, A. R., and Upfal, E. (1999). Balanced allocations. *SIAM Journal on Computing*, 29(1), 180--200.

Lamport, L., Shostak, R., and Pease, M. (1982). The Byzantine generals problem. *ACM Transactions on Programming Languages and Systems*, 4(3), 382--401.

Levin, M. (2019). The computational boundary of a "self": developmental bioelectricity drives multicellularity and scale-free cognition. *Frontiers in Psychology*, 10, 2688.

Levin, M. (2022). Technological approach to mind everywhere: an experimentally-grounded framework for understanding diverse bodies and minds. *Frontiers in Systems Neuroscience*, 16, 768201.

Levin, M. (2026). A short argument on Platonic Space. Blog post, March 31, 2026.

Rosenthal, R. W. (1973). A class of games possessing pure-strategy Nash equilibria. *International Journal of Game Theory*, 2(1), 65--67.

Roughgarden, T., and Tardos, E. (2002). How bad is selfish routing? *Journal of the ACM*, 49(2), 236--259.

Simon, H. A. (1956). Rational choice and the structure of the environment. *Psychological Review*, 63(2), 129--138.

Wolpert, D. H., and Macready, W. G. (1997). No free lunch theorems for optimization. *IEEE Transactions on Evolutionary Computation*, 1(1), 67--82.

Zhang, T., Goldstein, A., and Levin, M. (2024). Classical sorting algorithms as a model of morphogenesis: self-sorting arrays reveal unexpected competencies in a minimal model of basal intelligence. *arXiv preprint* arXiv:2401.05375.
