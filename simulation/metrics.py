"""
Faultized Pigeonhole — Metrics

Statistical metrics for analyzing pigeonhole dynamics.
Measures pattern manifestation, fidelity, and corruption under faultization,
extended with probes for failure response and substrate bias.
"""
from __future__ import annotations

from collections import defaultdict
import numpy as np
from dataclasses import dataclass

from typing import Any


@dataclass
class RunSummary:
    """Summary statistics for a single simulation run."""
    # overload
    final_overload: int
    min_overload: int
    theoretical_min_overload: int
    overload_ratio: float          # final / theoretical_min (1.0 = optimal)

    # potential
    final_potential: float
    min_potential: float

    # load balance
    final_max_load: int
    final_load_std: float          # std dev of loads (lower = more balanced)

    # placement
    final_unplaced: int

    # convergence
    steps_to_min_overload: int
    convergence_step: int          # last step where overload changed

    # emergent behaviors
    delayed_gratification_events: int
    dg_index: float                # magnitude-weighted DG score
    total_failed_placements: int   # moves rejected by frozen holes

    # learning-like failure response
    post_failure_same_target_rate: float   # retry the same failed hole next attempt
    post_failure_repeat_failure_rate: float  # next attempt also fails
    post_failure_opportunities: int

    # fault-induced bias
    misleading_occupancy_share: float
    misleading_occupancy_bias: float
    misleading_overload_share: float
    misleading_overload_bias: float
    misleading_load_gap: float


def summarize_run(
    probe: Any,
    m: int,
    n_usable: int,
    hole_statuses: Any | None = None,
) -> RunSummary:
    """Compute summary from a Probe."""
    overloads = probe.overloads
    potentials = probe.potentials

    if not overloads:
        theo = max(0, m - n_usable)
        return RunSummary(
            final_overload=0, min_overload=0,
            theoretical_min_overload=theo, overload_ratio=0.0,
            final_potential=0.0, min_potential=0.0,
            final_max_load=0, final_load_std=0.0,
            final_unplaced=m,
            steps_to_min_overload=0, convergence_step=0,
            delayed_gratification_events=0, dg_index=0.0,
            total_failed_placements=0,
            post_failure_same_target_rate=0.0,
            post_failure_repeat_failure_rate=0.0,
            post_failure_opportunities=0,
            misleading_occupancy_share=0.0,
            misleading_occupancy_bias=0.0,
            misleading_overload_share=0.0,
            misleading_overload_bias=0.0,
            misleading_load_gap=0.0,
        )

    min_overload = min(overloads)
    theo = max(0, m - n_usable)
    ratio = overloads[-1] / theo if theo > 0 else (1.0 if overloads[-1] == 0 else float('inf'))

    # delayed gratification
    dg_events, dg_idx = compute_delayed_gratification(overloads)

    # convergence
    convergence = 0
    for i in range(1, len(overloads)):
        if overloads[i] != overloads[i - 1]:
            convergence = probe.steps[i]

    # failed placements
    failed = sum(1 for _, _, _, _, success in probe.moves if not success)
    same_target_rate, repeat_failure_rate, opportunities = compute_post_failure_persistence(probe.moves)

    # load balance at end
    final_loads = probe.load_snapshots[-1] if probe.load_snapshots else np.zeros(1)
    load_std = float(np.std(final_loads))
    occ_share, occ_bias, overload_share, overload_bias, load_gap = compute_misleading_bias(
        final_loads, hole_statuses
    )

    return RunSummary(
        final_overload=overloads[-1],
        min_overload=min_overload,
        theoretical_min_overload=theo,
        overload_ratio=ratio,
        final_potential=potentials[-1],
        min_potential=min(potentials),
        final_max_load=probe.max_loads[-1] if probe.max_loads else 0,
        final_load_std=load_std,
        final_unplaced=probe.unplaced_counts[-1] if probe.unplaced_counts else m,
        steps_to_min_overload=probe.steps[overloads.index(min_overload)],
        convergence_step=convergence,
        delayed_gratification_events=dg_events,
        dg_index=dg_idx,
        total_failed_placements=failed,
        post_failure_same_target_rate=same_target_rate,
        post_failure_repeat_failure_rate=repeat_failure_rate,
        post_failure_opportunities=opportunities,
        misleading_occupancy_share=occ_share,
        misleading_occupancy_bias=occ_bias,
        misleading_overload_share=overload_share,
        misleading_overload_bias=overload_bias,
        misleading_load_gap=load_gap,
    )


def compute_delayed_gratification(overloads: list[int]) -> tuple[int, float]:
    """
    Delayed gratification: count events where overload increases
    then later drops below the previous local minimum.
    Returns (count, magnitude-weighted index).

    Same concept as the sorting paper's DG metric: the system temporarily
    gets worse in order to later get better.
    """
    if len(overloads) < 3:
        return 0, 0.0

    events = 0
    total_gain = 0.0
    local_min = overloads[0]
    peak_after_min = overloads[0]
    saw_increase = False

    for i in range(1, len(overloads)):
        if overloads[i] > local_min:
            saw_increase = True
            peak_after_min = max(peak_after_min, overloads[i])
        elif overloads[i] < local_min:
            if saw_increase:
                events += 1
                # gain = how much better we got relative to the detour cost
                detour = peak_after_min - local_min
                gain = local_min - overloads[i]
                if detour > 0:
                    total_gain += gain / detour
            local_min = overloads[i]
            peak_after_min = overloads[i]
            saw_increase = False

    dg_index = total_gain / max(events, 1)
    return events, dg_index


def compute_post_failure_persistence(
    moves: list[tuple[int, int, int, int, bool]],
) -> tuple[float, float, int]:
    """Quantify whether pigeons persist on faulty substrate after rejection.

    We look only at pigeons that make another placement attempt after a failure.
    The resulting rates are therefore "next attempted move" rates, not
    next-activation rates.
    """
    by_pigeon: dict[int, list[tuple[int, bool]]] = defaultdict(list)
    for _, pigeon_id, _, target_hole, success in moves:
        by_pigeon[pigeon_id].append((target_hole, success))

    same_target_retries = 0
    repeat_failures = 0
    opportunities = 0

    for history in by_pigeon.values():
        for idx, (target_hole, success) in enumerate(history[:-1]):
            if success:
                continue
            opportunities += 1
            next_target, next_success = history[idx + 1]
            if next_target == target_hole:
                same_target_retries += 1
            if not next_success:
                repeat_failures += 1

    if opportunities == 0:
        return 0.0, 0.0, 0

    return (
        same_target_retries / opportunities,
        repeat_failures / opportunities,
        opportunities,
    )


def compute_misleading_bias(
    loads: np.ndarray,
    hole_statuses: Any | None,
) -> tuple[float, float, float, float, float]:
    """Measure whether misleading holes disproportionately attract load.

    Returns:
        occupancy_share: fraction of pigeons on misleading holes
        occupancy_bias: occupancy_share - fraction_of_misleading_holes
        overload_share: fraction of overload concentrated on misleading holes
        overload_bias: overload_share - fraction_of_misleading_holes
        load_gap: mean misleading-hole load minus mean honest-hole load
    """
    if hole_statuses is None:
        return 0.0, 0.0, 0.0, 0.0, 0.0

    statuses = list(hole_statuses)
    if not statuses:
        return 0.0, 0.0, 0.0, 0.0, 0.0

    def status_name(status: Any) -> str:
        return getattr(status, 'name', str(status))

    misleading_ids = [i for i, status in enumerate(statuses) if status_name(status) == 'MISLEADING']
    if not misleading_ids:
        return 0.0, 0.0, 0.0, 0.0, 0.0

    honest_ids = [i for i, status in enumerate(statuses) if status_name(status) != 'MISLEADING']
    hole_fraction = len(misleading_ids) / len(statuses)

    total_load = float(np.sum(loads))
    occupancy_share = float(np.sum(loads[misleading_ids]) / total_load) if total_load > 0 else 0.0
    occupancy_bias = occupancy_share - hole_fraction

    excess = np.maximum(loads - 1, 0)
    total_excess = float(np.sum(excess))
    overload_share = (
        float(np.sum(excess[misleading_ids]) / total_excess)
        if total_excess > 0 else 0.0
    )
    overload_bias = overload_share - hole_fraction if total_excess > 0 else 0.0

    misleading_mean = float(np.mean(loads[misleading_ids])) if misleading_ids else 0.0
    honest_mean = float(np.mean(loads[honest_ids])) if honest_ids else 0.0
    load_gap = misleading_mean - honest_mean

    return occupancy_share, occupancy_bias, overload_share, overload_bias, load_gap


def robustness_curve(summaries_by_damage: dict[int, list[RunSummary]]) -> dict[int, dict]:
    """
    Given {n_frozen: [RunSummary, ...]}, compute mean/std of key metrics
    at each damage level. Analogous to sorting paper's error tolerance curve.
    """
    result = {}
    for nf, runs in summaries_by_damage.items():
        overloads = [r.final_overload for r in runs]
        ratios = [r.overload_ratio for r in runs]
        dgs = [r.dg_index for r in runs]
        failed = [r.total_failed_placements for r in runs]
        result[nf] = {
            'mean_overload': float(np.mean(overloads)),
            'std_overload': float(np.std(overloads)),
            'mean_ratio': float(np.mean(ratios)),
            'mean_dg_index': float(np.mean(dgs)),
            'std_dg_index': float(np.std(dgs)),
            'mean_failed': float(np.mean(failed)),
        }
    return result


def detect_phases(overloads: list[int]) -> list[dict]:
    """Classify phases in an overload trajectory.

    Identifies contiguous regions of the trajectory as one of:
        'descent'  -- overload is decreasing on average
        'plateau'  -- overload is stable
        'increase' -- overload is increasing on average

    Returns a list of dicts with keys:
        phase:     str ('descent', 'plateau', 'increase')
        start:     int (index into overloads)
        end:       int (index, exclusive)
        start_val: int
        end_val:   int
    """
    if len(overloads) < 2:
        return [{'phase': 'plateau', 'start': 0, 'end': len(overloads),
                 'start_val': overloads[0] if overloads else 0,
                 'end_val': overloads[0] if overloads else 0}]

    # Compute a smoothed derivative using a rolling window
    window = max(3, len(overloads) // 50)
    arr = np.array(overloads, dtype=float)
    # Pad to avoid edge effects
    padded = np.pad(arr, (window // 2, window // 2), mode='edge')
    smoothed = np.convolve(padded, np.ones(window) / window, mode='valid')[:len(arr)]

    # Classify each point
    diffs = np.diff(smoothed)
    threshold = 0.05 * max(1, np.std(arr))

    phases: list[dict] = []
    current_phase = 'plateau'
    phase_start = 0

    for i, d in enumerate(diffs):
        if d < -threshold:
            new_phase = 'descent'
        elif d > threshold:
            new_phase = 'increase'
        else:
            new_phase = 'plateau'

        if new_phase != current_phase:
            phases.append({
                'phase': current_phase,
                'start': phase_start,
                'end': i + 1,
                'start_val': int(arr[phase_start]),
                'end_val': int(arr[i]),
            })
            current_phase = new_phase
            phase_start = i + 1

    # Final phase
    phases.append({
        'phase': current_phase,
        'start': phase_start,
        'end': len(overloads),
        'start_val': int(arr[phase_start]) if phase_start < len(arr) else int(arr[-1]),
        'end_val': int(arr[-1]),
    })

    return phases


def recovery_completeness(
    control_overload: float,
    recovered_overload: float,
    theoretical_min: float,
) -> float:
    """Compute how completely the system recovered after damage.

    Returns a value in [0, 1] where 1.0 means full recovery to control
    level and 0.0 means no recovery (stayed at theoretical minimum
    distance from control).

    Args:
        control_overload:   final overload of undamaged control run.
        recovered_overload: final overload after damage and healing.
        theoretical_min:    theoretical minimum overload (m - n_active).

    Returns:
        Completeness ratio. Clamped to [0, 1].
    """
    # If control is already at theoretical min, recovery is trivially complete
    if abs(control_overload - theoretical_min) < 1e-9:
        return 1.0 if abs(recovered_overload - control_overload) < 1e-9 else 0.0

    # How close is the recovered state to the control state,
    # relative to the gap between theoretical_min and control?
    gap = abs(control_overload - theoretical_min)
    distance = abs(recovered_overload - control_overload)
    completeness = 1.0 - min(distance / gap, 1.0)
    return max(0.0, min(1.0, completeness))


def trajectory_stats(overloads: list[int]) -> dict:
    """Compute summary statistics for an overload trajectory.

    Returns dict with keys:
        slope:          float -- linear regression slope (overload vs step)
        variance:       float -- variance of overload values
        final_min_ratio: float -- final_overload / min_overload (>= 1)
        mean:           float -- mean overload
        median:         float -- median overload
        range:          int   -- max - min overload
    """
    if not overloads:
        return {
            'slope': 0.0,
            'variance': 0.0,
            'final_min_ratio': 1.0,
            'mean': 0.0,
            'median': 0.0,
            'range': 0,
        }

    arr = np.array(overloads, dtype=float)
    steps = np.arange(len(arr), dtype=float)

    # Linear regression for slope
    if len(arr) > 1:
        slope = float(np.polyfit(steps, arr, 1)[0])
    else:
        slope = 0.0

    min_val = float(np.min(arr))
    final_val = float(arr[-1])
    final_min_ratio = final_val / min_val if min_val > 0 else (
        1.0 if final_val == 0 else float('inf')
    )

    return {
        'slope': slope,
        'variance': float(np.var(arr)),
        'final_min_ratio': final_min_ratio,
        'mean': float(np.mean(arr)),
        'median': float(np.median(arr)),
        'range': int(np.max(arr) - np.min(arr)),
    }


def policy_aggregation(probe: Any, policies: list[Any]) -> float:
    """
    Aggregation metric: do pigeons with the same policy cluster
    in the same holes? Analogous to Algotype aggregation in sorting paper.

    Returns aggregation value in [0, 1]. Higher = more clustering by policy.
    """
    if not probe.assignment_snapshots:
        return 0.0

    final_assignments = probe.assignment_snapshots[-1]
    n_holes = max(max(a for a in final_assignments if a >= 0) + 1, 1) \
        if any(a >= 0 for a in final_assignments) else 1

    # for each hole, what fraction of its pigeons share the majority policy?
    from collections import Counter
    total_agreement = 0
    total_placed = 0
    for h in range(n_holes):
        pigeons_in_h = [i for i, a in enumerate(final_assignments) if a == h]
        if len(pigeons_in_h) <= 1:
            continue
        policy_counts = Counter(policies[p] for p in pigeons_in_h)
        majority = policy_counts.most_common(1)[0][1]
        total_agreement += majority
        total_placed += len(pigeons_in_h)

    return total_agreement / total_placed if total_placed > 0 else 0.0
