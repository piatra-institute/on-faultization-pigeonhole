# On Faultization: Pigeonhole

*Coverage and Failure in a Pigeonhole Model*

Ten items seek places in seven holes. Some destinations reject entry, some
misreport their loads, and some reports contain noise. The September revision
asks what these failures reveal about the allocation rule and its measurement.

Overload equals placed items minus occupied holes. It measures coverage only
when placement is complete, and cannot distinguish balanced from concentrated
loads. The new audit records those outcomes separately. It finds an admission
trap in empty closed holes, representation-dependent tiny-noise effects, and a
substantial difference between blocking new entries and evicting occupants.

## Read and reproduce

The current manuscript is [paper/PAPER.md](paper/PAPER.md). Build its local PDF
with `python3 build.py` from this directory; Pandoc and XeLaTeX are required.
The builder splits the title at its first colon, then prints the institutional
author and date on separate lines. The generated PDF, build log and manifest
remain local and ignored by Git.

The [audit protocol](simulation/AUDIT_PROTOCOL.md) specifies the exploratory
redesign before its new outcomes. From `simulation/`:

```sh
python3 -m unittest test_audit -v
uv run --script audit.py --output output/my-audit
```

The second command uses pinned script dependencies and a fresh output path.
With the recorded dependencies already installed, `python3 audit.py` also works.
Do not rerun against the canonical output directory: the runner refuses an
existing result file. No external data are needed.

## Evidence

The canonical scientific results and figures are in
[simulation/output/september-audit/](simulation/output/september-audit/).
[verification/september-audit.json](verification/september-audit.json) records
execution and hashes. [claims.yaml](claims.yaml) binds selected manuscript
claims to results and sources; [source-checks.md](source-checks.md) records what
was actually checked. Editorial and visual reviews identify the exact artifacts
reviewed. Local verification does not certify deployment or external validity.

The eight old experiment JSON files and original model remain unchanged.
`CLAIM_LEDGER.md`, the old findings/experiment reports and the June referee report
are historical, not verification for this revision. Their claims about
convergence, noise tolerance, equal information access and pattern access should
not be carried forward.
