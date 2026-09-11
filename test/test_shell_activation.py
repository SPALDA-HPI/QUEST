"""Integration tests for activation decisions inside one Celestial shell."""

import unittest

from celestial.activation import SatelliteActivation
from celestial.config import BoundingBox, GroundStation, GroundStationConnectionType
from celestial.config import MachineConfig
from celestial.shell import Shell
from celestial.types import MachineID_id, VMState


def ground_station() -> GroundStation:
    """Place one test ground station below satellite zero at simulation start."""
    return GroundStation(
        name="ground",
        lat=0.0,
        lng=0.0,
        gts_bandwidth_kbits=10_000,
        min_elevation=0.0,
        connection_type=GroundStationConnectionType.ALL,
        machine_config=MachineConfig(1, 128, 1, "vmlinux", "stream.img", []),
    )


def shell(policy: SatelliteActivation, with_ground_station: bool) -> Shell:
    """Return a tiny real orbital shell suitable for fast tests."""
    return Shell(
        shell_identifier=1,
        planes=1,
        sats=4,
        altitude_km=550.0,
        inclination=0.0,
        arc_of_ascending_nodes=360.0,
        eccentricity=0.0,
        isl_bandwidth_kbits=10_000,
        bbox=BoundingBox(-90.0, -180.0, 90.0, 180.0),
        ground_stations=[ground_station()] if with_ground_station else [],
        satellite_activation=policy,
    )


class ShellActivationTest(unittest.TestCase):
    """Catch activation being calculated before contact links or from paths."""

    def test_bbox_policy_activates_every_satellite_in_the_global_bbox(self) -> None:
        constellation_shell = shell(SatelliteActivation.BBOX, False)

        constellation_shell.step(0, calculate_diffs=True)

        active_ids = {
            int(MachineID_id(machine_id))
            for machine_id, state in constellation_shell.get_sat_node_diffs().items()
            if state == VMState.ACTIVE
        }
        self.assertEqual(active_ids, {0, 1, 2, 3})

    def test_contact_policy_activates_exactly_the_directly_linked_satellites(self) -> None:
        constellation_shell = shell(
            SatelliteActivation.GROUND_STATION_CONTACT, True
        )

        constellation_shell.step(0, calculate_diffs=True)

        direct_ids = {
            int(link["sat"]) for link in constellation_shell.get_gst_links()
        }
        active_ids = {
            int(MachineID_id(machine_id))
            for machine_id, state in constellation_shell.get_sat_node_diffs().items()
            if state == VMState.ACTIVE
        }
        self.assertGreater(len(direct_ids), 0)
        self.assertLess(len(direct_ids), 4)
        self.assertEqual(active_ids, direct_ids)

    def test_prepare_step_exposes_physical_ground_station_contacts(self) -> None:
        constellation_shell = shell(
            SatelliteActivation.GROUND_STATION_CONTACT, True
        )

        constellation_shell.prepare_step(0)

        self.assertGreater(len(constellation_shell.get_gst_links()), 0)

    def test_finish_step_filters_contacts_before_activation(self) -> None:
        constellation_shell = shell(
            SatelliteActivation.GROUND_STATION_CONTACT, True
        )
        constellation_shell.prepare_step(0)
        selected_satellite = int(constellation_shell.get_gst_links()[0]["sat"])

        constellation_shell.finish_step(
            calculate_diffs=True,
            selected_contacts={0: {selected_satellite}},
        )

        self.assertEqual(
            {int(link["sat"]) for link in constellation_shell.get_gst_links()},
            {selected_satellite},
        )
        active_ids = {
            int(MachineID_id(machine_id))
            for machine_id, state in constellation_shell.get_sat_node_diffs().items()
            if state == VMState.ACTIVE
        }
        self.assertEqual(active_ids, {selected_satellite})


if __name__ == "__main__":
    unittest.main()
