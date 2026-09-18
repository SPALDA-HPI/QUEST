# DNS API

Every guest uses the gateway of its `/30` subnet as its Domain Name System
(DNS) server. The service supports IPv4 `A` records in the private
`.celestial` namespace.

| Machine | Name form | Example |
| --- | --- | --- |
| satellite | `<ID>.<SHELL>.celestial` | `12.1.celestial` |
| ground station | `<NAME>.gst.celestial` | `potsdam.gst.celestial` |
| information service | `info.celestial` | `http://info.celestial/self` |

Shell numbers start at 1. Ground stations use machine group 0 internally and
are addressed by their configured unique name.

DNS returns the address of a known configured machine even when that machine
is inactive or the current topology has no usable path to it. Name resolution
therefore does not prove reachability. An application must handle timeouts and can
query the [HTTP information API](http.md) for current state.
