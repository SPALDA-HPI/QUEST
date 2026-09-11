# HTTP Information API

The worker exposes a read-only Hypertext Transfer Protocol (HTTP) information
service to each guest through its gateway. Workloads built with the repository
builder can use `http://info.celestial`.

All examples below are guest-side `GET` requests. Identifiers use shell 1 and
the ground-station name `potsdam` only as examples.

## `GET /self`

Returns the requester identity. A ground station includes `type: "gst"`, its
numeric ID, and configured name. A satellite includes `type: "sat"`, its shell
and satellite ID, and current `active` flag.

```json
{
  "type": "sat",
  "active": true,
  "identifier": {"shell": 1, "id": 12}
}
```

## `GET /info`

Returns every shell and ground station with identifiers and satellite active
flags. This can be large for a full constellation; prefer the narrower routes
below inside frequent workload loops.

## `GET /shell/{shell}`

Returns all configured satellites in one numeric shell and each current
`active` value.

## `GET /shell/{shell}/{satellite}`

Returns one satellite identity and its current `active` value.

## `GET /gst/{name}`

Returns one named ground station:

```json
{
  "type": "gst",
  "identifier": {"id": 0, "name": "potsdam"}
}
```

## `GET /path/{source-shell}/{source-id}/{target-shell}/{target-id}`

Use `gst` as a shell and a configured name as the ID for a ground station. For
example:

```text
GET /path/gst/potsdam/1/12
```

The response describes the selected end-to-end path:

```json
{
  "source": {"id": 0, "name": "potsdam"},
  "target": {"shell": 1, "id": 12},
  "delay_us": 10000,
  "bandwidth_kbits": 10000,
  "blocked": false,
  "segments": []
}
```

`delay_us` is one-way delay in microseconds. `bandwidth_kbits` is the path
bottleneck in kilobits per second. `blocked` reports whether the current route
is unavailable. `segments` contains the individual links when a route has
multiple hops.

The API reports the topology model applied by the coordinator. It is not a
measurement of physical Internet round-trip time. The quickstart validator
compares this reported value with guest pings.
