import xml.etree.ElementTree as ET
import time
from typing import Dict, Tuple


class ServoSimulator:
    """In-memory CiA-402 servo simulator using values from an ESI file."""

    DEFAULT_INDICES = {
        0x6040,  # control word
        0x6041,  # status word
        0x6060,  # mode of operation
        0x6061,  # mode display
        0x607A,  # target position
        0x60FF,  # target velocity
        0x6064,  # actual position
        0x60FE,  # digital outputs
    }

    def __init__(self, ifname: str = "", slave_pos: int = 0, esi_path: str = "JMC_DRIVE_V1.8.xml") -> None:
        self.esi_path = esi_path
        # map of (index, subindex) -> value
        self.objects: Dict[Tuple[int, int], int] = {}
        self.opened = False

    def _parse_esi(self) -> None:
        tree = ET.parse(self.esi_path)
        root = tree.getroot()
        for obj in root.iter("Object"):
            index_txt = obj.findtext("Index")
            if not index_txt:
                continue
            idx = int(index_txt.replace("#x", ""), 16)
            if idx not in self.DEFAULT_INDICES:
                continue
            sub_items = obj.findall("Info/SubItem")
            if sub_items:
                for sub_idx, sub in enumerate(sub_items):
                    val_txt = sub.findtext("Info/DefaultData")
                    val = int(val_txt, 16) if val_txt else 0
                    self.objects[(idx, sub_idx)] = val
            else:
                val_txt = obj.findtext("Info/DefaultData")
                val = int(val_txt, 16) if val_txt else 0
                self.objects[(idx, 0)] = val

    # Basic API -------------------------------------------------------------
    def open(self) -> None:
        self._parse_esi()
        self.opened = True

    def close(self) -> None:
        self.opened = False

    def write_sdo(self, idx: int, subidx: int, val: int, size: int = 2) -> None:
        self.objects[(idx, subidx)] = val

    def read_sdo(self, idx: int, subidx: int, size: int = 2) -> int:
        return self.objects.get((idx, subidx), 0)

    # High-level helpers ---------------------------------------------------
    def enable_operation(self) -> None:
        for cw in (0x06, 0x07, 0x0F):
            self.write_sdo(0x6040, 0, cw)
            time.sleep(0.01)

    def set_mode(self, mode: int) -> None:
        self.write_sdo(0x6060, 0, mode)
        time.sleep(0.01)

    def set_target_position(self, pos: int) -> None:
        self.write_sdo(0x607A, 0, pos)

    def set_target_position_after_gearbox(self, output_pos: int, gear_ratio: float) -> None:
        self.set_target_position(int(output_pos * gear_ratio))

    def set_target_velocity(self, vel: int) -> None:
        self.write_sdo(0x60FF, 0, vel)

    def read_actual_position(self) -> int:
        return self.read_sdo(0x6064, 0)

    def start_motion(self) -> None:
        # When starting motion we simply copy target position to actual position
        self.write_sdo(0x6040, 0, 0x3F)
        target = self.read_sdo(0x607A, 0)
        self.write_sdo(0x6064, 0, target)

    def release_brake(self) -> None:
        state = self.read_sdo(0x60FE, 1)
        self.write_sdo(0x60FE, 1, state | 0x01)

    def enable_controller(self) -> None:
        state = self.read_sdo(0x60FE, 1)
        self.write_sdo(0x60FE, 1, state | 0x06)
        time.sleep(0.01)
