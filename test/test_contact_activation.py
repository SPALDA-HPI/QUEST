"""Behavior tests for the opt-in satellite activation policy."""

import unittest

from celestial.activation import SatelliteActivation, activation_mask


class ActivationMaskTest(unittest.TestCase):
    """Catch accidental changes to which satellites Celestial boots."""

    def test_bbox_policy_preserves_existing_behavior(self) -> None:
        self.assertEqual(
            activation_mask(SatelliteActivation.BBOX, [True, False, True], []),
            [True, False, True],
        )

    def test_contact_policy_activates_only_directly_connected_satellites(self) -> None:
        self.assertEqual(
            activation_mask(
                SatelliteActivation.GROUND_STATION_CONTACT,
                [False, True, True, False],
                [0, 3],
            ),
            [True, False, False, True],
        )

    def test_contact_policy_deduplicates_links_from_multiple_ground_stations(self) -> None:
        self.assertEqual(
            activation_mask(
                SatelliteActivation.GROUND_STATION_CONTACT,
                [False, False, False],
                [1, 1],
            ),
            [False, True, False],
        )

    def test_contact_policy_rejects_an_out_of_range_satellite_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "satellite id 2 is out of range"):
            activation_mask(
                SatelliteActivation.GROUND_STATION_CONTACT,
                [False, False],
                [2],
            )


if __name__ == "__main__":
    unittest.main()
