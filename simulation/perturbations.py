"""
Faultized Pigeonhole — Perturbations

Hook-based perturbations for the pigeonhole system. Each perturbation
returns (hook_name, hook_fn) or registers directly on a Hooks instance.

Perturbation categories (Platonic Space / faultization framing):
  A. Interface degradation  — frozen holes, misleading holes
  B. Perceptual corruption  — pigeons see wrong loads
  C. Policy corruption      — pigeons sometimes ignore their own policy
  D. Dynamic interface      — holes break/heal mid-run
  E. Chimeric interfaces    — mixed policy populations
"""
from __future__ import annotations

import random
from typing import Callable

import numpy as np
from model import Hooks, HoleStatus


# ============================================================================
# A. DAMAGED SUBSTRATE
# ============================================================================

def make_freeze_hole(hole_statuses: np.ndarray, hole_id: int) -> None:
    """Freeze a specific hole (make it reject all pigeons)."""
    hole_statuses[hole_id] = HoleStatus.FROZEN


def make_misleading_hole(hole_statuses: np.ndarray, hole_id: int) -> None:
    """Make a hole report empty when it may not be."""
    hole_statuses[hole_id] = HoleStatus.MISLEADING


# ============================================================================
# B. NOISY PERCEPTION
# ============================================================================

def make_noisy_view(noise_std: float = 1.0, rng: random.Random | None = None) -> tuple[str, Callable]:
    """Add Gaussian noise to reported loads. Returns (hook_name, hook_fn)."""
    _rng = rng or random.Random()
    def hook(view: list[tuple[int, int]], step: int = 0) -> list[tuple[int, int]]:
        return [(h, max(0, int(l + _rng.gauss(0, noise_std)))) for h, l in view]
    return 'pigeon_view', hook


def make_blind_pigeon(blind_prob: float = 0.2, rng: random.Random | None = None) -> tuple[str, Callable]:
    """With some probability, pigeon sees all holes as equally loaded."""
    _rng = rng or random.Random()
    def hook(view: list[tuple[int, int]], step: int = 0) -> list[tuple[int, int]] | None:
        if _rng.random() < blind_prob:
            avg = sum(l for _, l in view) // max(len(view), 1)
            return [(h, avg) for h, _ in view]
        return None
    return 'pigeon_view', hook


def make_inverted_view() -> tuple[str, Callable]:
    """Pigeon sees loads inverted: crowded holes appear empty."""
    def hook(view: list[tuple[int, int]], step: int = 0) -> list[tuple[int, int]]:
        max_l = max(l for _, l in view) if view else 0
        return [(h, max_l - l) for h, l in view]
    return 'pigeon_view', hook


# ============================================================================
# C. POLICY DAMAGE
# ============================================================================

def make_stubborn_pigeon(stubborn_prob: float = 0.3, rng: random.Random | None = None) -> tuple[str, Callable]:
    """Pigeon sometimes refuses to move regardless of what policy says."""
    _rng = rng or random.Random()
    def hook(target: int | None, step: int = 0) -> int | None:
        if target is not None and _rng.random() < stubborn_prob:
            return None  # refuse to move
        return target  # pass through
    return 'pigeon_decision', hook


def make_random_mover(random_prob: float = 0.1, n_holes: int = 7, rng: random.Random | None = None) -> tuple[str, Callable]:
    """Pigeon sometimes ignores policy and picks a random hole."""
    _rng = rng or random.Random()
    def hook(target: int | None, step: int = 0) -> int | None:
        if _rng.random() < random_prob:
            return _rng.randint(0, n_holes - 1)
        return target
    return 'pigeon_decision', hook


def make_contrarian(contrarian_prob: float = 0.15, n_holes: int = 7, rng: random.Random | None = None) -> tuple[str, Callable]:
    """Pigeon sometimes deliberately picks a crowded hole."""
    _rng = rng or random.Random()
    def hook(target: int | None, step: int = 0) -> int | None:
        if target is not None and _rng.random() < contrarian_prob:
            # pick a random different hole (likely worse)
            return _rng.randint(0, n_holes - 1)
        return target
    return 'pigeon_decision', hook


# ============================================================================
# D. DYNAMIC DAMAGE (scheduled)
# ============================================================================

def make_hole_breaker(system: object, break_step: int, hole_id: int) -> tuple[str, Callable]:
    """Freeze a hole mid-simulation at a specific step."""
    def hook(value: object, step: int = 0) -> None:
        if step == break_step:
            system.hole_status[hole_id] = HoleStatus.FROZEN
        return None
    return 'post_step', hook


def make_hole_healer(system: object, heal_step: int, hole_id: int) -> tuple[str, Callable]:
    """Unfreeze a hole mid-simulation."""
    def hook(value: object, step: int = 0) -> None:
        if step == heal_step:
            system.hole_status[hole_id] = HoleStatus.ACTIVE
        return None
    return 'post_step', hook


def make_progressive_damage(system: object, start_step: int, interval: int, max_frozen: int) -> tuple[str, Callable]:
    """Progressively freeze holes one at a time."""
    frozen_count = [0]
    def hook(value: object, step: int = 0) -> None:
        if step >= start_step and (step - start_step) % interval == 0:
            if frozen_count[0] < max_frozen:
                # find an active hole to freeze
                for i in range(system.n):
                    if system.hole_status[i] == HoleStatus.ACTIVE:
                        system.hole_status[i] = HoleStatus.FROZEN
                        frozen_count[0] += 1
                        break
        return None
    return 'post_step', hook


# ============================================================================
# E. SCHEDULES (matching morphogpt pattern)
# ============================================================================

def schedule_chronic(hook_fn: Callable) -> Callable:
    """Always active."""
    return hook_fn


def schedule_acute(hook_fn: Callable, start_step: int, end_step: int) -> Callable:
    """Active only during [start_step, end_step]."""
    def scheduled(value: object, step: int = 0) -> object | None:
        if start_step <= step <= end_step:
            return hook_fn(value, step=step)
        return None
    return scheduled


def schedule_stochastic(hook_fn: Callable, prob: float, rng: random.Random | None = None) -> Callable:
    """Active with probability prob each step."""
    _rng = rng or random.Random()
    def scheduled(value: object, step: int = 0) -> object | None:
        if _rng.random() < prob:
            return hook_fn(value, step=step)
        return None
    return scheduled
