import pathlib
import unittest

import toml

from celestial.activation import SatelliteActivation
from celestial.config import Config


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]


class QuickstartConfigTest(unittest.TestCase):
    def test_example_exercises_retained_quest_features(self) -> None:
        config_path = REPOSITORY_ROOT / "quickstart" / "quickstart.toml"
        self.assertTrue(config_path.exists(), "quickstart configuration is missing")
        config = Config(toml.load(config_path))

        self.assertEqual(config.duration, 120)
        self.assertEqual(config.resolution, 5)
        self.assertEqual(
            config.satellite_activation,
            SatelliteActivation.GROUND_STATION_CONTACT,
        )
        self.assertEqual(len(config.shells), 1)
        self.assertEqual(len(config.ground_stations), 2)
        self.assertEqual(
            [station.name for station in config.ground_stations],
            ["potsdam", "berlin"],
        )
        self.assertEqual(
            [station.antenna_number for station in config.ground_stations],
            [2, 1],
        )
        self.assertEqual(config.ground_station_bandwidth_kbits, 1_000_000)
        self.assertEqual(config.ground_station_path_stretch, 1.3)


if __name__ == "__main__":
    unittest.main()
