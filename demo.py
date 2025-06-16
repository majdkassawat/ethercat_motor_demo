import os

if os.getenv("SIMULATION") == "1":
    from servo_simulator import ServoSimulator as EthercatServo
else:
    from ethercat_servo import EthercatServo

import argparse

import time

from ethercat_servo import EthercatServo
from get_adapter_name import get_first_adapter

# Environment variable to override the detected adapter name
ENV_IFNAME = "ECAT_IFNAME"

# Example 30:1 planetary gearbox
GEAR_RATIO = 30


def main(ifname: str | None = None) -> None:
    """Run a small motion demo on the first EtherCAT slave."""

    if ifname is None:
        ifname = os.environ.get(ENV_IFNAME)
    if ifname is None:
        ifname = get_first_adapter()

    servo = EthercatServo(ifname=ifname, slave_pos=0)
    servo.open()
    try:
        servo.set_mode(1)             # profile-position mode
        servo.enable_operation()
        servo.release_brake()
        servo.enable_controller()
        servo.set_target_position_after_gearbox(10000, GEAR_RATIO)
        servo.start_motion()
        time.sleep(2)
        print("Actual position:", servo.read_actual_position())
    finally:
        servo.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Minimal EtherCAT servo demo")
    parser.add_argument(
        "-i",
        "--ifname",
        metavar="IFNAME",
        help="Ethernet adapter name used for EtherCAT communication",
    )
    args = parser.parse_args()
    main(args.ifname)
