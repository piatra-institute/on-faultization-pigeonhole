"""
Faultized Pigeonhole Model

m pigeons, n holes (m > n). Each pigeon is an autonomous agent with a local
policy for choosing a hole. Holes can be frozen (damaged). The system
self-organizes around the unavoidable overload O >= m - n.

Applies Levin's faultization methodology: systematically perturb the interface
between local policies and the pigeonhole pattern (O_min = m - n) to reveal
what patterns from the latent space the system accesses (Levin, 2026).

Flat-file layout matching faultization conventions. No packages, just scripts.
"""
from __future__ import annotations

import random
from typing import Any, Callable

import numpy as np
from dataclasses import dataclass, field
from enum import Enum, auto


# ============================================================================
# Enums
# ============================================================================

class HoleStatus(Enum):
    ACTIVE = auto()
    FROZEN = auto()       # rejects pigeons silently (damaged hardware)
    MISLEADING = auto()   # reports empty but is actually full


class PolicyType(Enum):
    GREEDY = auto()       # pick first visible hole with lowest load
    EXPLORATORY = auto()  # sample wider, pick best
    REPULSIVE = auto()    # probabilistic escape from crowded holes
    COOPERATIVE = auto()  # move only if global potential decreases


# ============================================================================
# Hooks — same pattern as morphogpt
# ============================================================================

class Hooks:
    """
    Named hook points in the pigeonhole computation.
    Each hook: fn(value, step=step) -> modified_value or None.
    """

    def __init__(self) -> None:
        self._hooks: dict[str, list[Callable]] = {}
        self.step: int = 0

    def register(self, name: str, fn: Callable) -> None:
        self._hooks.setdefault(name, []).append(fn)

    def clear(self, name: str | None = None) -> None:
        if name is None:
            self._hooks.clear()
        else:
            self._hooks.pop(name, None)

    def apply(self, name: str, value: Any) -> Any:
        for fn in self._hooks.get(name, []):
            result = fn(value, step=self.step)
            if result is not None:
                value = result
        return value

    def has(self, name: str) -> bool:
        return name in self._hooks and len(self._hooks[name]) > 0


# ============================================================================
# Probe — records system trajectory
# ============================================================================

class Probe:
    """Records the full trajectory of the system through state space."""

    def __init__(self, record_interval: int = 1) -> None:
        self.record_interval: int = record_interval
        self.steps: list[int] = []
        self.overloads: list[int] = []
        self.potentials: list[float] = []
        self.max_loads: list[int] = []
        self.unplaced_counts: list[int] = []
        self.load_snapshots: list[np.ndarray] = []      # full load vector at each recorded step
        self.assignment_snapshots: list[list[int]] = []  # full assignment vector
        self.moves: list[tuple[int, int, int, int, bool]] = []  # (step, pigeon_id, from_hole, to_hole, success)

    def record(self, step: int, loads: np.ndarray, assignments: list[int],
               overload: int, potential: float, max_load: int, unplaced: int) -> None:
        if step % self.record_interval == 0:
            self.steps.append(step)
            self.overloads.append(overload)
            self.potentials.append(potential)
            self.max_loads.append(max_load)
            self.unplaced_counts.append(unplaced)
            self.load_snapshots.append(loads.copy())
            self.assignment_snapshots.append(assignments[:])

    def record_move(self, step: int, pigeon_id: int, from_hole: int, to_hole: int, success: bool) -> None:
        self.moves.append((step, pigeon_id, from_hole, to_hole, success))


# ============================================================================
# Config
# ============================================================================

@dataclass
class Config:
    m: int = 10          # pigeons
    n: int = 7           # holes
    frozen_holes: int = 0
    misleading_holes: int = 0
    policy: PolicyType = PolicyType.GREEDY
    mixed_policies: list[PolicyType] | None = None
    view_radius: int = 3
    alpha: float = 1.0   # overload penalty weight
    beta: float = 0.5    # concentration penalty weight
    gamma: float = 10.0  # unplaced penalty weight
    num_steps: int = 500
    seed: int | None = None

    def __post_init__(self) -> None:
        assert self.m > 0, f'm must be positive, got {self.m}'
        assert self.n > 0, f'n must be positive, got {self.n}'
        assert self.m > self.n, f'm ({self.m}) must be > n ({self.n})'
        assert 0 <= self.frozen_holes < self.n, f'frozen_holes must be in [0, {self.n}), got {self.frozen_holes}'


def make_config(**kwargs: Any) -> Config:
    return Config(**kwargs)


# ============================================================================
# Core simulation
# ============================================================================

class PigeonholeSystem:
    """
    Decentralized pigeonhole placement.

    Each step: one pigeon is activated asynchronously, inspects local
    information, and decides whether to move. Hooks intercept at every
    decision point.

    Hook points:
        'pigeon_view'       — what the pigeon sees (list of (hole_id, load))
        'pigeon_decision'   — chosen target hole_id (or None)
        'placement_attempt' — (pigeon_id, target_hole_id) before checking frozen
        'post_step'         — full state after the step
    """

    def __init__(self, config: Config, hooks: Hooks | None = None,
                 probe: Probe | None = None):
        self.config = config
        self.hooks = hooks or Hooks()
        self.probe = probe or Probe()
        self.rng = random.Random(config.seed)
        self.np_rng = np.random.RandomState(config.seed)

        self.m = config.m
        self.n = config.n

        # hole status array
        self.hole_status = np.array([HoleStatus.ACTIVE] * self.n)
        self._apply_damage(config)

        # pigeon policies
        if config.mixed_policies is not None:
            assert len(config.mixed_policies) == self.m
            self.policies = list(config.mixed_policies)
        else:
            self.policies = [config.policy] * self.m

        # assignments: pigeon_id -> hole_id (-1 = unplaced)
        self.assignments = np.full(self.m, -1, dtype=int)

        # view radius per pigeon (can be overridden by hooks)
        self.view_radius = config.view_radius

        self.step_count = 0

    def _apply_damage(self, config: Config):
        """Freeze and mislead holes."""
        all_ids = list(range(self.n))
        self.rng.shuffle(all_ids)
        idx = 0
        for _ in range(min(config.frozen_holes, self.n)):
            self.hole_status[all_ids[idx]] = HoleStatus.FROZEN
            idx += 1
        for _ in range(min(config.misleading_holes, self.n - idx)):
            self.hole_status[all_ids[idx]] = HoleStatus.MISLEADING
            idx += 1

    # --- state queries ---

    def loads(self) -> np.ndarray:
        """Load vector: count of pigeons in each hole."""
        loads = np.zeros(self.n, dtype=int)
        for a in self.assignments:
            if a >= 0:
                loads[a] += 1
        return loads

    def overload(self, loads: np.ndarray | None = None) -> int:
        if loads is None:
            loads = self.loads()
        return int(np.sum(np.maximum(loads - 1, 0)))

    def max_load(self, loads: np.ndarray | None = None) -> int:
        if loads is None:
            loads = self.loads()
        return int(np.max(loads)) if self.n > 0 else 0

    def unplaced_count(self) -> int:
        return int(np.sum(self.assignments < 0))

    def potential(self, loads: np.ndarray | None = None) -> float:
        if loads is None:
            loads = self.loads()
        excess = np.maximum(loads - 1, 0)
        return float(
            self.config.alpha * np.sum(excess)
            + self.config.beta * np.sum(excess ** 2)
            + self.config.gamma * self.unplaced_count()
        )

    def n_active_holes(self) -> int:
        return int(np.sum([s == HoleStatus.ACTIVE for s in self.hole_status]))

    def n_usable_holes(self) -> int:
        """Holes that can still accept pigeons.

        Misleading holes are deceptive but usable; frozen holes are not.
        """
        return int(np.sum([s != HoleStatus.FROZEN for s in self.hole_status]))

    def _record(self) -> None:
        loads = self.loads()
        self.probe.record(
            step=self.step_count,
            loads=loads,
            assignments=list(self.assignments),
            overload=self.overload(loads),
            potential=self.potential(loads),
            max_load=self.max_load(loads),
            unplaced=self.unplaced_count(),
        )

    # --- pigeon view and action ---

    def _visible_holes(self, pigeon_id: int) -> list[tuple[int, int]]:
        """What this pigeon can see: list of (hole_id, reported_load)."""
        k = min(self.view_radius, self.n)
        sample_ids = self.rng.sample(range(self.n), k)
        loads = self.loads()

        view = []
        for h in sample_ids:
            if self.hole_status[h] == HoleStatus.MISLEADING:
                # misleading hole reports 0 load regardless
                view.append((h, 0))
            else:
                view.append((h, int(loads[h])))

        # hook: pigeon_view
        view = self.hooks.apply('pigeon_view', view)
        return view

    def _decide(self, pigeon_id: int, view: list[tuple[int, int]]) -> int | None:
        """Apply pigeon's policy to choose a target hole. Returns hole_id or None."""
        policy = self.policies[pigeon_id]
        current_hole = int(self.assignments[pigeon_id])
        loads = self.loads()
        current_load = int(loads[current_hole]) if current_hole >= 0 else 999

        if policy == PolicyType.GREEDY:
            best_h, best_l = min(view, key=lambda x: x[1])
            target = best_h if best_l < current_load else None

        elif policy == PolicyType.EXPLORATORY:
            # see more holes (double sample if possible)
            extra_k = min(self.view_radius * 2, self.n)
            extra_ids = self.rng.sample(range(self.n), extra_k)
            full_view = view + [(h, int(loads[h])) for h in extra_ids if h not in dict(view)]
            best_h, best_l = min(full_view, key=lambda x: x[1])
            target = best_h if best_l < current_load else None

        elif policy == PolicyType.REPULSIVE:
            if current_hole < 0:
                best_h, best_l = min(view, key=lambda x: x[1])
                target = best_h
            elif current_load <= 1:
                target = None
            elif self.rng.random() < (current_load - 1) / current_load:
                best_h, best_l = min(view, key=lambda x: x[1])
                target = best_h if best_l < current_load else None
            else:
                target = None

        elif policy == PolicyType.COOPERATIVE:
            if current_hole < 0:
                best_h, _ = min(view, key=lambda x: x[1])
                target = best_h
            else:
                current_phi = self.potential(loads)
                best_target = None
                best_phi = current_phi
                for h, _ in view:
                    if h == current_hole:
                        continue
                    trial = loads.copy()
                    trial[current_hole] -= 1
                    trial[h] += 1
                    trial_phi = self.potential(trial)
                    if trial_phi < best_phi:
                        best_phi = trial_phi
                        best_target = h
                target = best_target
        else:
            target = None

        # hook: pigeon_decision
        target = self.hooks.apply('pigeon_decision', target)
        return target

    def _try_place(self, pigeon_id: int, target: int) -> bool:
        """Attempt placement. Frozen holes reject silently."""
        # hook: placement_attempt
        attempt = self.hooks.apply('placement_attempt', (pigeon_id, target))
        if attempt is None:
            return False
        pigeon_id, target = attempt

        if self.hole_status[target] == HoleStatus.FROZEN:
            self.probe.record_move(self.step_count, pigeon_id,
                                   int(self.assignments[pigeon_id]), target, False)
            return False

        old_hole = int(self.assignments[pigeon_id])
        self.assignments[pigeon_id] = target
        self.probe.record_move(self.step_count, pigeon_id, old_hole, target, True)
        return True

    # --- simulation ---

    def initial_placement(self) -> None:
        """Random initial placement."""
        for p in range(self.m):
            target = self.rng.randint(0, self.n - 1)
            if self.hole_status[target] != HoleStatus.FROZEN:
                self.assignments[p] = target
            else:
                target2 = self.rng.randint(0, self.n - 1)
                if self.hole_status[target2] != HoleStatus.FROZEN:
                    self.assignments[p] = target2
        self._record()

    def step(self) -> None:
        """Activate one random pigeon."""
        self.step_count += 1
        self.hooks.step = self.step_count

        pigeon_id = self.rng.randint(0, self.m - 1)
        view = self._visible_holes(pigeon_id)
        target = self._decide(pigeon_id, view)

        if target is not None:
            self._try_place(pigeon_id, target)

        # hook: post_step
        self.hooks.apply('post_step', None)

        self._record()

    def run(self) -> Probe:
        """Run full simulation."""
        self.initial_placement()
        for _ in range(self.config.num_steps):
            self.step()
        return self.probe
