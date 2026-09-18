# Guest Time

QUEST does not replace the guest clock. Timekeeping depends on the selected
guest kernel, root filesystem, host clock, and whether the run spans multiple
workers.

Accurate clocks matter when an application compares timestamps written by
different guests. Network Time Protocol (NTP) synchronizes against a network
server. Precision Time Protocol (PTP) can expose the host clock through KVM and
avoids a separate request stream from every guest.

The supplied builder configures PTP support. The guest kernel requires:

```config
CONFIG_PTP_1588_CLOCK=y
CONFIG_PTP_1588_CLOCK_KVM=y
```

When the host and nested-virtualization environment support it, the guest sees
`/dev/ptp0` and its startup script can configure a time service such as
`chrony`. The current builder performs its time setup before the application
entry point, `app.sh`, runs.

PTP availability is environment-dependent. If the worker reports that it is
not using `/dev/ptp0`, capture the message and ask the administrator to inspect
the host clock source. Students must not rewrite a shared remote host's clock
source or kernel boot parameters.

For an experiment, record the clock method and measure remaining offset. A
successful PTP startup does not prove that multiple physical hosts have zero
clock error.
