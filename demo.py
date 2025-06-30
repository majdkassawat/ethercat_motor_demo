import os
import argparse
import time

# Example 30:1 planetary gearbox
GEAR_RATIO = 30

ENV_IFNAME = "ECAT_IFNAME"


def import_backend(backend: str):
    """Return Servo class and adapter helper for chosen backend."""
    if backend == "sim":
        from servo_simulator import ServoSimulator as EthercatServo

        def get_adapter_name(search: str = "default") -> str:
            return "sim"

    else:
        from ethercat_servo import EthercatServo
        from get_adapter_name import get_adapter_name

    return EthercatServo, get_adapter_name


def main(ifname: str | None = None, backend: str | None = None) -> None:
    """Run a small motion demo on the first EtherCAT slave or simulator."""

    if backend is None:
        backend = "sim" if os.getenv("SIMULATION") == "1" else "hw"

    EthercatServo, get_adapter_name = import_backend(backend)

    if ifname is None:
        ifname = os.environ.get(ENV_IFNAME)
    if ifname is None:
        ifname = get_adapter_name()

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
    parser.add_argument(
        "--backend",
        choices=["hw", "sim"],
        help="Select 'hw' for real hardware or 'sim' for the simulator",
        default=None,
    )
    args = parser.parse_args()
    main(args.ifname, args.backend)
