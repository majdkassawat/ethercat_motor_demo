import argparse
import os
import tkinter as tk
from tkinter import ttk

if os.getenv("SIMULATION") == "1":
    from servo_simulator import ServoSimulator as EthercatServo
else:
    from ethercat_servo import EthercatServo

from get_adapter_name import get_adapter_name

# Indices of registers displayed in the GUI.  Each entry contains
# (index, subindex, name, size_in_bytes).
REGISTER_DEFS = [
    (0x6040, 0, "controlword", 2),
    (0x6041, 0, "statusword", 2),
    (0x6060, 0, "op_mode", 1),
    (0x6061, 0, "op_mode_display", 1),
    (0x607A, 0, "target_position", 4),
    (0x60FF, 0, "target_velocity", 4),
    (0x6064, 0, "actual_position", 4),
    (0x60FE, 1, "physical_outputs", 4),
]

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

        reg_frame = ttk.LabelFrame(frame, text="Registers")
        reg_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        self.register_vars = {}
        for r, (idx, sub, name, size) in enumerate(REGISTER_DEFS):
            ttk.Label(reg_frame, text=f"{name} (0x{idx:04X}:{sub})").grid(row=r, column=0, sticky="w")
            var = tk.StringVar(value="n/a")
            ttk.Label(reg_frame, textvariable=var).grid(row=r, column=1, sticky="w")
            self.register_vars[(idx, sub)] = (var, size)

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
                for idx, sub, name, size in REGISTER_DEFS:
                    var, sz = self.register_vars[(idx, sub)]
                    try:
                        val = self.servo.read_sdo(idx, sub, size=sz)
                        var.set(str(val))
                    except Exception:
                        var.set("err")
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
        ifname = get_adapter_name()

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
