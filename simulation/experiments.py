"""
Faultized Pigeonhole — Experiments

Faultization experiments probing pattern access under the pigeonhole constraint:

1. Frozen hole robustness — pattern bandwidth
2. Policy comparison — pattern plurality
3. Noisy perception — pattern fidelity (discrete)
4. View radius sweep — information geometry
5. Chimeric policies — lateral pattern resonance
6. Dynamic damage / recovery — bidirectional interface
7. Progressive vs sudden damage — memoryless pattern-driven
8. Misleading holes — pattern corruption
"""
from __future__ import annotations

import json
import os
import random
import time
from dataclasses import asdict
from typing import Any

from model import (
    Config, PigeonholeSystem, Hooks, Probe,
    PolicyType, HoleStatus, make_config,
)
from perturbations import (
    make_noisy_view, make_blind_pigeon, make_stubborn_pigeon,
    make_random_mover, make_hole_breaker, make_hole_healer,
    make_progressive_damage, schedule_acute,
)
from metrics import summarize_run, RunSummary, robustness_curve, policy_aggregation


RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def _save(name: str, data: Any, result_suffix: str = '') -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, f'{name}{result_suffix}.json')
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f'  saved: {path}')


def _run_one(config: Config, hooks: Hooks | None = None) -> tuple[PigeonholeSystem, RunSummary]:
    """Run one experiment, return (system, summary)."""
    probe = Probe()
    sys = PigeonholeSystem(config, hooks=hooks, probe=probe)
    sys.run()
    n_usable = sys.n_usable_holes()
    summary = summarize_run(probe, config.m, n_usable, hole_statuses=sys.hole_status)
    return sys, summary


# ============================================================================
# Experiment 1: Frozen hole robustness curve
# ============================================================================

def experiment1(num_reps: int = 30, num_steps: int = 500, result_suffix: str = '', m: int = 10, n: int = 7) -> dict:
    """How does increasing frozen holes affect overload and failure persistence?"""
    print(f'Experiment 1: Frozen hole robustness curve (m={m}, n={n}, reps={num_reps})')
    all_results = {}

    for nf in range(n):
        label = f'frozen_{nf}'
        summaries = []
        for r in range(num_reps):
            config = make_config(m=m, n=n, frozen_holes=nf,
                                 num_steps=num_steps, seed=r)
            _, summary = _run_one(config)
            summaries.append(asdict(summary))
        all_results[label] = summaries
        avg_o = sum(s['final_overload'] for s in summaries) / num_reps
        avg_retry = sum(s['post_failure_same_target_rate'] for s in summaries) / num_reps
        print(f'  frozen={nf}  avg_overload={avg_o:.2f}  avg_same_retry={avg_retry:.2f}')

    _save('experiment1_frozen_robustness', all_results, result_suffix)
    return all_results


# ============================================================================
# Experiment 2: Policy comparison
# ============================================================================

def experiment2(num_reps: int = 30, num_steps: int = 500, result_suffix: str = '', m: int = 10, n: int = 7, frozen: int = 1) -> dict:
    """Compare all four policies under identical conditions."""
    print(f'Experiment 2: Policy comparison (m={m}, n={n}, frozen={frozen}, reps={num_reps})')
    all_results = {}

    for policy in PolicyType:
        summaries = []
        for r in range(num_reps):
            config = make_config(m=m, n=n, frozen_holes=frozen,
                                 policy=policy, num_steps=num_steps, seed=r)
            _, summary = _run_one(config)
            summaries.append(asdict(summary))
        all_results[policy.name] = summaries
        avg_o = sum(s['final_overload'] for s in summaries) / num_reps
        avg_fail = sum(s['total_failed_placements'] for s in summaries) / num_reps
        avg_retry = sum(s['post_failure_same_target_rate'] for s in summaries) / num_reps
        print(f'  {policy.name:15s}  avg_overload={avg_o:.2f}  avg_failed={avg_fail:.1f}  avg_same_retry={avg_retry:.2f}')

    _save('experiment2_policy_comparison', all_results, result_suffix)
    return all_results


# ============================================================================
# Experiment 3: Noisy perception
# ============================================================================

def experiment3(num_reps: int = 30, num_steps: int = 500, result_suffix: str = '', m: int = 10, n: int = 7) -> dict:
    """Effect of perceptual noise on placement quality."""
    print(f'Experiment 3: Noisy perception (m={m}, n={n}, reps={num_reps})')
    noise_levels = [0.0, 0.5, 1.0, 2.0, 5.0]
    all_results = {}

    for sigma in noise_levels:
        label = f'noise_{sigma}'
        summaries = []
        for r in range(num_reps):
            config = make_config(m=m, n=n, num_steps=num_steps, seed=r)
            hooks = Hooks()
            if sigma > 0:
                name, fn = make_noisy_view(noise_std=sigma, rng=random.Random(r + 1000))
                hooks.register(name, fn)
            _, summary = _run_one(config, hooks=hooks)
            summaries.append(asdict(summary))
        all_results[label] = summaries
        avg_o = sum(s['final_overload'] for s in summaries) / num_reps
        print(f'  sigma={sigma:.1f}  avg_overload={avg_o:.2f}')

    _save('experiment3_noisy_perception', all_results, result_suffix)
    return all_results


# ============================================================================
# Experiment 4: View radius sweep
# ============================================================================

def experiment4(num_reps: int = 30, num_steps: int = 500, result_suffix: str = '', m: int = 10, n: int = 7) -> dict:
    """How does pigeon view radius affect convergence and quality?"""
    print(f'Experiment 4: View radius sweep (m={m}, n={n}, reps={num_reps})')
    radii = [1, 2, 3, 5, n]  # from nearly blind to full visibility
    all_results = {}

    for vr in radii:
        label = f'radius_{vr}'
        summaries = []
        for r in range(num_reps):
            config = make_config(m=m, n=n, view_radius=vr,
                                 num_steps=num_steps, seed=r)
            _, summary = _run_one(config)
            summaries.append(asdict(summary))
        all_results[label] = summaries
        avg_o = sum(s['final_overload'] for s in summaries) / num_reps
        avg_conv = sum(s['convergence_step'] for s in summaries) / num_reps
        print(f'  radius={vr}  avg_overload={avg_o:.2f}  avg_convergence={avg_conv:.0f}')

    _save('experiment4_view_radius', all_results, result_suffix)
    return all_results


# ============================================================================
# Experiment 5: Chimeric policies (mixed populations)
# ============================================================================

def experiment5(num_reps: int = 30, num_steps: int = 500, result_suffix: str = '', m: int = 12, n: int = 8) -> dict:
    """Mixed-policy populations. Do same-policy pigeons cluster?"""
    print(f'Experiment 5: Chimeric policies (m={m}, n={n}, reps={num_reps})')
    pairs = [
        (PolicyType.GREEDY, PolicyType.COOPERATIVE),
        (PolicyType.GREEDY, PolicyType.EXPLORATORY),
        (PolicyType.EXPLORATORY, PolicyType.COOPERATIVE),
        (PolicyType.REPULSIVE, PolicyType.COOPERATIVE),
    ]
    all_results = {}

    for p1, p2 in pairs:
        label = f'{p1.name}+{p2.name}'
        summaries = []
        aggregations = []
        for r in range(num_reps):
            rng = random.Random(r)
            mixed = [rng.choice([p1, p2]) for _ in range(m)]
            config = make_config(m=m, n=n, mixed_policies=mixed,
                                 num_steps=num_steps, seed=r)
            sys, summary = _run_one(config)
            summaries.append(asdict(summary))
            agg = policy_aggregation(sys.probe, sys.policies)
            aggregations.append(agg)

        all_results[label] = {
            'summaries': summaries,
            'mean_aggregation': sum(aggregations) / len(aggregations),
            'aggregations': aggregations,
        }
        avg_o = sum(s['final_overload'] for s in summaries) / num_reps
        avg_agg = sum(aggregations) / num_reps
        print(f'  {label:30s}  avg_overload={avg_o:.2f}  avg_aggregation={avg_agg:.3f}')

    _save('experiment5_chimeric', all_results, result_suffix)
    return all_results


# ============================================================================
# Experiment 6: Recovery after damage
# ============================================================================

def experiment6(num_reps: int = 30, num_steps: int = 500, result_suffix: str = '', m: int = 10, n: int = 7) -> dict:
    """Freeze a hole mid-run, then heal it. Does the system recover?"""
    print(f'Experiment 6: Recovery after damage (m={m}, n={n}, reps={num_reps})')
    all_results = {'control': [], 'damage_only': [], 'damage_and_heal': []}

    break_step = num_steps // 3
    heal_step = 2 * num_steps // 3
    target_hole = 0

    for r in range(num_reps):
        # control: no damage
        config = make_config(m=m, n=n, num_steps=num_steps, seed=r)
        _, summary = _run_one(config)
        all_results['control'].append(asdict(summary))

        # damage only: freeze hole at break_step
        config = make_config(m=m, n=n, num_steps=num_steps, seed=r)
        hooks = Hooks()
        sys_tmp = PigeonholeSystem(config, hooks=hooks, probe=Probe())
        name, fn = make_hole_breaker(sys_tmp, break_step, target_hole)
        hooks.register(name, fn)
        sys_tmp.run()
        n_usable = sys_tmp.n_usable_holes()
        summary = summarize_run(sys_tmp.probe, m, n_usable, hole_statuses=sys_tmp.hole_status)
        all_results['damage_only'].append(asdict(summary))

        # damage + heal
        config = make_config(m=m, n=n, num_steps=num_steps, seed=r)
        hooks = Hooks()
        sys_tmp = PigeonholeSystem(config, hooks=hooks, probe=Probe())
        name1, fn1 = make_hole_breaker(sys_tmp, break_step, target_hole)
        name2, fn2 = make_hole_healer(sys_tmp, heal_step, target_hole)
        hooks.register(name1, fn1)
        hooks.register(name2, fn2)
        sys_tmp.run()
        n_usable = sys_tmp.n_usable_holes()
        summary = summarize_run(sys_tmp.probe, m, n_usable, hole_statuses=sys_tmp.hole_status)
        all_results['damage_and_heal'].append(asdict(summary))

    for cond in all_results:
        runs = all_results[cond]
        avg_o = sum(r['final_overload'] for r in runs) / num_reps
        avg_retry = sum(r['post_failure_same_target_rate'] for r in runs) / num_reps
        print(f'  {cond:20s}  avg_overload={avg_o:.2f}  avg_same_retry={avg_retry:.2f}')

    _save('experiment6_recovery', all_results, result_suffix)
    return all_results


# ============================================================================
# Experiment 7: Progressive damage (stress inoculation)
# ============================================================================

def experiment7(num_reps: int = 30, num_steps: int = 500, result_suffix: str = '', m: int = 10, n: int = 7) -> dict:
    """Gradual vs sudden damage. Does gradual exposure build tolerance?"""
    print(f'Experiment 7: Progressive damage (m={m}, n={n}, reps={num_reps})')
    max_frozen = min(3, n - 1)
    all_results = {'sudden': [], 'gradual': []}

    for r in range(num_reps):
        # sudden: freeze max_frozen holes at step 100
        config = make_config(m=m, n=n, num_steps=num_steps, seed=r)
        hooks = Hooks()
        sys_tmp = PigeonholeSystem(config, hooks=hooks, probe=Probe())
        for i in range(max_frozen):
            name, fn = make_hole_breaker(sys_tmp, 100, i)
            hooks.register(name, fn)
        sys_tmp.run()
        summary = summarize_run(
            sys_tmp.probe,
            m,
            sys_tmp.n_usable_holes(),
            hole_statuses=sys_tmp.hole_status,
        )
        all_results['sudden'].append(asdict(summary))

        # gradual: freeze one hole every 100 steps
        config = make_config(m=m, n=n, num_steps=num_steps, seed=r)
        hooks = Hooks()
        sys_tmp = PigeonholeSystem(config, hooks=hooks, probe=Probe())
        name, fn = make_progressive_damage(sys_tmp, start_step=100,
                                           interval=100, max_frozen=max_frozen)
        hooks.register(name, fn)
        sys_tmp.run()
        summary = summarize_run(
            sys_tmp.probe,
            m,
            sys_tmp.n_usable_holes(),
            hole_statuses=sys_tmp.hole_status,
        )
        all_results['gradual'].append(asdict(summary))

    for cond in all_results:
        runs = all_results[cond]
        avg_o = sum(r['final_overload'] for r in runs) / num_reps
        avg_retry = sum(r['post_failure_same_target_rate'] for r in runs) / num_reps
        print(f'  {cond:10s}  avg_overload={avg_o:.2f}  avg_same_retry={avg_retry:.2f}')

    _save('experiment7_progressive_damage', all_results, result_suffix)
    return all_results


# ============================================================================
# Experiment 8: Misleading holes (deceptive substrate)
# ============================================================================

def experiment8(num_reps: int = 30, num_steps: int = 500, result_suffix: str = '', m: int = 10, n: int = 7) -> dict:
    """Holes that lie about their load. Does the system still converge?"""
    print(f'Experiment 8: Misleading holes (m={m}, n={n}, reps={num_reps})')
    all_results = {}

    for nm in range(n):
        label = f'misleading_{nm}'
        summaries = []
        for r in range(num_reps):
            config = make_config(m=m, n=n, misleading_holes=nm,
                                 num_steps=num_steps, seed=r)
            _, summary = _run_one(config)
            summaries.append(asdict(summary))
        all_results[label] = summaries
        avg_o = sum(s['final_overload'] for s in summaries) / num_reps
        avg_bias = sum(s['misleading_occupancy_bias'] for s in summaries) / num_reps
        print(f'  misleading={nm}  avg_overload={avg_o:.2f}  avg_occ_bias={avg_bias:.2f}')

    _save('experiment8_misleading_holes', all_results, result_suffix)
    return all_results
