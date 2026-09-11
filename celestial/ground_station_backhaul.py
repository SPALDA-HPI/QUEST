"""Static direct ground-station backhaul topology helpers."""

import itertools
import math
import typing

import celestial.config
import celestial.types


EARTH_RADIUS_M = 6_371_000.0
FIBER_PROPAGATION_M_S = 200_000_000.0


def ground_station_delay_us(
    source: celestial.config.GroundStation,
    target: celestial.config.GroundStation,
    path_stretch: float,
) -> int:
    """Return deterministic one-way fiber propagation delay."""
    source_lat = math.radians(source.lat)
    target_lat = math.radians(target.lat)
    latitude_delta = target_lat - source_lat
    longitude_delta = math.radians(target.lng - source.lng)
    haversine = (
        math.sin(latitude_delta / 2.0) ** 2
        + math.cos(source_lat)
        * math.cos(target_lat)
        * math.sin(longitude_delta / 2.0) ** 2
    )
    central_angle = 2.0 * math.asin(min(1.0, math.sqrt(haversine)))
    distance_m = EARTH_RADIUS_M * central_angle
    return round(
        distance_m * path_stretch / FIBER_PROPAGATION_M_S * 1_000_000.0
    )


def ground_station_backhaul_links(
    stations: typing.Sequence[celestial.config.GroundStation],
    bandwidth_kbits: int,
    path_stretch: float,
) -> typing.Iterator[
    typing.Tuple[
        celestial.types.MachineID_dtype,
        celestial.types.MachineID_dtype,
        celestial.types.Link_dtype,
    ]
]:
    """Yield one direct link update for every unordered station pair."""
    indexed_stations = list(enumerate(stations))
    for (source_index, source), (target_index, target) in itertools.combinations(
        indexed_stations, 2
    ):
        source_id = celestial.types.MachineID(0, source_index, source.name)
        target_id = celestial.types.MachineID(0, target_index, target.name)
        yield (
            source_id,
            target_id,
            celestial.types.Link(
                latency_us=ground_station_delay_us(
                    source, target, path_stretch
                ),
                bandwidth_kbits=bandwidth_kbits,
                blocked=False,
                next_hop=target_id,
                prev_hop=source_id,
            ),
        )
