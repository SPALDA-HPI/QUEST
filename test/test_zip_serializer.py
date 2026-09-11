import unittest

import celestial.config
import celestial.types
from celestial.zip_serializer import _INIT_HEAD, _init_from_str, _init_to_str


class InitRecordTest(unittest.TestCase):
    def test_machine_configuration_round_trips_in_nine_columns(self) -> None:
        machine = celestial.types.MachineID(1, 2, "example")
        config = celestial.config.MachineConfig(
            vcpu_count=1,
            mem_size_mib=256,
            disk_size=1,
            kernel="vmlinux-5.12.bin",
            rootfs="server.img",
            boot_parameters=["quiet", "console=ttyS0"],
        )

        record = _init_to_str(machine, config)
        restored_machine, restored_config = _init_from_str(record + "\r\n")

        self.assertEqual(len(_INIT_HEAD.split(",")), 9)
        self.assertEqual(len(record.split(",")), 9)
        self.assertEqual(restored_machine, machine)
        self.assertEqual(restored_config.vcpu_count, 1)
        self.assertEqual(restored_config.mem_size_mib, 256)
        self.assertEqual(restored_config.disk_size, 1)
        self.assertEqual(restored_config.kernel, "vmlinux-5.12.bin")
        self.assertEqual(restored_config.rootfs, "server.img")
        self.assertEqual(
            restored_config.boot_parameters,
            ["quiet", "console=ttyS0"],
        )


if __name__ == "__main__":
    unittest.main()
