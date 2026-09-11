"""Select which satellite virtual machines should be running."""

from enum import Enum
import typing


class SatelliteActivation(Enum):
    """Supported policies for deciding whether a satellite VM is active."""

    BBOX = "bbox"
    GROUND_STATION_CONTACT = "ground_station_contact"


def activation_mask(
    policy: SatelliteActivation,
    in_bbox: typing.Iterable[bool],
    direct_contact_ids: typing.Iterable[int],
) -> typing.List[bool]:
    """Return one active/inactive flag per satellite.

    ``in_bbox`` is deliberately passed in even for contact mode.  Keeping the
    two inputs separate prevents a contact-driven experiment from changing
    the existing geographic calculation used by Celestial's visualizer.
    """
    bbox_flags = [bool(active) for active in in_bbox]
    if policy == SatelliteActivation.BBOX:
        return bbox_flags

    result = [False] * len(bbox_flags)
    for satellite_id in direct_contact_ids:
        if satellite_id < 0 or satellite_id >= len(result):
            raise ValueError(f"satellite id {satellite_id} is out of range")
        result[satellite_id] = True

    return result
