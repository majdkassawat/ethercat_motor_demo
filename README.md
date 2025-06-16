# ethercat_motor_demo

This repository provides a minimal example for driving the
[IHSV60-30-40-48-EC-SC](https://www.alibaba.com/product-detail/IHSV60-30-40-48-EC-SC_1601039441757.html)
EtherCAT integrated servo motor.

## Requirements

- Python 3.11+
- [pysoem](https://github.com/bnjmnp/pysoem) (installed automatically via `pip`)
- An Ethernet interface connected to the servo (e.g. `eth0`)

Install dependencies:

```bash
pip install pysoem
```

## Usage

`demo.py` shows a basic sequence to enable the servo and move it to a target
position using the CiA&nbsp;402 profile position mode. After enabling operation
the script releases the brake with `release_brake()`, enables the controller via
`enable_controller()`, and calls `start_motion()` after setting the target
position to trigger the move.

```bash
python demo.py
```

Edit the network interface name and slave position in `demo.py` if needed.

## Files

- `ethercat_servo.py` – simple low level API for CiA&nbsp;402 EtherCAT servos
- `demo.py` – example script using `EthercatServo`
