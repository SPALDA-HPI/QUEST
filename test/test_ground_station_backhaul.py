"""Behavior tests for optional direct ground-station backhaul links."""

import copy
import unittest

import celestial.types
import numpy as np
from celestial.antenna import AntennaScheduler
from celestial.config import Config
from celestial.satgen_constellation import SatgenConstellation
from celestial.shell import GST_SAT_LINK_DTYPE
from test.test_config_activation import valid_config


class RecordingWriter:
    """Capture serialized topology events without writing a topology archive."""

    def __init__(self) -> None:
        self.links = []

    def init_machine(self, *_args: object) -> None:
        pass

    def diff_machine(self, *_args: object) -> None:
        pass

    def diff_link(self, timestamp: int, source: object, target: object, link: object) -> None:
        self.links.append((timestamp, source, target, link))


class ShellWithGroundRoute:
    """Expose one legacy GS-GS route and one unrelated satellite route."""

    shell_identifier = 1

    def __init__(self) -> None:
        ground_0 = celestial.types.MachineID(0, 0, "station-0")
        ground_1 = celestial.types.MachineID(0, 1, "station-1")
        satellite = celestial.types.MachineID(1, 0)
        self.ground_link = celestial.types.Link(
            1_000, 10_000, False, satellite, satellite
        )
        self.satellite_link = celestial.types.Link(
            2_000, 20_000, False, ground_0, satellite
        )
        self.link_diff = {
            ground_0: {ground_1: self.ground_link},
            satellite: {ground_0: self.satellite_link},
        }

    def prepare_step(self, _timestamp: int) -> None:
        pass

    def get_gst_links(self) -> np.ndarray:
        return np.array([], dtype=GST_SAT_LINK_DTYPE)

    def finish_step(self, *_args: object, **_kwargs: object) -> None:
        pass

    def get_sat_node_diffs(self) -> dict:
        return {}

    def get_link_diff(self) -> dict:
        return self.link_diff


def config_with_stations(count: int, *, direct_backhaul: bool) -> Config:
    """Build a small real Config with fixed, hand-checkable station positions."""
    text_config = valid_config()
    text_config["ground_station"] = [
        {
            "name": f"station-{index}",
            "lat": 0.0,
            "long": float(index),
        }
        for index in range(count)
    ]
    if direct_backhaul:
        text_config["network_params"].update(
            {
                "ground_station_bandwidth_kbits": 10_000_000,
                "ground_station_path_stretch": 1.0,
            }
        )
    return Config(copy.deepcopy(text_config))


class GroundStationBackhaulTest(unittest.TestCase):
    """Catch missing, duplicate, or incorrectly parameterized GS-pair links."""

    def test_two_stations_get_one_direct_pair_at_the_configured_rate(self) -> None:
        writer = RecordingWriter()

        SatgenConstellation(config_with_stations(2, direct_backhaul=True), writer)

        self.assertEqual(len(writer.links), 1)
        timestamp, source, target, link = writer.links[0]
        self.assertEqual(timestamp, 0)
        self.assertEqual(source, celestial.types.MachineID(0, 0, "station-0"))
        self.assertEqual(target, celestial.types.MachineID(0, 1, "station-1"))
        self.assertEqual(int(celestial.types.Link_latency_us(link)), 556)
        self.assertEqual(
            int(celestial.types.Link_bandwidth_kbits(link)), 10_000_000
        )
        self.assertFalse(bool(celestial.types.Link_blocked(link)))
        self.assertEqual(celestial.types.Link_next_hop(link), target)
        self.assertEqual(celestial.types.Link_prev_hop(link), source)

    def test_three_stations_get_one_independent_link_per_pair(self) -> None:
        writer = RecordingWriter()

        SatgenConstellation(config_with_stations(3, direct_backhaul=True), writer)

        pairs = {(source[1], target[1]) for _, source, target, _ in writer.links}
        self.assertEqual(pairs, {(0, 1), (0, 2), (1, 2)})
        self.assertEqual(
            {
                int(celestial.types.Link_bandwidth_kbits(link))
                for _, _, _, link in writer.links
            },
            {10_000_000},
        )

    def test_legacy_config_emits_no_static_ground_station_pair(self) -> None:
        writer = RecordingWriter()

        SatgenConstellation(config_with_stations(2, direct_backhaul=False), writer)

        self.assertEqual(writer.links, [])

    def test_direct_backhaul_suppresses_shell_ground_station_routes(self) -> None:
        writer = RecordingWriter()
        shell = ShellWithGroundRoute()
        constellation = object.__new__(SatgenConstellation)
        constellation.current_time = 0
        constellation.shells = [shell]
        constellation.ground_stations = [object(), object()]
        constellation.antenna_scheduler = AntennaScheduler([None, None])
        constellation.direct_ground_station_backhaul_enabled = True
        constellation.writer = writer

        constellation.step(5)

        emitted_links = [link for _, _, _, link in writer.links]
        self.assertEqual(emitted_links, [shell.satellite_link])


if __name__ == "__main__":
    unittest.main()
