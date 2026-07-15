# /// script
# dependencies = ["numpy", "scipy"]
# ///
"""
Paired statistical analysis of all pigeonhole faultization experiments (n=30).

Uses paired t-tests (matching seeds across conditions) and independent
t-tests where appropriate. Analyzes pattern manifestation, fidelity, and
corruption under systematic perturbation.

Usage:
    uv run --script analyze_stats.py            # Analyze all experiments
    uv run --script analyze_stats.py exp1       # Analyze experiment 1 only
    uv run --script analyze_stats.py exp5       # Analyze experiment 5 only
    uv run --script analyze_stats.py summary    # Cross-experiment summary table
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy import stats


RESULTS_DIR = Path(__file__).parent / 'results'


# ============================================================================
# Utilities
# ============================================================================

def load_results(name: str) -> dict:
    """Load a result JSON file by experiment name."""
    path = RESULTS_DIR / f'{name}.json'
    with open(path) as f:
        return json.load(f)


def sig_marker(p: float) -> str:
    """Significance marker for p-value."""
    if p < 0.001:
        return '***'
    if p < 0.01:
        return '**'
    if p < 0.05:
        return '*'
    if p < 0.10:
        return '\u2020'
    return 'n.s.'


def cohens_d(a: list[float], b: list[float]) -> float:
    """Cohen's d effect size (pooled standard deviation)."""
    a_arr, b_arr = np.array(a, dtype=float), np.array(b, dtype=float)
    pooled_std = np.sqrt(
        (np.std(a_arr, ddof=1) ** 2 + np.std(b_arr, ddof=1) ** 2) / 2
    )
    if pooled_std < 1e-15:
        return 0.0
    return float((np.mean(a_arr) - np.mean(b_arr)) / pooled_std)


def paired_ttest(
    baseline_vals: list[float],
    condition_vals: list[float],
) -> tuple[float, float, float, float, float]:
    """Paired t-test.

    Returns (t_stat, p_value, mean_diff, se_diff, cohen_d).
    """
    diffs = np.array(condition_vals, dtype=float) - np.array(baseline_vals, dtype=float)
    n = len(diffs)
    mean_diff = float(np.mean(diffs))
    se_diff = float(np.std(diffs, ddof=1) / np.sqrt(n))
    if se_diff < 1e-15:
        return 0.0, 1.0, mean_diff, se_diff, 0.0
    t_stat = mean_diff / se_diff
    p_value = float(stats.t.sf(np.abs(t_stat), df=n - 1) * 2)  # two-tailed
    d = float(mean_diff / np.std(diffs, ddof=1))
    return t_stat, p_value, mean_diff, se_diff, d


def independent_ttest(
    a: list[float],
    b: list[float],
) -> tuple[float, float, float, float]:
    """Welch's independent t-test.

    Returns (t_stat, p_value, mean_diff, cohen_d).
    """
    a_arr, b_arr = np.array(a, dtype=float), np.array(b, dtype=float)
    if np.allclose(a_arr, b_arr) and np.std(a_arr) < 1e-15 and np.std(b_arr) < 1e-15:
        return 0.0, 1.0, 0.0, 0.0
    t_stat, p_value = stats.ttest_ind(a_arr, b_arr, equal_var=False)
    d = cohens_d(a, b)
    return float(t_stat), float(p_value), float(np.mean(a_arr) - np.mean(b_arr)), d


def extract_metric(summaries: list[dict], metric: str) -> list[float]:
    """Extract a metric from a list of RunSummary dicts."""
    return [float(s[metric]) for s in summaries]


def print_comparison(
    label: str,
    baseline_vals: list[float],
    condition_vals: list[float],
    paired: bool = True,
) -> dict:
    """Print a statistical comparison line and return result dict."""
    bl_mean = float(np.mean(baseline_vals))
    cond_mean = float(np.mean(condition_vals))
    pct_change = (cond_mean - bl_mean) / bl_mean * 100 if abs(bl_mean) > 1e-15 else 0.0

    if paired:
        t, p, md, se, d = paired_ttest(baseline_vals, condition_vals)
    else:
        t, p, md, d = independent_ttest(condition_vals, baseline_vals)

    print(f"  {label:30s}: mean={cond_mean:.4f} ({pct_change:+.1f}%) "
          f"t={t:+.3f} p={p:.4f}{sig_marker(p):>4s} d={d:+.3f}")
    return {'label': label, 'mean': cond_mean, 'bl_mean': bl_mean,
            'pct_change': pct_change, 't': t, 'p': p, 'd': d}


# ============================================================================
# Experiment 1: Frozen Hole Robustness Curve
# ============================================================================

def analyze_exp1() -> None:
    """Analyze how frozen holes affect overload and failure persistence."""
    print("=" * 70)
    print("EXPERIMENT 1: Frozen Hole Robustness Curve -- Paired t-tests (n=30)")
    print("=" * 70)

    data = load_results('experiment1_frozen_robustness')
    # keys: frozen_0, frozen_1, ..., frozen_6

    baseline_key = 'frozen_0'
    bl = data[baseline_key]
    bl_overload = extract_metric(bl, 'final_overload')
    bl_ratio = extract_metric(bl, 'overload_ratio')

    print(f"\nBaseline (frozen_0): overload={np.mean(bl_overload):.4f}+/-{np.std(bl_overload, ddof=1):.4f}, "
          f"ratio={np.mean(bl_ratio):.4f}, n={len(bl)}")

    condition_keys = sorted(
        [k for k in data if k != baseline_key],
        key=lambda x: int(x.split('_')[-1]),
    )

    print("\n--- Overload Ratio vs Baseline (paired) ---")
    for key in condition_keys:
        cond_ratio = extract_metric(data[key], 'overload_ratio')
        print_comparison(key, bl_ratio, cond_ratio)

    print("\n--- Final Overload vs Baseline (paired) ---")
    for key in condition_keys:
        cond_overload = extract_metric(data[key], 'final_overload')
        print_comparison(key, bl_overload, cond_overload)

    print("\n--- Failure Persistence By Damage Level ---")
    for key in condition_keys:
        retry = extract_metric(data[key], 'post_failure_same_target_rate')
        repeat_fail = extract_metric(data[key], 'post_failure_repeat_failure_rate')
        print(f"  {key:20s}: same_target={np.mean(retry):.4f} "
              f"repeat_fail={np.mean(repeat_fail):.4f}")

    # Monotonicity: Spearman correlation of frozen level vs overload
    print("\n--- Monotonicity (Spearman rank correlation) ---")
    levels: list[int] = []
    overloads: list[float] = []
    for key in sorted(data.keys(), key=lambda x: int(x.split('_')[-1])):
        nf = int(key.split('_')[-1])
        for s in data[key]:
            levels.append(nf)
            overloads.append(s['final_overload'])
    rho, p = stats.spearmanr(levels, overloads)
    print(f"  Spearman rho={rho:.4f}, p={p:.4f} {sig_marker(p)}")


# ============================================================================
# Experiment 2: Policy Comparison
# ============================================================================

def analyze_exp2() -> None:
    """Compare policies under identical conditions."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: Policy Comparison -- Paired t-tests (n=30)")
    print("=" * 70)

    data = load_results('experiment2_policy_comparison')
    # keys: GREEDY, EXPLORATORY, REPULSIVE, COOPERATIVE

    baseline_name = 'GREEDY'
    bl = data[baseline_name]
    bl_overload = extract_metric(bl, 'final_overload')
    bl_failed = extract_metric(bl, 'total_failed_placements')
    bl_retry = extract_metric(bl, 'post_failure_same_target_rate')
    bl_repeat_fail = extract_metric(bl, 'post_failure_repeat_failure_rate')

    print(f"\nBaseline ({baseline_name}): overload={np.mean(bl_overload):.4f}+/-{np.std(bl_overload, ddof=1):.4f}, "
          f"same_target_retry={np.mean(bl_retry):.4f}, n={len(bl)}")

    condition_names = [k for k in data if k != baseline_name]

    print("\n--- Final Overload vs GREEDY (paired) ---")
    for name in condition_names:
        cond = extract_metric(data[name], 'final_overload')
        print_comparison(name, bl_overload, cond)

    print("\n--- Same-Target Retry vs GREEDY (paired) ---")
    for name in condition_names:
        cond = extract_metric(data[name], 'post_failure_same_target_rate')
        print_comparison(name, bl_retry, cond)

    print("\n--- Repeat Failure vs GREEDY (paired) ---")
    for name in condition_names:
        cond = extract_metric(data[name], 'post_failure_repeat_failure_rate')
        print_comparison(name, bl_repeat_fail, cond)

    print("\n--- Failed Placements vs GREEDY (paired) ---")
    for name in condition_names:
        cond = extract_metric(data[name], 'total_failed_placements')
        print_comparison(name, bl_failed, cond)

    # Convergence speed comparison
    print("\n--- Convergence Step (all policies) ---")
    for name in data:
        conv = extract_metric(data[name], 'convergence_step')
        print(f"  {name:20s}: convergence={np.mean(conv):.1f}+/-{np.std(conv, ddof=1):.1f}")


# ============================================================================
# Experiment 3: Noisy Perception
# ============================================================================

def analyze_exp3() -> None:
    """Analyze effect of perceptual noise."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: Noisy Perception -- Paired t-tests (n=30)")
    print("=" * 70)

    data = load_results('experiment3_noisy_perception')
    # keys: noise_0.0, noise_0.5, noise_1.0, noise_2.0, noise_5.0

    baseline_key = 'noise_0.0'
    bl = data[baseline_key]
    bl_overload = extract_metric(bl, 'final_overload')
    bl_ratio = extract_metric(bl, 'overload_ratio')

    print(f"\nBaseline (noise_0.0): overload={np.mean(bl_overload):.4f}+/-{np.std(bl_overload, ddof=1):.4f}, "
          f"n={len(bl)}")

    condition_keys = sorted(
        [k for k in data if k != baseline_key],
        key=lambda x: float(x.split('_')[-1]),
    )

    print("\n--- Final Overload vs Baseline (paired) ---")
    for key in condition_keys:
        cond = extract_metric(data[key], 'final_overload')
        print_comparison(key, bl_overload, cond)

    print("\n--- Overload Ratio vs Baseline (paired) ---")
    for key in condition_keys:
        cond = extract_metric(data[key], 'overload_ratio')
        print_comparison(key, bl_ratio, cond)

    # Monotonicity
    print("\n--- Monotonicity (Spearman: noise vs overload) ---")
    noise_levels: list[float] = []
    overloads: list[float] = []
    for key in sorted(data.keys(), key=lambda x: float(x.split('_')[-1])):
        sigma = float(key.split('_')[-1])
        for s in data[key]:
            noise_levels.append(sigma)
            overloads.append(s['final_overload'])
    rho, p = stats.spearmanr(noise_levels, overloads)
    print(f"  Spearman rho={rho:.4f}, p={p:.4f} {sig_marker(p)}")


# ============================================================================
# Experiment 4: View Radius Sweep
# ============================================================================

def analyze_exp4() -> None:
    """Analyze view radius effects on convergence and quality."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 4: View Radius Sweep -- Paired t-tests (n=30)")
    print("=" * 70)

    data = load_results('experiment4_view_radius')
    # keys: radius_1, radius_2, radius_3, radius_5, radius_7

    # Use smallest radius as baseline
    baseline_key = 'radius_1'
    bl = data[baseline_key]
    bl_overload = extract_metric(bl, 'final_overload')
    bl_conv = extract_metric(bl, 'convergence_step')

    print(f"\nBaseline ({baseline_key}): overload={np.mean(bl_overload):.4f}, "
          f"convergence={np.mean(bl_conv):.1f}+/-{np.std(bl_conv, ddof=1):.1f}, n={len(bl)}")

    condition_keys = sorted(
        [k for k in data if k != baseline_key],
        key=lambda x: int(x.split('_')[-1]),
    )

    print("\n--- Final Overload vs radius_1 (paired) ---")
    for key in condition_keys:
        cond = extract_metric(data[key], 'final_overload')
        print_comparison(key, bl_overload, cond)

    print("\n--- Convergence Step vs radius_1 (paired) ---")
    for key in condition_keys:
        cond = extract_metric(data[key], 'convergence_step')
        print_comparison(key, bl_conv, cond)

    # Spearman: radius vs convergence speed
    print("\n--- Monotonicity (Spearman: radius vs convergence step) ---")
    radii: list[int] = []
    convs: list[float] = []
    for key in sorted(data.keys(), key=lambda x: int(x.split('_')[-1])):
        r = int(key.split('_')[-1])
        for s in data[key]:
            radii.append(r)
            convs.append(s['convergence_step'])
    rho, p = stats.spearmanr(radii, convs)
    print(f"  Spearman rho={rho:.4f}, p={p:.4f} {sig_marker(p)}")


# ============================================================================
# Experiment 5: Chimeric Policies
# ============================================================================

def analyze_exp5() -> None:
    """Analyze mixed-policy populations."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 5: Chimeric Policies (n=30)")
    print("=" * 70)

    data = load_results('experiment5_chimeric')
    # keys: GREEDY+COOPERATIVE, etc.
    # each value: {summaries: [...], mean_aggregation: float, aggregations: [...]}

    pairs = list(data.keys())

    print(f"\n  {'Pair':30s} {'Overload':>10s} {'Ovl Std':>8s} "
          f"{'Aggreg':>8s} {'Agg Std':>8s}")
    print("  " + "-" * 66)

    for pair in pairs:
        entry = data[pair]
        summaries = entry['summaries']
        aggregations = entry['aggregations']

        ovl = extract_metric(summaries, 'final_overload')
        print(f"  {pair:30s} {np.mean(ovl):10.4f} {np.std(ovl, ddof=1):8.4f} "
              f"{np.mean(aggregations):8.4f} {np.std(aggregations, ddof=1):8.4f}")

    # Compare all pairs pairwise on overload
    print("\n--- Pairwise overload comparisons (independent t-test) ---")
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            ovl_i = extract_metric(data[pairs[i]]['summaries'], 'final_overload')
            ovl_j = extract_metric(data[pairs[j]]['summaries'], 'final_overload')
            t, p, md, d = independent_ttest(ovl_i, ovl_j)
            print(f"  {pairs[i]:25s} vs {pairs[j]:25s}: "
                  f"diff={md:+.4f} t={t:+.3f} p={p:.4f}{sig_marker(p):>4s}")


# ============================================================================
# Experiment 6: Recovery After Damage
# ============================================================================

def analyze_exp6() -> None:
    """Analyze recovery dynamics: control vs damage vs damage+heal."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 6: Recovery After Damage -- Paired t-tests (n=30)")
    print("=" * 70)

    data = load_results('experiment6_recovery')
    # keys: control, damage_only, damage_and_heal

    ctrl = data['control']
    damage = data['damage_only']
    healed = data['damage_and_heal']

    ctrl_overload = extract_metric(ctrl, 'final_overload')

    print(f"\nn={len(ctrl)}")
    print(f"  Control:        overload={np.mean(ctrl_overload):.4f}+/-{np.std(ctrl_overload, ddof=1):.4f}")

    print("\n--- Final Overload vs Control (paired) ---")
    print_comparison('damage_only', ctrl_overload,
                     extract_metric(damage, 'final_overload'))
    print_comparison('damage_and_heal', ctrl_overload,
                     extract_metric(healed, 'final_overload'))

    print("\n--- Failure Persistence ---")
    for cond_name in ['damage_only', 'damage_and_heal']:
        retry = extract_metric(data[cond_name], 'post_failure_same_target_rate')
        repeat_fail = extract_metric(data[cond_name], 'post_failure_repeat_failure_rate')
        print(f"  {cond_name:20s}: same_target={np.mean(retry):.4f} "
              f"repeat_fail={np.mean(repeat_fail):.4f}")

    # Does healing recover to control levels?
    print("\n--- Healing vs Damage Only (paired) ---")
    print_comparison('heal vs damage',
                     extract_metric(damage, 'final_overload'),
                     extract_metric(healed, 'final_overload'))

    # Failed placements comparison
    print("\n--- Failed Placements ---")
    for cond_name in ['control', 'damage_only', 'damage_and_heal']:
        failed = extract_metric(data[cond_name], 'total_failed_placements')
        print(f"  {cond_name:20s}: {np.mean(failed):.1f}+/-{np.std(failed, ddof=1):.1f}")


# ============================================================================
# Experiment 7: Progressive Damage (Stress Inoculation)
# ============================================================================

def analyze_exp7() -> None:
    """Analyze gradual vs sudden damage."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 7: Progressive Damage -- Paired t-tests (n=30)")
    print("=" * 70)

    data = load_results('experiment7_progressive_damage')
    # keys: sudden, gradual

    sudden = data['sudden']
    gradual = data['gradual']

    sudden_overload = extract_metric(sudden, 'final_overload')
    gradual_overload = extract_metric(gradual, 'final_overload')

    print(f"\nn={len(sudden)}")
    print(f"  Sudden:  overload={np.mean(sudden_overload):.4f}+/-{np.std(sudden_overload, ddof=1):.4f}")
    print(f"  Gradual: overload={np.mean(gradual_overload):.4f}+/-{np.std(gradual_overload, ddof=1):.4f}")

    print("\n--- Gradual vs Sudden (paired) ---")
    print_comparison('gradual vs sudden (overload)', sudden_overload, gradual_overload)

    # Convergence
    sudden_conv = extract_metric(sudden, 'convergence_step')
    gradual_conv = extract_metric(gradual, 'convergence_step')
    print_comparison('gradual vs sudden (conv)', sudden_conv, gradual_conv)

    # Failed placements
    sudden_fail = extract_metric(sudden, 'total_failed_placements')
    gradual_fail = extract_metric(gradual, 'total_failed_placements')
    print_comparison('gradual vs sudden (failed)', sudden_fail, gradual_fail)

    # Failure persistence
    sudden_retry = extract_metric(sudden, 'post_failure_same_target_rate')
    gradual_retry = extract_metric(gradual, 'post_failure_same_target_rate')
    sudden_repeat = extract_metric(sudden, 'post_failure_repeat_failure_rate')
    gradual_repeat = extract_metric(gradual, 'post_failure_repeat_failure_rate')
    print_comparison('gradual vs sudden (same target)', sudden_retry, gradual_retry)
    print_comparison('gradual vs sudden (repeat fail)', sudden_repeat, gradual_repeat)


# ============================================================================
# Experiment 8: Misleading Holes
# ============================================================================

def analyze_exp8() -> None:
    """Analyze tolerance to deceptive holes."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 8: Misleading Holes -- Paired t-tests (n=30)")
    print("=" * 70)

    data = load_results('experiment8_misleading_holes')
    # keys: misleading_0, misleading_1, ..., misleading_6

    baseline_key = 'misleading_0'
    bl = data[baseline_key]
    bl_overload = extract_metric(bl, 'final_overload')
    bl_ratio = extract_metric(bl, 'overload_ratio')
    bl_max = extract_metric(bl, 'final_max_load')
    bl_occ_bias = extract_metric(bl, 'misleading_occupancy_bias')
    bl_overload_bias = extract_metric(bl, 'misleading_overload_bias')
    bl_load_gap = extract_metric(bl, 'misleading_load_gap')

    print(f"\nBaseline (misleading_0): overload={np.mean(bl_overload):.4f}+/-{np.std(bl_overload, ddof=1):.4f}, "
          f"n={len(bl)}")

    condition_keys = sorted(
        [k for k in data if k != baseline_key],
        key=lambda x: int(x.split('_')[-1]),
    )

    print("\n--- Final Overload vs Baseline (paired) ---")
    for key in condition_keys:
        cond = extract_metric(data[key], 'final_overload')
        print_comparison(key, bl_overload, cond)

    print("\n--- Overload Ratio vs Baseline (paired) ---")
    for key in condition_keys:
        cond = extract_metric(data[key], 'overload_ratio')
        print_comparison(key, bl_ratio, cond)

    print("\n--- Max Load vs Baseline (paired) ---")
    for key in condition_keys:
        cond = extract_metric(data[key], 'final_max_load')
        print_comparison(key, bl_max, cond)

    print("\n--- Occupancy Bias vs Baseline (paired) ---")
    for key in condition_keys:
        cond = extract_metric(data[key], 'misleading_occupancy_bias')
        print_comparison(key, bl_occ_bias, cond)

    print("\n--- Overload Bias vs Baseline (paired) ---")
    for key in condition_keys:
        cond = extract_metric(data[key], 'misleading_overload_bias')
        print_comparison(key, bl_overload_bias, cond)

    print("\n--- Load Gap vs Baseline (paired) ---")
    for key in condition_keys:
        cond = extract_metric(data[key], 'misleading_load_gap')
        print_comparison(key, bl_load_gap, cond)

    # Monotonicity
    print("\n--- Monotonicity (Spearman: n_misleading vs overload) ---")
    levels: list[int] = []
    overloads: list[float] = []
    for key in sorted(data.keys(), key=lambda x: int(x.split('_')[-1])):
        nm = int(key.split('_')[-1])
        for s in data[key]:
            levels.append(nm)
            overloads.append(s['final_overload'])
    rho, p = stats.spearmanr(levels, overloads)
    print(f"  Spearman rho={rho:.4f}, p={p:.4f} {sig_marker(p)}")


# ============================================================================
# Cross-Experiment Summary Table
# ============================================================================

def summary_table() -> None:
    """Print a compact cross-experiment summary table."""
    print("\n" + "=" * 70)
    print("CROSS-EXPERIMENT SUMMARY (n=30, 500 steps, paired t-tests)")
    print("=" * 70)
    print(f"\n{'Experiment':35s} {'Condition':25s} {'Mean':>7s} "
          f"{'D%':>6s} {'p':>8s} {'Sig':>4s}")
    print("-" * 87)

    # Exp 1: Frozen robustness
    try:
        data = load_results('experiment1_frozen_robustness')
        bl = extract_metric(data['frozen_0'], 'overload_ratio')
        for key in sorted([k for k in data if k != 'frozen_0'],
                          key=lambda x: int(x.split('_')[-1])):
            vals = extract_metric(data[key], 'overload_ratio')
            t, p, md, se, d = paired_ttest(bl, vals)
            pct = md / np.mean(bl) * 100 if abs(np.mean(bl)) > 1e-15 else 0.0
            print(f"{'1: Frozen Robustness':35s} {key:25s} "
                  f"{np.mean(vals):7.4f} {pct:+5.1f}% {p:8.4f} {sig_marker(p):>4s}")
    except FileNotFoundError:
        print(f"{'1: Frozen Robustness':35s} -- no results file --")

    # Exp 2: Policy comparison
    try:
        data = load_results('experiment2_policy_comparison')
        bl = extract_metric(data['GREEDY'], 'post_failure_same_target_rate')
        for name in [k for k in data if k != 'GREEDY']:
            vals = extract_metric(data[name], 'post_failure_same_target_rate')
            t, p, md, se, d = paired_ttest(bl, vals)
            pct = md / np.mean(bl) * 100 if abs(np.mean(bl)) > 1e-15 else 0.0
            print(f"{'2: Policy Persistence':35s} {name:25s} "
                  f"{np.mean(vals):7.4f} {pct:+5.1f}% {p:8.4f} {sig_marker(p):>4s}")
    except FileNotFoundError:
        print(f"{'2: Policy Persistence':35s} -- no results file --")

    # Exp 3: Noisy perception
    try:
        data = load_results('experiment3_noisy_perception')
        bl = extract_metric(data['noise_0.0'], 'final_overload')
        for key in sorted([k for k in data if k != 'noise_0.0'],
                          key=lambda x: float(x.split('_')[-1])):
            vals = extract_metric(data[key], 'final_overload')
            t, p, md, se, d = paired_ttest(bl, vals)
            pct = md / np.mean(bl) * 100 if abs(np.mean(bl)) > 1e-15 else 0.0
            print(f"{'3: Noisy Perception':35s} {key:25s} "
                  f"{np.mean(vals):7.4f} {pct:+5.1f}% {p:8.4f} {sig_marker(p):>4s}")
    except FileNotFoundError:
        print(f"{'3: Noisy Perception':35s} -- no results file --")

    # Exp 4: View radius
    try:
        data = load_results('experiment4_view_radius')
        bl = extract_metric(data['radius_1'], 'convergence_step')
        for key in sorted([k for k in data if k != 'radius_1'],
                          key=lambda x: int(x.split('_')[-1])):
            vals = extract_metric(data[key], 'convergence_step')
            t, p, md, se, d = paired_ttest(bl, vals)
            pct = md / np.mean(bl) * 100 if abs(np.mean(bl)) > 1e-15 else 0.0
            print(f"{'4: View Radius':35s} {key + ' (conv)':25s} "
                  f"{np.mean(vals):7.4f} {pct:+5.1f}% {p:8.4f} {sig_marker(p):>4s}")
    except FileNotFoundError:
        print(f"{'4: View Radius':35s} -- no results file --")

    # Exp 5: Chimeric
    try:
        data = load_results('experiment5_chimeric')
        pairs = list(data.keys())
        for pair in pairs:
            entry = data[pair]
            ovl = extract_metric(entry['summaries'], 'final_overload')
            agg = entry['aggregations']
            print(f"{'5: Chimeric':35s} {pair:25s} "
                  f"{np.mean(ovl):7.4f}  agg={np.mean(agg):.3f}")
    except FileNotFoundError:
        print(f"{'5: Chimeric':35s} -- no results file --")

    # Exp 6: Recovery
    try:
        data = load_results('experiment6_recovery')
        bl = extract_metric(data['control'], 'final_overload')
        for cond in ['damage_only', 'damage_and_heal']:
            vals = extract_metric(data[cond], 'final_overload')
            t, p, md, se, d = paired_ttest(bl, vals)
            pct = md / np.mean(bl) * 100 if abs(np.mean(bl)) > 1e-15 else 0.0
            print(f"{'6: Recovery':35s} {cond:25s} "
                  f"{np.mean(vals):7.4f} {pct:+5.1f}% {p:8.4f} {sig_marker(p):>4s}")
    except FileNotFoundError:
        print(f"{'6: Recovery':35s} -- no results file --")

    # Exp 7: Progressive damage
    try:
        data = load_results('experiment7_progressive_damage')
        sudden = extract_metric(data['sudden'], 'final_overload')
        gradual = extract_metric(data['gradual'], 'final_overload')
        t, p, md, se, d = paired_ttest(sudden, gradual)
        pct = md / np.mean(sudden) * 100 if abs(np.mean(sudden)) > 1e-15 else 0.0
        print(f"{'7: Progressive Damage':35s} {'gradual vs sudden':25s} "
              f"{np.mean(gradual):7.4f} {pct:+5.1f}% {p:8.4f} {sig_marker(p):>4s}")
    except FileNotFoundError:
        print(f"{'7: Progressive Damage':35s} -- no results file --")

    # Exp 8: Misleading holes
    try:
        data = load_results('experiment8_misleading_holes')
        bl = extract_metric(data['misleading_0'], 'final_overload')
        for key in sorted([k for k in data if k != 'misleading_0'],
                          key=lambda x: int(x.split('_')[-1])):
            vals = extract_metric(data[key], 'final_overload')
            t, p, md, se, d = paired_ttest(bl, vals)
            pct = md / np.mean(bl) * 100 if abs(np.mean(bl)) > 1e-15 else 0.0
            print(f"{'8: Misleading Holes':35s} {key:25s} "
                  f"{np.mean(vals):7.4f} {pct:+5.1f}% {p:8.4f} {sig_marker(p):>4s}")

        bl_bias = extract_metric(data['misleading_0'], 'misleading_occupancy_bias')
        for key in sorted([k for k in data if k != 'misleading_0'],
                          key=lambda x: int(x.split('_')[-1])):
            vals = extract_metric(data[key], 'misleading_occupancy_bias')
            t, p, md, se, d = paired_ttest(bl_bias, vals)
            pct = md * 100
            print(f"{'8: Occupancy Bias':35s} {key:25s} "
                  f"{np.mean(vals):7.4f} {pct:+5.1f}pp {p:8.4f} {sig_marker(p):>4s}")
    except FileNotFoundError:
        print(f"{'8: Misleading Holes':35s} -- no results file --")

    print(f"\nSignificance: *** p<0.001, ** p<0.01, * p<0.05, "
          f"\u2020 p<0.10, n.s. p>=0.10")
    print(f"All tests: two-tailed paired t-test, seeds matched across conditions")


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'

    dispatch = {
        'exp1': analyze_exp1,
        'exp2': analyze_exp2,
        'exp3': analyze_exp3,
        'exp4': analyze_exp4,
        'exp5': analyze_exp5,
        'exp6': analyze_exp6,
        'exp7': analyze_exp7,
        'exp8': analyze_exp8,
        'summary': summary_table,
    }

    if cmd == 'all':
        analyze_exp1()
        analyze_exp2()
        analyze_exp3()
        analyze_exp4()
        analyze_exp5()
        analyze_exp6()
        analyze_exp7()
        analyze_exp8()
        summary_table()
    elif cmd in dispatch:
        dispatch[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: uv run --script analyze_stats.py [all|exp1|exp2|...|exp8|summary]")


if __name__ == '__main__':
    main()
