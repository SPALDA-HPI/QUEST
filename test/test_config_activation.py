"""Configuration tests for the satellite activation policy."""

import copy
import unittest

from celestial.activation import SatelliteActivation
from celestial.config import Config


def valid_config() -> dict:
    """Return the smallest complete Celestial configuration used by a test."""
    return {
        "bbox": [-90.0, -180.0, 90.0, 180.0],
        "resolution": 5,
        "duration": 60,
        "network_params": {
            "bandwidth_kbits": 10_000,
            "min_elevation": 25.0,
            "ground_station_connection_type": "all",
        },
        "compute_params": {
            "vcpu_count": 1,
            "mem_size_mib": 128,
            "disk_size_mib": 1,
            "kernel": "vmlinux",
            "rootfs": "stream.img",
        },
        "shell": [
            {
                "planes": 1,
                "sats": 1,
                "altitude_km": 550,
                "inclination": 53.0,
                "arc_of_ascending_nodes": 360.0,
                "eccentricity": 0.0,
            }
        ],
    }


def config_with_ground_station() -> dict:
    """Return a complete configuration with one ground station."""
    text_config = valid_config()
    text_config["ground_station"] = [
        {"name": "ground", "lat": 52.5, "long": 13.3}
    ]
    return text_config


class ActivationConfigTest(unittest.TestCase):
    """Catch validation or defaulting that changes legacy configurations."""

    def test_bbox_is_the_default_for_existing_configs(self) -> None:
        config = Config(copy.deepcopy(valid_config()))

        self.assertEqual(config.satellite_activation, SatelliteActivation.BBOX)

    def test_contact_policy_requires_a_ground_station(self) -> None:
        text_config = valid_config()
        text_config["satellite_activation"] = "ground_station_contact"

        with self.assertRaisesRegex(
            ValueError, "ground_station_contact requires at least one ground station"
        ):
            Config(text_config)

    def test_contact_policy_is_exposed_as_an_enum(self) -> None:
        text_config = config_with_ground_station()
        text_config["satellite_activation"] = "ground_station_contact"

        config = Config(text_config)

        self.assertEqual(
            config.satellite_activation,
            SatelliteActivation.GROUND_STATION_CONTACT,
        )

    def test_antenna_number_is_optional_for_legacy_all(self) -> None:
        config = Config(config_with_ground_station())

        self.assertIsNone(config.ground_stations[0].antenna_number)

    def test_positive_antenna_number_is_exposed(self) -> None:
        text_config = config_with_ground_station()
        text_config["ground_station"][0]["antenna_number"] = 4

        config = Config(text_config)

        self.assertEqual(config.ground_stations[0].antenna_number, 4)

    def test_non_positive_antenna_number_is_rejected(self) -> None:
        text_config = config_with_ground_station()
        text_config["ground_station"][0]["antenna_number"] = 0

        with self.assertRaises(ValueError):
            Config(text_config)

    def test_one_and_antenna_number_are_rejected(self) -> None:
        text_config = config_with_ground_station()
        text_config["network_params"]["ground_station_connection_type"] = "one"
        text_config["ground_station"][0]["antenna_number"] = 2

        with self.assertRaisesRegex(ValueError, "antenna_number.*all"):
            Config(text_config)

    def test_legacy_config_has_no_ground_station_backhaul(self) -> None:
        config = Config(config_with_ground_station())

        self.assertIsNone(
            getattr(config, "ground_station_bandwidth_kbits", "missing")
        )
        self.assertIsNone(getattr(config, "ground_station_path_stretch", "missing"))

    def test_ground_station_backhaul_fields_must_be_supplied_together(self) -> None:
        text_config = config_with_ground_station()
        text_config["network_params"]["ground_station_bandwidth_kbits"] = 10_000_000

        with self.assertRaisesRegex(ValueError, "must be supplied together"):
            Config(text_config)

    def test_ground_station_backhaul_values_are_exposed(self) -> None:
        text_config = config_with_ground_station()
        text_config["network_params"].update(
            {
                "ground_station_bandwidth_kbits": 10_000_000,
                "ground_station_path_stretch": 1.3,
            }
        )

        try:
            config = Config(text_config)
        except ValueError as error:
            self.fail(f"valid backhaul configuration was rejected: {error}")

        self.assertEqual(config.ground_station_bandwidth_kbits, 10_000_000)
        self.assertEqual(config.ground_station_path_stretch, 1.3)

    def test_ground_station_overrides_survive_backhaul_configuration(self) -> None:
        text_config = config_with_ground_station()
        text_config["network_params"].update(
            {
                "ground_station_bandwidth_kbits": 10_000_000,
                "ground_station_path_stretch": 1.3,
            }
        )
        text_config["ground_station"].append(
            {
                "name": "edge",
                "lat": 78.2,
                "long": 15.4,
                "antenna_number": 2,
                "network_params": {"bandwidth_kbits": 280_000},
                "compute_params": {
                    "vcpu_count": 4,
                    "mem_size_mib": 1024,
                    "disk_size_mib": 2048,
                },
            }
        )

        try:
            config = Config(text_config)
        except ValueError as error:
            self.fail(f"valid backhaul configuration was rejected: {error}")

        edge = config.ground_stations[1]
        self.assertEqual(edge.gts_bandwidth_kbits, 280_000)
        self.assertEqual(edge.antenna_number, 2)
        self.assertEqual(edge.machine_config.vcpu_count, 4)
        self.assertEqual(edge.machine_config.mem_size_mib, 1024)
        self.assertEqual(edge.machine_config.disk_size, 2048)

    def test_invalid_ground_station_backhaul_values_are_rejected(self) -> None:
        for bandwidth_kbits, path_stretch in (
            (0, 1.3),
            (-1, 1.3),
            (10_000_000, 0.9),
            (10_000_000, float("inf")),
            (10_000_000, float("nan")),
        ):
            with self.subTest(
                bandwidth_kbits=bandwidth_kbits, path_stretch=path_stretch
            ):
                text_config = config_with_ground_station()
                text_config["network_params"].update(
                    {
                        "ground_station_bandwidth_kbits": bandwidth_kbits,
                        "ground_station_path_stretch": path_stretch,
                    }
                )
                with self.assertRaises(ValueError):
                    Config(text_config)

    def test_backhaul_fields_are_global_only(self) -> None:
        text_config = config_with_ground_station()
        text_config["ground_station"][0]["network_params"] = {
            "ground_station_bandwidth_kbits": 10_000_000,
            "ground_station_path_stretch": 1.3,
        }

        with self.assertRaises(ValueError):
            Config(text_config)

    def test_duplicate_ground_station_names_remain_rejected(self) -> None:
        text_config = config_with_ground_station()
        text_config["ground_station"].append(
            {"name": "ground", "lat": 78.2, "long": 15.4}
        )

        with self.assertRaisesRegex(ValueError, "duplicate names: ground"):
            Config(text_config)


if __name__ == "__main__":
    unittest.main()
