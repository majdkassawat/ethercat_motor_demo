from ethercat_servo import EthercatServo
import time

# Device name copied from get_adapter_name.py output
IFNAME = r"\Device\NPF_{99F254B6-0FBF-4B4D-B9DB-F9CA300B4CCF}"  # TwinCAT-Intel PCI Ethernet Adapter (Gigabit)


def main():
    # Use the selected Ethernet adapter for EtherCAT communication
    servo = EthercatServo(ifname=IFNAME, slave_pos=0)
    servo.open()
    try:
        servo.set_mode(1)             # profile-position mode
        servo.enable_operation()
        servo.release_brake()
        servo.enable_controller()
        servo.set_target_position(10000)
        servo.start_motion()
        time.sleep(2)
        print("Actual position:", servo.read_actual_position())
    finally:
        servo.close()


if __name__ == "__main__":
    main()
