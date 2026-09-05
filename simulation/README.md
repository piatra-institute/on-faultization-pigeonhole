# Pigeonhole simulation

## Current audit

Read [AUDIT_PROTOCOL.md](AUDIT_PROTOCOL.md) before interpreting the September
results. The new `audit.py` reuses the core placement state but runs a separate
paired-input design. It is not an exact replication of the eight old experiments.

From this directory:

```sh
python3 -m unittest test_audit -v
uv run --script audit.py --output output/my-audit
```

Python >=3.12; pinned NumPy 2.0.2, SciPy 1.14.1, Matplotlib 3.9.2. The recorded
run used Python 3.12.4. With these dependencies installed, invoke Python directly.
No dataset download is needed. Matplotlib may need a writable MPLCONFIGDIR.

The audit runs 26 regressions, mathematical checks, then 32 conditions over
30 independent seed tapes and 500 activations. It records U, coverage, squared
load, conditional balance regret, report queries, admission attempts, successful
moves and censored hitting times. Independent streams pair initialization,
activation, candidate ordering and noise across conditions. Execution success
is separate from whether any scientific contrast rejects its null.

Canonical evidence: `output/september-audit/results.json`, `admission.png` and
`noise.png`; receipt: `../verification/september-audit.json`. Only these selected
scientific outputs are Git-eligible. Other output paths, caches, build records
and PDFs remain ignored. The runner refuses an existing results.json and writes
nothing into legacy `results/`.

The main rules use the same reported-load interface. The arrival-aware rule adds
one before comparing with the exact current occupied load. Both exclude the
current hole as a relocation destination. Retry uses the next eligible candidate
within one activation, without persistent memory, and can spend more attempts.
Closed admission preserves incumbents unless an explicit eviction is requested.

## Legacy study

`model.py`, `perturbations.py`, `experiments.py`, `metrics.py`, `run.py`,
`analyze_stats.py` and `visualize.py` retain their original behavior. The eight
JSON files in `results/` are historical evidence for the old draft. The old
FINDINGS, EXPERIMENTS, root CLAIM_LEDGER and referee report are labeled historical.
Do not run `run.py all` merely to reproduce the new manuscript: that command
writes the old result files instead.

Known legacy semantics: overload stabilization is not assignment convergence;
noisy reports truncate rather than round; exploratory extra probes and the
cooperative potential use true information; shared seeds do not ensure shared
random tapes. Those differences motivated the new audit.
