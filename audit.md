## 2026-09-05 — measurement-led revision and separate audit

The complete original manuscript and core implementation were read before
rewriting. The new title is “On Faultization: Coverage and Failure in a
Pigeonhole Model.” A 198-word abstract and six argument-led sections replace
the repeated Platonic taxonomy. The central distinctions are full placement,
coverage, load balance, admission availability and the cost after arrival.

A separate audit uses 30 paired seed tapes, 32 conditions and 500 activations.
It passed 26 tests and exact mathematical checks; the recorded execution ran
08:21:39–08:22:00 UTC. Twelve specified paired contrasts use one Holm family,
with pointwise intervals. New output does not overwrite the eight historical
result JSON files or change the core model's legacy defaults.

Five closures leave mean U=5.0333 under the original comparison; larger samples
retain the trap, while one-candidate sampling and retry place all items. The
retry's extra admission attempts are counted. Tiny-noise truncation and an
unquantized strict decision boundary each affect Q; arrival-aware comparison
protects the tiny-noise endpoint without guaranteeing no movement. Misleading
reports can preserve coverage while increasing concentration. Entry-only
closure retains occupancy; eviction produces missing work and later replacement.
The revised interpretation does not infer cognition, a necessary detour, acquired
stress tolerance or an independently tested pattern ontology.

Five primary-source entries, 121 selected bound claim records and updated
supporting documentation accompany the manuscript. The original ledger,
experiment/findings reports and June referee report are explicitly historical.
The title uses the requested colon/newline treatment. All nine final pages were
rendered at 110 dpi, individually inspected and reread. A paragraph guard fixes
a floating-figure interruption; references start together on their own page.
Manuscript SHA-256: 49933f4005bbd6065950f0cf75ea0f08087bbd705bf462b550164168da7ce33b.
PDF SHA-256: 3d9828de2baeeabdc21a60e67120b9949091808212b68353641077ca65803c5f.

Only the canonical scientific JSON and two figures are newly Git-eligible;
build logs, manifests, scratch output and the paper's already-ignored PDF stay
local. Local completion is separate from the authorized commit/push step and
from any live-site deployment, which has not been requested.

# Audit

Dated log of editorial passes and verification runs. Newest first.

## 2026-07-15 — critique revision + template migration

Two passes in one: migrated the repo to the canonical paper template, and revised the manuscript to address an external referee report (a more thorough successor to `review-2026-06-18.md`).

**Template migration.** `docs/PAPER.md` -> `paper/PAPER.md` (`paper_dir: paper`); all simulation code, results, scripts, and reference data moved under `simulation/`; `CLAUDE.md` -> `simulation/README.md`; the detailed docs (`FINDINGS.md`, `EXPERIMENTS.md`) moved under `simulation/`; `CLAIM_LEDGER.md` relocated to repo root; added the missing template files `brief.md`, `sources.md`, `research.md`, and a local `chats/chat.md` (chats/ now gitignored). `.gitignore` re-anchored to the new paths (`simulation/results/*`, `paper/PAPER.pdf`, `chats/`).

**Content revision (honesty pass, no new experiments).** Brought every claim down to what the simulation shows, and fixed the concrete errors the referee passes flagged:
- Established the identity `O = m − H` (with all pigeons placed) and re-read "reaching O_min" as complete coverage of the usable holes, not optimal load balancing, throughout the abstract, introduction, methods, results, and conclusion. Added the potential-vs-overload distinction (Φ measures balance, O measures coverage) and the conditional-on-U=0 status of the O_min bound.
- Corrected the optimal-state count to the surjection count `7!{10 brace 7} = 29,635,200` (about 10.5% of the placed states), and deflated the `~10^9`-states free-lunch rhetoric: O_min is O(1) to compute, an optimal assignment O(m), and the random start already sits near the target (expected initial overload about 4.5 against a minimum of 3).
- Rewrote Experiments 6 and 7. The dynamic freeze blocks new entries but does not eject incumbents (verified in `perturbations.py` and `model.py`), so overload never leaves 3.0; Exp 7 converges at step 3.9, before damage at step 100. Retracted the "bidirectional recovery" and "stress inoculation" readings; the real, defensible effect is process cost (failed placements 49.4 vs 24.7 in Exp 6; 173.5 vs 128.9 in Exp 7).
- Reframed the delayed-gratification index as a statistic of the global trajectory, not agent memory, and removed the "accumulated experience is recruited" claim (it contradicts the memoryless agents). Marked the absence of stress inoculation as entailed by the architecture, not as evidence for pattern-channeling.
- Fixed the "physical impossibility" error in Exp 1 (holes have no capacity cap; one hole can hold all ten, O=9; the collapse at 5-6 frozen holes is silent-rejection with U>0, a denominator artifact). Softened the "phase transition" to a finite-horizon-sensitive change.
- Statistics: added the Spearman pseudoreplication caveat (pooled per-run points share seeds; across the five Exp-4 means the rank correlation is -1, not -0.494); flagged the noise-clipping bias; softened "no noise threshold" to "no detectable tolerance down to sigma = 0.5"; standardized on Cohen's d_z and removed the contradictory pooled-SD sentence; corrected the noise regression to O ≈ 3.21 + 0.24σ, R² ≈ 0.90 (was 3.0 + 0.26σ, R² 0.96); softened the power-of-two-choices analogy.
- Free lunch: disclaimed against Wolpert & Macready (1997), distinguishing Levin's philosophical sense from the theorem, and noted the distributed process is itself a computation. Platonic vocabulary marked as an organizing interpretation held apart from the empirical claims (§5.1); the Pearl-causality paragraph recast as illustrating Levin's claim, not establishing it (§5.6). Preserved the already-honest parts: the corrected 0.75 chimeric baseline, the continuous-interface contrast as a hypothesis, and the §5.7 non-distinguishability admission.
- Editorial: Aguilera 2004 -> 2000 (in-text and reference); Zhang reference initials -> Taining Zhang / Adam Goldstein; "first test" and "first morphogenetic perturbation analysis" -> "to our knowledge"; integrated Simon (1956) at the GREEDY policy (satisficing) and split Levin (2019, 2022) so both reconcile; removed the dangling "Table 0" reference; defined faultization against fault injection and mutation testing; removed the "free disaster" coinage; added two Limitations (freeze semantics; coverage-not-balance objective).

References 10 -> 11 (added Wolpert & Macready 1997). Metadata abstract synced. Rewrote the stale `README.md` (wrong sorting-paper attribution, dead `docs/` paths, MorphoGPT-era overclaims) to match the `simulation/` layout and the honest findings, and renamed the front-facing docs from the old codename "Faultized Pigeonhole" to "On Faultization: Pigeonhole Principle" (internal code identifiers keep the old name as historical record).

Not done (recorded in Limitations/Future Work as follow-ups): a load-balance objective (Φ − Φ* or the majorization vector); null policies; hard initial conditions; a scaling sweep in n and m/n; a freeze semantics that ejects incumbents; memory-augmented agents.

Verify: voice 0 errors (advisory contrastive warns, inherent to the corrective framing); refs 11/11, 0 missing/0 unused; claims => claim-ledger present; build fresh (`paper/PAPER.pdf`); check => PASS. PDF synced to web. Left `review-2026-06-18.md` at root; the untracked `critique.md` referee dump is left in place for the author to remove.

## 2026-06-13 — voice reform

Voice-reform pass to remove AI-writing tells, per `tooling/docs/voice.md`. No numbers, equations, table values, or citations changed.

- Reduced voice review-candidates 19 → 6 (0 errors throughout). Thinned the dominant "pattern-channeling, not learning" / "the pattern, not the policy" inline-contrastive tic across the abstract, Results (Exp 1, 6, 7), and Discussion (5.4, 5.6) by rewriting as positive declaratives ("the pattern channels the convergence; agent-level learning does not", "the pattern determines the outcome; the policy merely accesses it", "the interface itself, rather than the pattern, sets the fidelity requirement"). Rewrote "discovered, not created" framing in the introduction with "rather than".
- Density: deleted reflexive "exactly"/"precisely" scope-hedges in the introduction (signature exactly 6 → 3, precisely 3 → 2); left literal/mathematical "exactly one hole" and "exactly $O_{\min}$" uses intact.
- Structure unchanged (6 numbered sections, no structure advisory). Tricolon proxy 58 (advisory; residual is in the cross-experiment summary phrasing).

Verify: `voice` 0 errors; `refs` 0 missing, 9 in-text keys / 11 entries, 2 pre-existing unused (Simon 1956 and one other, not introduced here); `build` clean (0 missing-char); `check` => PASS.

## 2026-05-29 — upgrade pass (Group C): closed the results gap

The paper carried ~30 numeric claims with no committed result artifacts
(`claims_target: none`, empty `results/`). The voice was already clean (no
em-dashes, flat declaratives), so this pass is about reproducibility, not prose.

Changes:
- Regenerated the full result trail (seeded, deterministic): `run.py all` →
  8 `experiment*_*.json`; `analyze_stats.py all` → paired t-tests, Cohen's d,
  Spearman ρ; `visualize.py` → 8 PNGs. Total runtime ~10s.
- Verified every regenerated number against the prose and `FINDINGS.md`: all
  reproduce exactly (e.g. noise +12.2%/p=0.0011 → +43.3%; misleading +25.6% →
  +46.7%; occupancy bias +0.217; ρ=+0.638 and +0.417). No drift — the results
  had simply never been committed.
- Added `docs/CLAIM_LEDGER.md` (10 headline claims → source result file →
  verified value) and set `claims_target: claim-ledger`.
- Citation hygiene: replaced the placeholder `arXiv:2503.XXXXX` on Kofman, Bhatt
  & Levin (2025) with "Preprint." The Levin (2026) entry is honestly labelled
  ("Blog post, March 31, 2026") with a real locator and was left as is.

Verification: voice 0 errors; claims => claim-ledger present, all rows verified;
build clean; check => PASS. Results + figures now committed.
