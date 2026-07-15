# /// script
# dependencies = ["matplotlib", "numpy"]
# ///
"""Visualization functions for pigeonhole faultization experiments."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


RESULTS_DIR = Path(__file__).parent / 'results'


def plot_robustness_curve(results: dict[str, list[dict]], path: str | Path) -> None:
    """Plot final overload ratio vs. number of frozen holes with error bars.

    Expects keys like 'frozen_0', 'frozen_1', ..., each mapping to a list
    of RunSummary dicts.
    """
    levels: list[int] = []
    means: list[float] = []
    stds: list[float] = []
    for key, summaries in sorted(results.items(), key=lambda x: int(x[0].split('_')[-1])):
        n_frozen = int(key.split('_')[-1])
        ratios = [s['overload_ratio'] for s in summaries]
        levels.append(n_frozen)
        means.append(float(np.mean(ratios)))
        stds.append(float(np.std(ratios)))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(levels, means, yerr=stds, marker='o', capsize=4, linewidth=2)
    ax.set_xlabel('Number of Frozen Holes')
    ax.set_ylabel('Overload Ratio (final / theoretical min)')
    ax.set_title('Pattern Bandwidth: Frozen Hole Robustness')
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Optimal')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_policy_comparison(results: dict[str, list[dict]], path: str | Path) -> None:
    """Bar chart comparing policies on endpoint and fault-persistence metrics.

    Expects keys like 'GREEDY', 'EXPLORATORY', ..., each mapping to a list
    of RunSummary dicts.
    """
    policies = list(results.keys())
    metric_keys = ['final_overload', 'total_failed_placements', 'post_failure_same_target_rate']
    labels = ['Final Overload', 'Failed Placements', 'Same-Target Retry Rate']

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for ax, metric, label in zip(axes, metric_keys, labels):
        pol_means: list[float] = []
        pol_stds: list[float] = []
        for policy in policies:
            vals = [s.get(metric, 0) for s in results[policy]]
            pol_means.append(float(np.mean(vals)))
            pol_stds.append(float(np.std(vals)))
        x = np.arange(len(policies))
        ax.bar(x, pol_means, yerr=pol_stds, capsize=4, alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(policies, rotation=30, ha='right')
        ax.set_ylabel(label)
        ax.set_title(label)
        ax.grid(True, alpha=0.3, axis='y')
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_noise_tolerance(results: dict[str, list[dict]], path: str | Path) -> None:
    """Plot overload ratio vs. noise level.

    Expects keys like 'noise_0.0', 'noise_0.5', ..., each mapping to a list
    of RunSummary dicts.
    """
    levels: list[float] = []
    means: list[float] = []
    stds: list[float] = []
    for key, summaries in sorted(results.items(), key=lambda x: float(x[0].split('_')[-1])):
        noise = float(key.split('_')[-1])
        ratios = [s['overload_ratio'] for s in summaries]
        levels.append(noise)
        means.append(float(np.mean(ratios)))
        stds.append(float(np.std(ratios)))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(levels, means, yerr=stds, marker='s', capsize=4, linewidth=2,
                color='tab:orange')
    ax.set_xlabel('Noise Standard Deviation')
    ax.set_ylabel('Overload Ratio')
    ax.set_title('Pattern Fidelity: Noise Degradation')
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_view_radius_sweep(results: dict[str, list[dict]], path: str | Path) -> None:
    """Plot overload ratio and convergence vs. view radius.

    Expects keys like 'radius_1', 'radius_2', ..., each mapping to a list
    of RunSummary dicts.
    """
    radii: list[int] = []
    overload_means: list[float] = []
    overload_stds: list[float] = []
    conv_means: list[float] = []
    conv_stds: list[float] = []
    for key, summaries in sorted(results.items(), key=lambda x: int(x[0].split('_')[-1])):
        r = int(key.split('_')[-1])
        radii.append(r)
        o = [s['overload_ratio'] for s in summaries]
        c = [s['convergence_step'] for s in summaries]
        overload_means.append(float(np.mean(o)))
        overload_stds.append(float(np.std(o)))
        conv_means.append(float(np.mean(c)))
        conv_stds.append(float(np.std(c)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.errorbar(radii, overload_means, yerr=overload_stds, marker='o',
                 capsize=4, linewidth=2)
    ax1.set_xlabel('View Radius')
    ax1.set_ylabel('Overload Ratio')
    ax1.set_title('Overload vs. View Radius')
    ax1.grid(True, alpha=0.3)

    ax2.errorbar(radii, conv_means, yerr=conv_stds, marker='o', capsize=4,
                 linewidth=2, color='tab:green')
    ax2.set_xlabel('View Radius')
    ax2.set_ylabel('Convergence Step')
    ax2.set_title('Convergence Speed vs. View Radius')
    ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_recovery_dynamics(results: dict[str, list[dict]], path: str | Path) -> None:
    """Plot final overload distributions for control, damaged, and healed.

    Expects keys 'control', 'damage_only', 'damage_and_heal', each mapping
    to a list of RunSummary dicts.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {
        'control': 'tab:blue',
        'damage_only': 'tab:red',
        'damage_and_heal': 'tab:green',
    }
    labels = {
        'control': 'Control',
        'damage_only': 'Damage Only',
        'damage_and_heal': 'Damage + Heal',
    }

    for condition, summaries in results.items():
        if condition in colors:
            overloads = [s['final_overload'] for s in summaries]
            ax.hist(overloads, bins=15, alpha=0.5,
                    label=labels.get(condition, condition),
                    color=colors.get(condition, None))

    ax.set_xlabel('Final Overload')
    ax.set_ylabel('Count')
    ax.set_title('Bidirectional Interface: Recovery Overload Distribution')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_progressive_vs_sudden(results: dict[str, list[dict]], path: str | Path) -> None:
    """Compare gradual vs sudden damage final overload distributions.

    Expects keys 'sudden', 'gradual', each mapping to a list of
    RunSummary dicts.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = {'sudden': 'tab:red', 'gradual': 'tab:blue'}

    for condition, summaries in results.items():
        if condition in colors:
            overloads = [s['final_overload'] for s in summaries]
            ax.hist(overloads, bins=15, alpha=0.5,
                    label=condition.capitalize(), color=colors[condition])

    ax.set_xlabel('Final Overload')
    ax.set_ylabel('Count')
    ax.set_title('Pattern-Driven Dynamics: Progressive vs. Sudden')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_chimeric_aggregation(results: dict[str, dict], path: str | Path) -> None:
    """Bar chart of policy aggregation and overload by chimeric pair.

    Expects keys like 'GREEDY+COOPERATIVE', each mapping to a dict with:
        'summaries': list of RunSummary dicts,
        'mean_aggregation': float,
        'aggregations': list of float.
    """
    pairs = list(results.keys())
    overload_means: list[float] = []
    overload_stds: list[float] = []
    agg_means: list[float] = []
    agg_stds: list[float] = []

    for pair in pairs:
        entry = results[pair]
        summaries = entry['summaries']
        aggregations = entry['aggregations']

        ovl = [s['overload_ratio'] for s in summaries]
        overload_means.append(float(np.mean(ovl)))
        overload_stds.append(float(np.std(ovl)))
        agg_means.append(float(np.mean(aggregations)))
        agg_stds.append(float(np.std(aggregations)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    x = np.arange(len(pairs))

    ax1.bar(x, overload_means, yerr=overload_stds, capsize=4, alpha=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(pairs, rotation=30, ha='right')
    ax1.set_ylabel('Overload Ratio')
    ax1.set_title('Lateral Pattern Resonance: Overload')
    ax1.grid(True, alpha=0.3, axis='y')

    ax2.bar(x, agg_means, yerr=agg_stds, capsize=4, alpha=0.8, color='tab:orange')
    ax2.set_xticks(x)
    ax2.set_xticklabels(pairs, rotation=30, ha='right')
    ax2.set_ylabel('Policy Aggregation Score')
    ax2.set_title('Lateral Pattern Resonance: Aggregation')
    ax2.grid(True, alpha=0.3, axis='y')
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_misleading_tolerance(results: dict[str, list[dict]], path: str | Path) -> None:
    """Plot overload and deceptive-occupancy bias vs misleading-hole count.

    Expects keys like 'misleading_0', 'misleading_1', ..., each mapping
    to a list of RunSummary dicts.
    """
    levels: list[int] = []
    overload_means: list[float] = []
    overload_stds: list[float] = []
    bias_means: list[float] = []
    bias_stds: list[float] = []
    for key, summaries in sorted(results.items(), key=lambda x: int(x[0].split('_')[-1])):
        n = int(key.split('_')[-1])
        overloads = [s['final_overload'] for s in summaries]
        biases = [s['misleading_occupancy_bias'] for s in summaries]
        levels.append(n)
        overload_means.append(float(np.mean(overloads)))
        overload_stds.append(float(np.std(overloads)))
        bias_means.append(float(np.mean(biases)))
        bias_stds.append(float(np.std(biases)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.errorbar(levels, overload_means, yerr=overload_stds, marker='D',
                 capsize=4, linewidth=2, color='tab:purple')
    ax1.set_xlabel('Number of Misleading Holes')
    ax1.set_ylabel('Final Overload')
    ax1.set_title('Pattern Corruption: Overload')
    ax1.grid(True, alpha=0.3)

    ax2.errorbar(levels, bias_means, yerr=bias_stds, marker='o', capsize=4,
                 linewidth=2, color='tab:red')
    ax2.set_xlabel('Number of Misleading Holes')
    ax2.set_ylabel('Occupancy Bias')
    ax2.set_title('Pattern Corruption: Occupancy Bias')
    ax2.axhline(y=0.0, color='gray', linestyle='--', alpha=0.5)
    ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# --- Convenience: generate all plots from result files ---

def generate_all_plots() -> None:
    """Generate all plots from existing result JSON files."""
    plot_map: dict[str, tuple[str, Any]] = {
        'experiment1_frozen_robustness': ('exp1_robustness_curve.png', plot_robustness_curve),
        'experiment2_policy_comparison': ('exp2_policy_comparison.png', plot_policy_comparison),
        'experiment3_noisy_perception': ('exp3_noise_tolerance.png', plot_noise_tolerance),
        'experiment4_view_radius': ('exp4_view_radius.png', plot_view_radius_sweep),
        'experiment5_chimeric': ('exp5_chimeric.png', plot_chimeric_aggregation),
        'experiment6_recovery': ('exp6_recovery.png', plot_recovery_dynamics),
        'experiment7_progressive_damage': ('exp7_progressive_vs_sudden.png', plot_progressive_vs_sudden),
        'experiment8_misleading_holes': ('exp8_misleading.png', plot_misleading_tolerance),
    }

    for result_name, (plot_name, plot_fn) in plot_map.items():
        json_path = RESULTS_DIR / f'{result_name}.json'
        if json_path.exists():
            with open(json_path) as f:
                data = json.load(f)
            plot_path = RESULTS_DIR / plot_name
            try:
                plot_fn(data, plot_path)
                print(f'  {plot_name}')
            except Exception as e:
                print(f'  {plot_name} FAILED: {e}')
        else:
            print(f'  {result_name}.json not found, skipping')


if __name__ == '__main__':
    print('Generating plots...')
    generate_all_plots()
    print('Done.')
