import os

if os.getenv("SIMULATION") == "1":
    from servo_simulator import ServoSimulator as EthercatServo
else:
    from ethercat_servo import EthercatServo
import time

# Device name copied from get_adapter_name.py output
IFNAME = r"\Device\NPF_{99F254B6-0FBF-4B4D-B9DB-F9CA300B4CCF}"  # TwinCAT-Intel PCI Ethernet Adapter (Gigabit)
GEAR_RATIO = 30  # Example 30:1 planetary gearbox


def main():
    # Use the selected Ethernet adapter for EtherCAT communication
    servo = EthercatServo(ifname=IFNAME, slave_pos=0)
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
    main()
