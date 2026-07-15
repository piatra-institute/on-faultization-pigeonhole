# /// script
# dependencies = ["numpy"]
# ///
"""
Faultized Pigeonhole — Quick Run Script

Usage:
    uv run --script run.py test           # Quick smoke test
    uv run --script run.py experiment1    # Frozen hole robustness curve
    uv run --script run.py experiment2    # Policy comparison
    uv run --script run.py experiment3    # Noisy perception
    uv run --script run.py experiment4    # View radius sweep
    uv run --script run.py experiment5    # Chimeric policies
    uv run --script run.py experiment6    # Recovery after damage
    uv run --script run.py experiment7    # Progressive damage (stress inoculation)
    uv run --script run.py experiment8    # Misleading holes
    uv run --script run.py all            # Run experiments 1-8
    uv run --script run.py n300           # Run experiments 1-8 with 300 reps
"""

import argparse
import sys
import os
import time

# ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from model import Config, PigeonholeSystem, Hooks, Probe, PolicyType, make_config
from metrics import summarize_run
from experiments import (
    experiment1, experiment2, experiment3, experiment4,
    experiment5, experiment6, experiment7, experiment8,
)


def test():
    """Quick smoke test."""
    print('=== Smoke test ===')
    config = make_config(m=10, n=7, frozen_holes=0, num_steps=100, seed=42)
    probe = Probe()
    sys = PigeonholeSystem(config, probe=probe)
    sys.run()

    n_usable = sys.n_usable_holes()
    summary = summarize_run(probe, config.m, n_usable, hole_statuses=sys.hole_status)
    print(f'  m={config.m}, n={config.n}, frozen=0')
    print(f'  theoretical min overload: {summary.theoretical_min_overload}')
    print(f'  final overload:           {summary.final_overload}')
    print(f'  min overload reached:     {summary.min_overload}')
    print(f'  final max load:           {summary.final_max_load}')
    print(f'  final load std:           {summary.final_load_std:.3f}')
    print(f'  final unplaced:           {summary.final_unplaced}')
    print(f'  delayed gratification:    {summary.delayed_gratification_events} events (idx={summary.dg_index:.3f})')
    print(f'  convergence step:         {summary.convergence_step}')
    print(f'  failed placements:        {summary.total_failed_placements}')
    print(f'  overload trajectory (first 20): {probe.overloads[:20]}')
    print()

    # with frozen holes
    print('=== Smoke test (2 frozen holes) ===')
    config = make_config(m=10, n=7, frozen_holes=2, num_steps=100, seed=42)
    probe = Probe()
    sys = PigeonholeSystem(config, probe=probe)
    sys.run()
    n_usable = sys.n_usable_holes()
    summary = summarize_run(probe, config.m, n_usable, hole_statuses=sys.hole_status)
    print(f'  m={config.m}, n={config.n}, frozen=2, usable={n_usable}')
    print(f'  theoretical min overload: {summary.theoretical_min_overload}')
    print(f'  final overload:           {summary.final_overload}')
    print(f'  failed placements:        {summary.total_failed_placements}')
    print(f'  same-target retry rate:   {summary.post_failure_same_target_rate:.3f}')
    print(f'  repeat-failure rate:      {summary.post_failure_repeat_failure_rate:.3f}')
    print(f'  overload ratio:           {summary.overload_ratio:.3f}')
    print()
    print('OK')


def _run_all(num_reps: int, num_steps: int, result_suffix: str) -> None:
    """Run all 8 experiments sequentially."""
    t0 = time.time()
    experiments = [
        experiment1, experiment2, experiment3, experiment4,
        experiment5, experiment6, experiment7, experiment8,
    ]
    for exp_fn in experiments:
        exp_fn(num_reps, num_steps, result_suffix)
        print()
    print(f'All experiments done in {time.time() - t0:.1f}s')


def main():
    parser = argparse.ArgumentParser(
        description='Faultized Pigeonhole: Probing pattern access under irreducible constraint.'
    )
    sub = parser.add_subparsers(dest='command', help='Command to run')

    # Commands that take experiment arguments
    exp_commands = [
        'experiment1', 'experiment2', 'experiment3', 'experiment4',
        'experiment5', 'experiment6', 'experiment7', 'experiment8',
        'all', 'n300',
    ]
    for cmd in exp_commands:
        p = sub.add_parser(cmd)
        p.add_argument('--num-reps', type=int, default=30)
        p.add_argument('--num-steps', type=int, default=500)
        p.add_argument('--result-suffix', type=str, default='')

    # Commands without experiment arguments
    for cmd in ['test']:
        sub.add_parser(cmd)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return

    if args.command == 'test':
        test()
        return

    num_reps = args.num_reps
    num_steps = args.num_steps
    result_suffix = args.result_suffix

    dispatch = {
        'experiment1': experiment1,
        'experiment2': experiment2,
        'experiment3': experiment3,
        'experiment4': experiment4,
        'experiment5': experiment5,
        'experiment6': experiment6,
        'experiment7': experiment7,
        'experiment8': experiment8,
    }

    if args.command == 'n300':
        _run_all(num_reps=300, num_steps=num_steps, result_suffix=result_suffix or '_n300')
    elif args.command == 'all':
        _run_all(num_reps, num_steps, result_suffix)
    elif args.command in dispatch:
        t0 = time.time()
        dispatch[args.command](num_reps, num_steps, result_suffix)
        print(f'Done in {time.time() - t0:.1f}s')
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
