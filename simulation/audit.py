# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy==2.0.2", "scipy==1.14.1", "matplotlib==3.9.2"]
# ///
"""Separate September audit. See AUDIT_PROTOCOL.md; legacy outputs are untouched."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
import scipy
from scipy import stats

from model import Config, HoleStatus, PigeonholeSystem


@dataclass(frozen=True)
class Condition:
    name: str
    policy: str = "greedy"
    initial: str = "uniform"
    closed: int = 0
    radius: int = 3
    retry: bool = False
    misleading: int = 0
    sigma: float = 0.0
    encoding: str = "truncate"
    event: str = ""


def conditions():
    out = [Condition(f"{initial}/{policy}", policy=policy, initial=initial)
           for initial in ("uniform", "pile") for policy in
           ("stay", "random", "greedy", "arrival")]
    out += [Condition(f"closed/{k}", closed=k) for k in (1, 4, 5, 6)]
    out += [Condition("closed/5/radius1", closed=5, radius=1),
            Condition("closed/5/radius7", closed=5, radius=7),
            Condition("closed/5/retry", closed=5, retry=True)]
    out += [Condition(f"noise/{policy}/{encoding}/{label}", policy=policy,
                      encoding=encoding, sigma=sigma)
            for policy in ("greedy", "arrival")
            for encoding in ("truncate", "round", "float")
            for label, sigma in (("tiny", 1e-6), ("half", 0.5))]
    out += [Condition(f"misleading/{policy}", policy=policy, misleading=1)
            for policy in ("greedy", "arrival")]
    out += [Condition(f"dynamic/{event}", initial="balanced", event=event)
            for event in ("control", "close", "evict")]
    return out


# Zero-noise conditions share the corresponding uniform healthy control.
CONTRASTS = (
    ("uniform/random", "uniform/greedy", "squared_load"),
    ("pile/random", "pile/greedy", "squared_load"),
    ("closed/5/radius7", "closed/5", "unplaced"),
    ("closed/5/retry", "closed/5", "unplaced"),
    ("noise/greedy/truncate/tiny", "uniform/greedy", "squared_load"),
    ("noise/greedy/round/tiny", "uniform/greedy", "squared_load"),
    ("noise/greedy/float/tiny", "uniform/greedy", "squared_load"),
    ("noise/greedy/truncate/half", "noise/greedy/round/half", "squared_load"),
    ("noise/arrival/truncate/tiny", "uniform/arrival", "squared_load"),
    ("misleading/greedy", "uniform/greedy", "overload"),
    ("misleading/arrival", "uniform/arrival", "overload"),
    ("misleading/arrival", "uniform/arrival", "squared_load"),
)


def make_tape(seed, steps, m=10, n=7):
    streams = [np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(4)]
    return {
        "initial": streams[0].integers(0, n, size=(m, 2)),
        "active": streams[1].integers(0, m, size=steps),
        "candidates": np.array([streams[2].permutation(n) for _ in range(steps)]),
        "noise": streams[3].standard_normal((steps, n)),
    }


def tape_hash(tape):
    digest = hashlib.sha256()
    for key in sorted(tape):
        digest.update(key.encode())
        digest.update(tape[key].tobytes())
    return digest.hexdigest()


def encode(value, encoding):
    if encoding == "truncate":
        return max(0, int(value))
    if encoding == "round":
        return max(0, int(np.rint(value)))
    if encoding == "float":
        return float(value)
    raise ValueError("unknown load encoding")


def minimum_squared_load(m, k):
    if m < 0 or k < 1:
        raise ValueError("need nonnegative items and at least one accepting hole")
    q, r = divmod(m, k)
    return (k-r)*q*q + r*(q+1)*(q+1)


def state(system):
    loads = system.loads()
    accepting = np.array([s != HoleStatus.FROZEN for s in system.hole_status])
    occupied = loads > 0
    unplaced = system.unplaced_count()
    k = int(accepting.sum())
    h = int(occupied.sum())
    hc = int((occupied & ~accepting).sum())
    q = int(loads @ loads)
    regret = q - minimum_squared_load(system.m, k) if unplaced == 0 and hc == 0 else None
    misleading = np.array([s == HoleStatus.MISLEADING for s in system.hole_status])
    excess = np.maximum(loads - 1, 0)
    overload = system.overload(loads)
    return {
        "unplaced": unplaced, "placed": system.m-unplaced, "occupied": h,
        "accepting": k, "occupied_accepting": int((occupied & accepting).sum()),
        "occupied_closed": hc, "overload": overload, "squared_load": q,
        "max_load": int(loads.max()), "potential": system.potential(loads),
        "balance_regret": regret,
        "balanced": None if regret is None else int(regret == 0),
        "coverage_complete": int(unplaced == 0 and
                                 int((occupied & accepting).sum()) == min(system.m, k)),
        "misleading_occupancy_share": float(loads[misleading].sum()/system.m),
        "misleading_overload_share": float(excess[misleading].sum()/overload) if overload else 0.0,
    }


def initialize(system, cond, tape):
    system.hole_status[:cond.closed] = HoleStatus.FROZEN
    system.hole_status[cond.closed:cond.closed+cond.misleading] = HoleStatus.MISLEADING
    if cond.initial == "pile":
        system.assignments[:] = 0
    elif cond.initial == "balanced":
        system.assignments[:] = np.arange(system.m) % system.n
    elif cond.initial == "uniform":
        for item, proposals in enumerate(tape["initial"]):
            for target in proposals:
                if system.hole_status[target] != HoleStatus.FROZEN:
                    system.assignments[item] = target
                    break
    else:
        raise ValueError("unknown initialization")
    if cond.initial != "uniform" and (cond.closed or cond.misleading):
        raise ValueError("nonuniform starts here are healthy/event controls")


def activate(system, cond, item, ids, noise):
    """One activation; only the retry control can make multiple admission attempts."""
    old = int(system.assignments[item])
    if cond.policy == "stay":
        return 0, 0, 0, 0
    if cond.policy == "random":
        target = int(ids[0])
        if target == old:
            return 0, 0, 0, 0
        ok = system._try_place(item, target)
        return 0, 1, int(not ok), int(ok)

    loads = system.loads()
    current = int(loads[old]) if old >= 0 else math.inf
    view = []
    for h in ids[:cond.radius]:
        h = int(h)
        load = 0 if system.hole_status[h] == HoleStatus.MISLEADING else int(loads[h])
        reported = encode(load + cond.sigma*noise[h], cond.encoding) if cond.sigma else load
        if h != old:
            view.append((h, reported))
    view.sort(key=lambda pair: pair[1])  # stable ties follow the common permutation
    if cond.policy not in ("greedy", "arrival"):
        raise ValueError("unknown policy")
    offset = 1 if cond.policy == "arrival" else 0
    targets = [h for h, load in view if load + offset < current]
    if not cond.retry:
        targets = targets[:1]
    attempts = failures = changed = 0
    for target in targets:
        attempts += 1
        if system._try_place(item, target):
            changed = 1
            break
        failures += 1
    return min(cond.radius, system.n), attempts, failures, changed


def event(system, kind, step):
    if step not in (100, 300) or kind not in ("close", "evict"):
        return None
    before = state(system)
    if step == 100:
        system.hole_status[0] = HoleStatus.FROZEN
        if kind == "evict":
            system.assignments[system.assignments == 0] = -1
    else:
        system.hole_status[0] = HoleStatus.ACTIVE
    return {"step": step, "before": before, "after": state(system)}


def run_condition(cond, tape, steps):
    system = PigeonholeSystem(Config(num_steps=steps, seed=0))
    initialize(system, cond, tape)
    initial = state(system)
    snapshots = [initial]
    queries = attempts = failures = moves = after_coverage = 0
    first_cover = 0 if initial["coverage_complete"] else None
    first_balance = 0 if initial["balanced"] == 1 else None
    last_overload_change = last_move = 0
    overload_increases = 0
    events = []
    for t in range(1, steps+1):
        system.step_count = t
        counts = activate(system, cond, int(tape["active"][t-1]),
                          tape["candidates"][t-1], tape["noise"][t-1])
        queries += counts[0]
        attempts += counts[1]
        failures += counts[2]
        moves += counts[3]
        if counts[3]:
            last_move = t
            if first_cover is not None:
                after_coverage += 1
        change = event(system, cond.event, t)
        if change:
            events.append(change)
        now = state(system)
        if now["overload"] != snapshots[-1]["overload"]:
            last_overload_change = t
        overload_increases += int(now["overload"] > snapshots[-1]["overload"])
        if first_cover is None and now["coverage_complete"]:
            first_cover = t
        if first_balance is None and now["balanced"] == 1:
            first_balance = t
        snapshots.append(now)
    outcome = {
        "initial": initial, "final": snapshots[-1],
        "assignments": system.assignments.tolist(), "loads": system.loads().tolist(),
        "candidate_queries": queries, "admission_attempts": attempts,
        "failed_attempts": failures, "assignment_changes": moves,
        "moves_after_first_coverage": after_coverage,
        "first_coverage": first_cover, "first_balance": first_balance,
        "coverage_censored": first_cover is None, "balance_censored": first_balance is None,
        "last_overload_change": last_overload_change, "last_assignment_change": last_move,
        "overload_increases": overload_increases,
    }
    if cond.event:
        outcome["events"] = events
        outcome["trajectory"] = {
            key: [s[key] for s in snapshots]
            for key in ("unplaced", "occupied", "overload", "squared_load", "potential")}
        if cond.event in ("close", "evict"):
            replace = next((t for t in range(100, min(300, steps+1))
                            if snapshots[t]["unplaced"] == 0), None)
            recover = next((t for t in range(300, steps+1)
                            if snapshots[t]["unplaced"] == 0 and
                            snapshots[t]["occupied"] == system.n), None)
            outcome["replacement_latency"] = None if replace is None else replace-100
            outcome["reopening_coverage_latency"] = None if recover is None else recover-300
    return outcome


def describe(values):
    a = np.asarray(values, dtype=float)
    if not len(a):
        return {"n": 0, "mean": None, "sd": None, "minimum": None, "maximum": None}
    if not np.isfinite(a).all():
        raise ValueError("nonfinite observation")
    return {"n": len(a), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)) if len(a) > 1 else 0.0,
            "minimum": float(a.min()), "maximum": float(a.max())}


def paired(a, b):
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    if len(d) < 2 or not np.isfinite(d).all():
        raise ValueError("need at least two finite paired observations")
    mean = float(d.mean())
    sd = float(d.std(ddof=1))
    half = float(stats.t.ppf(0.975, len(d)-1)*sd/np.sqrt(len(d)))
    p = float(stats.ttest_1samp(d, 0).pvalue) if sd else float(mean == 0)
    return {"n": len(d), "difference": mean, "ci_low": mean-half,
            "ci_high": mean+half, "p": p, "degenerate": sd == 0}


def holm(values):
    p = np.asarray(values, dtype=float)
    order = np.argsort(p, kind="stable")
    ranked = np.minimum(1.0, np.maximum.accumulate(
        p[order]*(len(p)-np.arange(len(p)))))
    out = np.empty(len(p))
    out[order] = ranked
    return out.tolist()


def summarize(runs):
    out = {"conditions": {}, "contrasts": {}, "primary_contrasts": len(CONTRASTS)}
    for name in runs[0]["conditions"]:
        samples = [r["conditions"][name] for r in runs]
        summary = {"final": {}, "process": {}}
        for key in samples[0]["final"]:
            summary["final"][key] = describe([s["final"][key] for s in samples
                                              if s["final"][key] is not None])
        for key in ("candidate_queries", "admission_attempts", "failed_attempts",
                    "assignment_changes", "moves_after_first_coverage", "first_coverage",
                    "first_balance", "last_overload_change", "last_assignment_change",
                    "overload_increases", "replacement_latency", "reopening_coverage_latency"):
            vals = [s[key] for s in samples if s.get(key) is not None]
            if vals:
                summary["process"][key] = describe(vals)
        summary["coverage_hits"] = sum(s["first_coverage"] is not None for s in samples)
        summary["balance_hits"] = sum(s["first_balance"] is not None for s in samples)
        if "trajectory" in samples[0]:
            summary["mean_trajectory"] = {
                key: np.mean([s["trajectory"][key] for s in samples], axis=0).tolist()
                for key in samples[0]["trajectory"]}
            summary["events"] = {}
            for i, e in enumerate(samples[0]["events"]):
                summary["events"][str(e["step"])] = {
                    side: {key: describe([s["events"][i][side][key] for s in samples
                                          if s["events"][i][side][key] is not None])
                           for key in e[side]}
                    for side in ("before", "after")}
        out["conditions"][name] = summary
    for a, b, key in CONTRASTS:
        out["contrasts"][f"{a} - {b}: {key}"] = paired(
            [r["conditions"][a]["final"][key] for r in runs],
            [r["conditions"][b]["final"][key] for r in runs])
    for c, p in zip(out["contrasts"].values(), holm([c["p"] for c in out["contrasts"].values()])):
        c["p_holm"] = p
    return out


def compositions(total, parts):
    if parts == 1:
        yield (total,)
    else:
        for first in range(total+1):
            for tail in compositions(total-first, parts-1):
                yield (first,)+tail


def mathematical_checks():
    m, n = 10, 7
    vectors = list(compositions(m, n))
    weighted_coverage = weighted_balanced = 0
    min_o = min_phi = min_q = math.inf
    invariant_checks = 0
    for v in vectors:
        p = sum(v)
        h = sum(x > 0 for x in v)
        excess = [max(0, x-1) for x in v]
        o = sum(excess)
        assert o == p-h
        invariant_checks += 1
        q = sum(x*x for x in v)
        phi = o + 0.5*sum(x*x for x in excess)
        min_o, min_q, min_phi = min(min_o, o), min(min_q, q), min(min_phi, phi)
        count = math.factorial(m) // math.prod(math.factorial(x) for x in v)
        if h == n:
            weighted_coverage += count
        if q == minimum_squared_load(m, n):
            weighted_balanced += count
    inclusion_exclusion = sum((-1)**j*math.comb(n, j)*(n-j)**m for j in range(n+1))
    assert weighted_coverage == inclusion_exclusion
    assert (min_o, min_q, min_phi) == (3, 16, 4.5)
    return {
        "m": m, "n": n, "load_vectors_checked": invariant_checks,
        "minimum_overload": min_o, "minimum_squared_load": min_q,
        "minimum_potential": min_phi, "full_assignment_states": n**m,
        "states_including_unplaced": (n+1)**m,
        "coverage_assignments": weighted_coverage, "balanced_assignments": weighted_balanced,
        "uniform_coverage_probability": weighted_coverage/n**m,
        "uniform_balance_probability": weighted_balanced/n**m,
        "uniform_expected_overload": m-n*(1-((n-1)/n)**m),
        "uniform_expected_squared_load": m+m*(m-1)/n,
        "examples": {
            "balanced": {"loads": [2, 2, 2, 1, 1, 1, 1], "overload": 3,
                         "squared_load": 16, "potential": 4.5},
            "concentrated": {"loads": [4, 1, 1, 1, 1, 1, 1], "overload": 3,
                            "squared_load": 22, "potential": 7.5}},
        "tiny_report_example": {
            "true_load": 2, "epsilon": 1e-6,
            "truncated_negative": encode(2-1e-6, "truncate"),
            "truncated_positive": encode(2+1e-6, "truncate"),
            "rounded_negative": encode(2-1e-6, "round"),
            "rounded_positive": encode(2+1e-6, "round")},
    }


def figures(result, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    result["runtime"]["matplotlib"] = matplotlib.__version__
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    summary = result["summary"]["conditions"]
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.3))
    for ax, metric, ylabel in zip(axes, ("unplaced", "occupied_accepting"),
                                   ("Items left unplaced", "Accepting holes occupied")):
        labels = ("Three candidates", "One candidate", "Seven candidates", "Retry within step")
        keys = ("closed/5", "closed/5/radius1", "closed/5/radius7", "closed/5/retry")
        vals = [summary[k]["final"][metric]["mean"] for k in keys]
        ax.bar(range(4), vals, color=["#415a77", "#899bab", "#62798f", "#998357"])
        ax.set_xticks(range(4), labels, rotation=24, ha="right")
        ax.set_ylabel(ylabel)
        ax.set_ylim(0, 10 if metric == "unplaced" else 2.5)
    fig.suptitle("Five closed holes; two still accept placements", fontsize=11)
    fig.tight_layout()
    fig.savefig(output/"admission.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.3), sharey=True)
    for ax, policy, title in zip(axes, ("greedy", "arrival"),
                                 ("Pre-arrival comparison", "Arrival-aware comparison")):
        for encoding, label, style in (("truncate", "Truncate + clip", "-o"),
                                       ("round", "Round + clip", "--s"),
                                       ("float", "Unquantized", ":^")):
            vals = [summary[f"uniform/{policy}"]["final"]["squared_load"]["mean"]]
            vals += [summary[f"noise/{policy}/{encoding}/{x}"]["final"]["squared_load"]["mean"]
                     for x in ("tiny", "half")]
            ax.plot(range(3), vals, style, label=label, markersize=4)
        ax.axhline(16, color="0.6", linewidth=0.8)
        ax.set_xticks(range(3), ["0", "0.000001", "0.5"])
        ax.set(xlabel="Noise standard deviation (categorical spacing)", title=title)
    axes[0].set_ylabel("Mean sum of squared loads")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.0), fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(output/"noise.png", dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("output/september-audit"))
    parser.add_argument("--reps", type=int, default=30)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--seed-start", type=int, default=6000)
    args = parser.parse_args()
    if args.reps < 2 or args.steps < 301 or args.seed_start < 0:
        parser.error("need at least two runs, 301 steps and nonnegative seeds")
    base = Path(__file__).resolve().parent
    output = args.output.resolve()
    if output == base/"results" or base/"results" in output.parents:
        parser.error("legacy results directory is not an audit destination")
    if (output/"results.json").exists():
        parser.error("results.json exists; choose a fresh output directory")
    subprocess.run([sys.executable, "-m", "unittest", "test_audit", "-v"],
                   cwd=base, check=True)
    declared = conditions()
    result = {
        "schema": "pigeonhole-audit-v1",
        "runtime": {"python": sys.version, "numpy": np.__version__,
                    "scipy": scipy.__version__, "platform": platform.platform()},
        "protocol": {"m": 10, "n": 7, "steps": args.steps,
                     "seeds": list(range(args.seed_start, args.seed_start+args.reps)),
                     "conditions": [asdict(c) for c in declared],
                     "contrasts": [list(c) for c in CONTRASTS],
                     "pairing": "independent precomputed initialization/activation/candidate/noise tapes",
                     "scope": "pointwise seed-tape uncertainty; exploratory toy-model audit"},
        "mathematics": mathematical_checks(), "runs": [],
    }
    start = time.monotonic()
    for seed in result["protocol"]["seeds"]:
        tape = make_tape(seed, args.steps)
        result["runs"].append({"seed": seed, "tape_sha256": tape_hash(tape),
                              "conditions": {c.name: run_condition(c, tape, args.steps)
                                             for c in declared}})
        print(f"Completed seed {seed}: {len(result['runs'])}/{args.reps}", flush=True)
    result["summary"] = summarize(result["runs"])
    result["runtime"]["seconds"] = time.monotonic()-start
    output.mkdir(parents=True, exist_ok=True)
    figures(result, output)
    result["execution"] = {"status": "PASS", "exit_code": 0}
    result["experiments"] = [
        {"id": name, "required": True, "execution": {"status": "PASS", "exit_code": 0}}
        for name in ("regressions", "mathematical_checks", "paired_audit")]
    with (output/"results.json").open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(f"Saved {output/'results.json'}")


if __name__ == "__main__":
    main()
