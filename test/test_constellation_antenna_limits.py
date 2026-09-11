"""Integration tests for global antenna selection across orbital shells."""

import unittest

import numpy as np

import celestial.config
from celestial.antenna import AntennaScheduler
from celestial.satgen_connstellation import SatgenConstellation
from celestial.shell import GST_SAT_LINK_DTYPE


class RecordingShell:
    def __init__(self, shell_identifier: int, events: list[str]) -> None:
        self.shell_identifier = shell_identifier
        self.events = events
        self.selected_contacts = None
        self.links = np.array(
            [(-1, 0, 1_000)], dtype=GST_SAT_LINK_DTYPE
        )

    def prepare_step(self, _time: int) -> None:
        self.events.append(f"prepare-{self.shell_identifier}")

    def get_gst_links(self) -> np.ndarray:
        return self.links

    def finish_step(
        self,
        _calculate_diffs: bool,
        _delay_update_threshold_us: int,
        selected_contacts: dict[int, set[int]],
    ) -> None:
        self.events.append(f"finish-{self.shell_identifier}")
        self.selected_contacts = selected_contacts

    def get_sat_node_diffs(self) -> dict:
        return {}

    def get_link_diff(self) -> dict:
        return {}


class RecordingWriter:
    def diff_machine(self, *_args: object) -> None:
        pass

    def diff_link(self, *_args: object) -> None:
        pass


class ConstellationAntennaLimitTest(unittest.TestCase):
    def test_one_antenna_is_shared_across_all_shells(self) -> None:
        events: list[str] = []
        constellation = object.__new__(SatgenConstellation)
        constellation.current_time = 0
        constellation.shells = [RecordingShell(1, events), RecordingShell(2, events)]
        constellation.ground_stations = [object()]
        constellation.writer = RecordingWriter()
        constellation.antenna_scheduler = AntennaScheduler([1])

        constellation.step(0)

        self.assertEqual(
            events,
            ["prepare-1", "prepare-2", "finish-1", "finish-2"],
        )
        self.assertEqual(constellation.shells[0].selected_contacts, {0: {0}})
        self.assertEqual(constellation.shells[1].selected_contacts, {0: set()})


if __name__ == "__main__":
    unittest.main()
