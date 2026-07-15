# Sources

## Load-bearing sources

- **Zhang, T., Goldstein, A., & Levin, M. (2024).** "Classical sorting algorithms as a model of morphogenesis," arXiv:2401.05375 (also *Adaptive Behavior*, 2025). The methodological parent: faultization (systematic morphogenetic perturbation), the three-stage protocol, the delayed-gratification index, and chimeras all derive from it. Web-verified; the first author is Taining Zhang (an early draft had "Zhang, A." and "Goldstein, I.", since corrected).
- **Levin, M. (2026).** "A short argument on Platonic Space," blog post, March 31 2026. Supplies the interpretive vocabulary (patterns, interfaces, free lunches, the two-way interface). Honestly labelled as a non-peer-reviewed blog post; used as a lens, not as evidence.

## Distributed-systems and load-balancing sources

- **Rosenthal (1973)** (congestion games) and **Roughgarden & Tardos (2002)** (price of anarchy): frame the system as a congestion game whose social optimum is itself an irreducible-conflict state.
- **Azar, Broder, Karlin & Upfal (1999)** (balanced allocations / power of two choices): the view-radius experiment is a loose analogy, softened in revision (the classical result is one-pass and asymptotic; ours permits relocation and measures coverage).
- **Aguilera, Chen & Toueg (2000)** (crash-recovery failure detection): the frozen-vs-misleading contrast maps onto crash vs Byzantine faults. Year corrected from 2004 to 2000 (both referee passes flagged it).
- **Lamport, Shostak & Pease (1982)** (Byzantine generals): the crash/Byzantine framing of Experiments 1 and 8.

## Citations added or integrated in the 2026-07 revision

- **Wolpert & Macready (1997).** No-Free-Lunch theorems, *IEEE TEC* 1(1). Added to disclaim the informal "free lunch" usage: the paper uses Levin's philosophical sense, not the theorem.
- **Simon (1956).** Satisficing / bounded rationality. Was listed but never cited; now integrated where the GREEDY policy is described (it is a satisficing rule), resolving the orphan entry.
- **Levin (2019, 2022).** Basal cognition. Split into separate in-text citations so both years reconcile.

## Verification notes

An earlier pass removed an unlocatable, load-bearing citation ("Kofman, Bhatt & Levin 2025," whose arXiv locator was a scrubbed placeholder) and the discrete-vs-continuous fidelity comparison that depended on it; that contrast is now stated as a hypothesis, not a measured result. The chimeric-aggregation baseline was corrected from 0.5 to the correct 0.75 (every multiply-occupied hole holds two pigeons), and the resulting null is reported. All in-text citation keys reconcile against the bibliography (`papers refs on-faultization-pigeonhole`: 11 keys, 11 entries, 0 missing, 0 unused).
