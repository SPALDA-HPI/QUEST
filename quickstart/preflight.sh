#!/bin/sh

set -u

result=0

ok() {
    printf 'OK: %s\n' "$1"
}

fail() {
    printf 'ERROR: %s\n' "$1" >&2
    result=1
}

require_command() {
    if command -v "$1" >/dev/null 2>&1; then
        ok "$1 is available"
    else
        fail "$1 is missing"
    fi
}

if [ "$(uname -s)" = "Linux" ]; then
    ok "remote operating system is Linux"
else
    fail "the Celestial worker requires Linux"
fi

case "$(uname -m)" in
    x86_64|amd64) ok "remote architecture is x86_64" ;;
    *) fail "the Celestial worker requires x86_64/amd64" ;;
esac

for command_name in git make go python3 sudo firecracker wg ip iptables tc mount umount; do
    require_command "$command_name"
done

if command -v docker >/dev/null 2>&1; then
    fail "Docker is installed on the remote host; stop and contact the administrator"
else
    ok "Docker is absent from the remote host"
fi

if [ -c /dev/kvm ]; then
    ok "/dev/kvm exists"
else
    fail "/dev/kvm is missing; contact the HPI Scientific Compute Helpdesk"
fi

if [ -r /dev/kvm ] && [ -w /dev/kvm ]; then
    ok "/dev/kvm is readable and writable"
else
    fail "/dev/kvm permissions are insufficient; contact the HPI Scientific Compute Helpdesk"
fi

default_interface="$(ip route show default 2>/dev/null | awk 'NR == 1 { print $5 }')"
if [ -n "$default_interface" ]; then
    printf 'INFO: default network interface is %s\n' "$default_interface"
else
    fail "no default network interface was detected"
fi

exit "$result"
