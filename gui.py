import argparse
import os
import tkinter as tk
from tkinter import ttk

if os.getenv("SIMULATION") == "1":
    from servo_simulator import ServoSimulator as EthercatServo
else:
    from ethercat_servo import EthercatServo

from get_adapter_name import get_first_adapter

class ServoGUI:
    def __init__(self, root, servo):
        self.root = root
        self.servo = servo
        self.connected = False

        self.target_var = tk.IntVar(value=0)
        self.pos_var = tk.StringVar(value="n/a")
        self.status_var = tk.StringVar(value="Disconnected")

        frame = ttk.Frame(root, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Target position:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.target_var).grid(row=0, column=1, sticky="ew")

        ttk.Button(frame, text="Connect", command=self.connect).grid(row=1, column=0, sticky="ew")
        ttk.Button(frame, text="Move", command=self.move).grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="Actual position:").grid(row=2, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.pos_var).grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Status:").grid(row=3, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.status_var).grid(row=3, column=1, sticky="w")

        root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(200, self.update)

    def connect(self):
        if self.connected:
            return
        try:
            self.servo.open()
            self.servo.set_mode(1)
            self.servo.enable_operation()
            self.servo.release_brake()
            self.servo.enable_controller()
            self.status_var.set("Connected")
            self.connected = True
        except Exception as exc:
            self.status_var.set(f"Error: {exc}")

    def move(self):
        if not self.connected:
            return
        try:
            pos = self.target_var.get()
            self.servo.set_target_position(pos)
            self.servo.start_motion()
        except Exception as exc:
            self.status_var.set(f"Error: {exc}")

    def update(self):
        if self.connected:
            try:
                pos = self.servo.read_actual_position()
                self.pos_var.set(str(pos))
                status = self.servo.read_sdo(0x6041, 0)
                if status & 0x08:
                    self.status_var.set("Fault")
            except Exception as exc:
                self.status_var.set(f"Error: {exc}")
        self.root.after(200, self.update)

    def close(self):
        try:
            if self.connected:
                self.servo.close()
        finally:
            self.root.destroy()


def main(ifname=None, simulate=False):
    simulate = simulate or os.getenv("SIMULATION") == "1"
    if ifname is None:
        ifname = os.environ.get("ECAT_IFNAME")
    if ifname is None:
        ifname = get_first_adapter()

    if simulate:
        servo = EthercatServo(ifname=ifname, slave_pos=0)
    else:
        servo = EthercatServo(ifname=ifname, slave_pos=0)

    root = tk.Tk()
    root.title("EtherCAT Servo GUI")
    ServoGUI(root, servo)
    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EtherCAT servo GUI")
    parser.add_argument("--ifname", help="network interface", default=None)
    parser.add_argument("--simulate", action="store_true", help="use simulator")
    args = parser.parse_args()
    main(args.ifname, args.simulate)
