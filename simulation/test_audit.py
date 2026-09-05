"""Regression checks for measurement and intervention semantics."""
import itertools
import math
import random
import unittest

import numpy as np

from audit import (Condition, activate, conditions, encode, event, holm, initialize,
                   make_tape, mathematical_checks, minimum_squared_load, paired,
                   run_condition, state, tape_hash)
from model import Config, HoleStatus, PigeonholeSystem, PolicyType
from perturbations import make_noisy_view


class AuditTests(unittest.TestCase):
    def system(self, assignments=None):
        s = PigeonholeSystem(Config(seed=1))
        if assignments is not None:
            s.assignments[:] = assignments
        return s

    def test_identity_including_unplaced(self):
        for assigned in itertools.product(range(-1, 3), repeat=4):
            s = PigeonholeSystem(Config(m=4, n=3, seed=0))
            s.assignments[:] = assigned
            result = state(s)
            self.assertEqual(result["overload"], result["placed"]-result["occupied"])
            self.assertEqual(result["unplaced"]+result["placed"], 4)

    def test_equal_coverage_different_balance(self):
        a = self.system([0, 0, 1, 1, 2, 2, 3, 4, 5, 6])
        b = self.system([0, 0, 0, 0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(state(a)["overload"], state(b)["overload"])
        self.assertEqual((state(a)["squared_load"], state(b)["squared_load"]), (16, 22))
        self.assertEqual((state(a)["potential"], state(b)["potential"]), (4.5, 7.5))

    def test_conditional_regret(self):
        s = self.system()
        self.assertIsNone(state(s)["balance_regret"])
        s.assignments[:] = np.arange(10) % 7
        s.hole_status[0] = HoleStatus.FROZEN
        self.assertIsNone(state(s)["balance_regret"])
        self.assertEqual(state(s)["occupied_closed"], 1)

    def test_optimum_and_count_enumeration(self):
        result = mathematical_checks()
        self.assertEqual(result["load_vectors_checked"], 8008)
        self.assertEqual(result["coverage_assignments"], 29635200)
        self.assertEqual(result["balanced_assignments"], 15876000)
        self.assertEqual(result["minimum_squared_load"], 16)
        self.assertEqual(result["minimum_potential"], 4.5)

    def test_convex_move_identity(self):
        for a in range(1, 21):
            for b in range(21):
                change = (a-1)**2+(b+1)**2-a*a-b*b
                self.assertEqual(change, 2*(b-a+1))
                if b < a:
                    self.assertLessEqual(change, 0)
                if b+1 < a:
                    self.assertLess(change, 0)

    def test_general_squared_optimum(self):
        for m in range(12):
            for n in range(1, 8):
                q, r = divmod(m, n)
                loads = [q+1]*r+[q]*(n-r)
                self.assertEqual(minimum_squared_load(m, n), sum(x*x for x in loads))
        with self.assertRaises(ValueError):
            minimum_squared_load(3, 0)

    def test_truncation_is_not_rounding(self):
        self.assertEqual(encode(2-1e-6, "truncate"), 1)
        self.assertEqual(encode(2+1e-6, "truncate"), 2)
        self.assertEqual(encode(2-1e-6, "round"), 2)
        self.assertEqual(encode(2+1e-6, "round"), 2)
        self.assertEqual(encode(-0.1, "truncate"), 0)
        self.assertEqual(encode(-0.1, "float"), -0.1)

    def test_legacy_noise_uses_truncation(self):
        class NegativeNoise:
            def gauss(self, mean, std):
                return -1e-6
        _, hook = make_noisy_view(1e-6, NegativeNoise())
        self.assertEqual(hook([(0, 2)]), [(0, 1)])

    def test_tapes_are_repeatable_and_condition_independent(self):
        a, b = make_tape(6000, 301), make_tape(6000, 301)
        self.assertEqual(tape_hash(a), tape_hash(b))
        old_hash = tape_hash(a)
        run_condition(Condition("wide", radius=7), a, 301)
        run_condition(Condition("tiny", radius=1), a, 301)
        self.assertEqual(tape_hash(a), old_hash)
        self.assertFalse(np.array_equal(a["active"], make_tape(6001, 301)["active"]))

    def test_legacy_shared_seed_does_not_lock_rng_consumption(self):
        a = PigeonholeSystem(Config(seed=2, policy=PolicyType.GREEDY))
        b = PigeonholeSystem(Config(seed=2, policy=PolicyType.EXPLORATORY))
        a.initial_placement()
        b.initial_placement()
        np.testing.assert_array_equal(a.assignments, b.assignments)
        a.step()
        b.step()
        self.assertNotEqual(a.rng.getstate(), b.rng.getstate())

    def test_legacy_cooperative_uses_true_loads(self):
        s = self.system([0, 0, 1, 1, 2, 2, 3, 4, 5, 6])
        s.policies = [PolicyType.COOPERATIVE]*10
        self.assertIsNone(s._decide(0, [(1, 0), (2, 0)]))
        s.policies = [PolicyType.GREEDY]*10
        self.assertEqual(s._decide(0, [(1, 0), (2, 0)]), 1)

    def test_common_initial_proposals(self):
        tape = make_tape(6000, 301)
        a, b = self.system(), self.system()
        initialize(a, Condition("a"), tape)
        initialize(b, Condition("b", radius=7), tape)
        np.testing.assert_array_equal(a.assignments, b.assignments)
        np.testing.assert_array_equal(a.assignments, tape["initial"][:, 0])

    def test_two_rejections_leave_item_unplaced(self):
        tape = make_tape(6000, 301)
        tape["initial"][:] = 0
        s = self.system()
        initialize(s, Condition("closed", closed=1), tape)
        self.assertEqual(s.unplaced_count(), 10)

    def test_greedy_accepts_neutral_move_arrival_rejects(self):
        assignments = [0, 0, 1, 2, 3, 4, 5, 6, 2, 3]
        ids, noise = np.array([1, 0, 2, 3, 4, 5, 6]), np.zeros(7)
        a, b = self.system(assignments), self.system(assignments)
        before = state(a)["squared_load"]
        counts = activate(a, Condition("g", radius=1), 0, ids, noise)
        self.assertEqual(counts, (1, 1, 0, 1))
        self.assertEqual(state(a)["squared_load"], before)
        self.assertEqual(activate(b, Condition("a", policy="arrival", radius=1), 0, ids, noise),
                         (1, 0, 0, 0))

    def test_tiny_noise_can_raise_cost_without_quantization(self):
        assignments = [0, 0, 1, 1, 2, 2, 3, 4, 5, 6]
        ids, noise = np.array([1, 0, 2, 3, 4, 5, 6]), np.array([0, -1, 0, 0, 0, 0, 0])
        for encoding in ("float", "truncate"):
            a, b = self.system(assignments), self.system(assignments)
            activate(a, Condition("g", radius=1, sigma=1e-6, encoding=encoding), 0, ids, noise)
            activate(b, Condition("a", policy="arrival", radius=1, sigma=1e-6,
                                  encoding=encoding), 0, ids, noise)
            self.assertEqual(state(a)["squared_load"], 18)
            self.assertEqual(state(b)["squared_load"], 16)

    def test_tiny_rounded_reports_are_exact_for_bounded_tape(self):
        a = Condition("clean")
        b = Condition("rounded", encoding="round", sigma=1e-6)
        tape = make_tape(6000, 301)
        self.assertLess(np.abs(tape["noise"]).max()*1e-6, 0.5)
        self.assertEqual(run_condition(a, tape, 301), run_condition(b, tape, 301))

    def test_current_hole_is_not_relocation(self):
        s = self.system([0]*10)
        s.hole_status[0] = HoleStatus.MISLEADING
        counts = activate(s, Condition("own", radius=1), 0, np.arange(7), np.zeros(7))
        self.assertEqual(counts, (1, 0, 0, 0))

    def test_closed_hole_rejects_without_ejecting(self):
        s = self.system([0, 1, 1, 2, 2, 3, 3, 4, 5, 6])
        old = s.assignments.copy()
        s.hole_status[0] = HoleStatus.FROZEN
        self.assertFalse(s._try_place(1, 0))
        np.testing.assert_array_equal(s.assignments, old)
        self.assertEqual(state(s)["occupied_closed"], 1)

    def test_retry_finds_same_view_alternative(self):
        assignments = [-1, 5, 6, 6, 6, 6, 6, 6, 6, 6]
        a, b = self.system(assignments), self.system(assignments)
        a.hole_status[:5] = b.hole_status[:5] = HoleStatus.FROZEN
        ids, noise = np.array([0, 5, 6, 1, 2, 3, 4]), np.zeros(7)
        ordinary = activate(a, Condition("ordinary"), 0, ids, noise)
        retry = activate(b, Condition("retry", retry=True), 0, ids, noise)
        self.assertEqual(ordinary, (3, 1, 1, 0))
        self.assertEqual(retry, (3, 2, 1, 1))
        self.assertEqual(int(b.assignments[0]), 5)

    def test_closed_trap_for_every_three_hole_view(self):
        assignments = [-1, 5, 6, 6, 6, 6, 6, 6, 6, 6]
        for subset in itertools.combinations(range(7), 3):
            s = self.system(assignments)
            s.hole_status[:5] = HoleStatus.FROZEN
            counts = activate(s, Condition("trap"), 0, np.array(subset), np.zeros(7))
            self.assertEqual(counts, (3, 1, 1, 0))
            self.assertEqual(int(s.assignments[0]), -1)

    def test_event_timing_and_eviction(self):
        a = self.system(np.arange(10) % 7)
        b = self.system(np.arange(10) % 7)
        self.assertIsNone(event(a, "close", 99))
        closed = event(a, "close", 100)
        evicted = event(b, "evict", 100)
        self.assertEqual(closed["before"]["occupied"], closed["after"]["occupied"])
        self.assertEqual(closed["after"]["unplaced"], 0)
        self.assertEqual(evicted["after"]["unplaced"], 2)
        self.assertEqual(evicted["after"]["overload"], 2)
        self.assertLess(evicted["after"]["overload"], evicted["before"]["overload"])
        event(b, "evict", 300)
        self.assertEqual(b.hole_status[0], HoleStatus.ACTIVE)
        self.assertEqual(b.unplaced_count(), 2)  # reopening does not teleport items

    def test_stay_put_is_censored_from_pile(self):
        outcome = run_condition(Condition("stay", initial="pile", policy="stay"),
                                make_tape(6000, 301), 301)
        self.assertIsNone(outcome["first_coverage"])
        self.assertIsNone(outcome["first_balance"])
        self.assertEqual(outcome["last_overload_change"], 0)
        self.assertEqual(outcome["assignment_changes"], 0)
        self.assertEqual(outcome["final"]["overload"], 9)

    def test_first_coverage_does_not_mean_retained_coverage(self):
        tape = make_tape(6000, 1)
        tape["active"][0] = 3
        tape["candidates"][0] = np.arange(7)
        result = run_condition(Condition("random", initial="balanced", policy="random"), tape, 1)
        self.assertEqual(result["first_coverage"], 0)
        self.assertEqual(result["final"]["coverage_complete"], 0)
        self.assertEqual(result["moves_after_first_coverage"], 1)
        self.assertEqual(result["final"]["overload"], 4)

    def test_paired_interval_and_degenerate_case(self):
        result = paired([2, 4, 6], [1, 1, 1])
        self.assertEqual(result["difference"], 3)
        self.assertAlmostEqual(result["ci_high"], 7.9682754, places=5)
        self.assertEqual(paired([1, 1], [1, 1])["p"], 1)
        self.assertEqual(paired([2, 2], [1, 1])["p"], 0)
        with self.assertRaises(ValueError):
            paired([math.nan, 1], [0, 0])

    def test_holm_known_example(self):
        np.testing.assert_allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])

    def test_condition_names_are_unique(self):
        names = [c.name for c in conditions()]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(names), 32)


if __name__ == "__main__":
    unittest.main()
