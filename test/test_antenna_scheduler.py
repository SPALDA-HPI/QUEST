"""Behavior tests for fair, non-preemptive antenna selection."""

import unittest

from celestial.antenna import AntennaScheduler


class AntennaSchedulerTest(unittest.TestCase):
    """Catch per-shell limits, preemption, starvation, and unstable ties."""

    def test_limit_is_global_across_shells_and_ties_are_deterministic(self) -> None:
        scheduler = AntennaScheduler([2])

        selected = scheduler.select(0, {0: {(2, 0), (1, 1), (1, 0)}})

        self.assertEqual(selected[0], {(1, 0), (1, 1)})

    def test_existing_assignments_are_not_preempted(self) -> None:
        scheduler = AntennaScheduler([1])
        self.assertEqual(scheduler.select(0, {0: {(2, 0)}})[0], {(2, 0)})

        selected = scheduler.select(5, {0: {(1, 0), (2, 0)}})

        self.assertEqual(selected[0], {(2, 0)})

    def test_oldest_unserved_satellite_keeps_priority_across_a_missed_pass(
        self,
    ) -> None:
        scheduler = AntennaScheduler([1])
        scheduler.select(0, {0: {(1, 0), (1, 1)}})
        scheduler.select(5, {0: {(1, 0)}})
        scheduler.select(10, {0: set()})

        selected = scheduler.select(15, {0: {(1, 1), (1, 2)}})

        self.assertEqual(selected[0], {(1, 1)})

    def test_assignment_resets_waiting_priority(self) -> None:
        scheduler = AntennaScheduler([1])
        scheduler.select(0, {0: {(1, 0), (1, 1)}})
        scheduler.select(5, {0: {(1, 1)}})
        scheduler.select(10, {0: set()})

        selected = scheduler.select(15, {0: {(1, 0), (1, 1)}})

        self.assertEqual(selected[0], {(1, 0)})

    def test_none_selects_every_visible_satellite(self) -> None:
        scheduler = AntennaScheduler([None])
        visible = {0: {(1, 0), (2, 3)}}

        self.assertEqual(scheduler.select(0, visible), visible)


if __name__ == "__main__":
    unittest.main()
