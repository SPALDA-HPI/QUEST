"""Fair, non-preemptive ground-station antenna selection."""

import typing


SatelliteKey = typing.Tuple[int, int]


class AntennaScheduler:
    """Limit direct contacts independently for each ground station."""

    def __init__(
        self, antenna_numbers: typing.Sequence[typing.Optional[int]]
    ) -> None:
        self.antenna_numbers = list(antenna_numbers)
        self.assignments: typing.List[typing.Set[SatelliteKey]] = [
            set() for _ in antenna_numbers
        ]
        self.waiting_since: typing.List[typing.Dict[SatelliteKey, int]] = [
            {} for _ in antenna_numbers
        ]

    def select(
        self,
        timestamp_s: int,
        visible_by_ground_station: typing.Mapping[
            int, typing.Set[SatelliteKey]
        ],
    ) -> typing.Dict[int, typing.Set[SatelliteKey]]:
        """Return selected direct contacts for every ground station."""
        result: typing.Dict[int, typing.Set[SatelliteKey]] = {}

        for ground_station, limit in enumerate(self.antenna_numbers):
            visible = set(visible_by_ground_station.get(ground_station, set()))
            if limit is None:
                result[ground_station] = visible
                continue

            assigned = self.assignments[ground_station]
            assigned.intersection_update(visible)
            waiting_since = self.waiting_since[ground_station]
            for satellite in visible - assigned:
                waiting_since.setdefault(satellite, timestamp_s)

            available = limit - len(assigned)
            eligible = sorted(
                visible - assigned,
                key=lambda satellite: (
                    waiting_since[satellite],
                    satellite[0],
                    satellite[1],
                ),
            )
            newly_assigned = eligible[:available]
            assigned.update(newly_assigned)
            for satellite in newly_assigned:
                waiting_since.pop(satellite, None)

            result[ground_station] = set(assigned)

        return result
