import pysoem
import struct
import time
from typing import Optional


class EthercatServo:
    """Simple EtherCAT CiA 402 servo interface."""

    CONTROL_WORD = 0x6040
    STATUS_WORD = 0x6041
    MODE_OF_OPERATION = 0x6060
    MODE_OF_OPERATION_DISPLAY = 0x6061
    TARGET_POSITION = 0x607A
    TARGET_VELOCITY = 0x60FF
    ACTUAL_POSITION = 0x6064
    DIGITAL_OUTPUTS = 0x60FE
    CONTROLLER_BITS = 0x06  # Fw (bit1) and Fb (bit2)

    def __init__(self, ifname: str, slave_pos: int = 0) -> None:
        self.ifname = ifname
        self.slave_pos = slave_pos
        self.master: Optional[pysoem.Master] = None
        self.slave = None

    def open(self) -> None:
        """Open EtherCAT master and configure slave."""
        self.master = pysoem.Master()
        self.master.open(self.ifname)
        if self.master.config_init() <= self.slave_pos:
            raise RuntimeError("Not enough slaves found")
        self.slave = self.master.slaves[self.slave_pos]
        self.master.config_map()
        self.master.state = pysoem.OP_STATE
        self.master.write_state()
        if self.master.state != pysoem.OP_STATE:
            raise RuntimeError("Unable to enter OP state")

    def close(self) -> None:
        if self.master:
            self.master.close()
            self.master = None

    def write_sdo(self, idx: int, subidx: int, val: int, size: int = 2) -> None:
        buf = val.to_bytes(size, byteorder="little", signed=False)
        self.slave.sdo_write(idx, subidx, buf)

    def read_sdo(self, idx: int, subidx: int, size: int = 2) -> int:
        buf = self.slave.sdo_read(idx, subidx)
        return int.from_bytes(buf[:size], byteorder="little", signed=False)

    def enable_operation(self) -> None:
        # switch on, enable voltage, quick stop, enable operation
        for cw in (0x06, 0x07, 0x0F):
            self.write_sdo(self.CONTROL_WORD, 0, cw)
            time.sleep(0.1)

    def set_mode(self, mode: int) -> None:
        self.write_sdo(self.MODE_OF_OPERATION, 0, mode, size=1)
        time.sleep(0.05)

    def set_target_position(self, pos: int) -> None:
        self.write_sdo(self.TARGET_POSITION, 0, pos, size=4)

    def set_target_velocity(self, vel: int) -> None:
        self.write_sdo(self.TARGET_VELOCITY, 0, vel, size=4)

    def read_actual_position(self) -> int:
        return self.read_sdo(self.ACTUAL_POSITION, 0, size=4)

    def start_motion(self) -> None:
        """Trigger motion in profile position mode."""
        # Set the "new set-point" and "change set immediately" bits
        # according to CiA 402 profile position mode.
        self.write_sdo(self.CONTROL_WORD, 0, 0x3F)
        time.sleep(0.05)

    def release_brake(self) -> None:
        """Release the motor brake using digital outputs if available."""
        try:
            state = self.read_sdo(self.DIGITAL_OUTPUTS, 1, size=1)
        except Exception:
            state = 0
        self.write_sdo(self.DIGITAL_OUTPUTS, 1, state | 0x01, size=1)
        time.sleep(0.05)

    def enable_controller(self) -> None:
        """Enable controller with Fw and Fb control bits."""
        try:
            state = self.read_sdo(self.DIGITAL_OUTPUTS, 1, size=1)
        except Exception:
            state = 0
        self.write_sdo(self.DIGITAL_OUTPUTS, 1, state | self.CONTROLLER_BITS, size=1)
        time.sleep(0.05)
