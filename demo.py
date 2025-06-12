from ethercat_servo import EthercatServo
import time


def main():
    servo = EthercatServo(ifname="eth0", slave_pos=0)
    servo.open()
    try:
        servo.set_mode(1)  # profile position
        servo.enable_operation()
        servo.set_target_position(10000)
        time.sleep(2)
        print("Actual position:", servo.read_actual_position())
    finally:
        servo.close()


if __name__ == "__main__":
    main()
