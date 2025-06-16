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


```bash
python demo.py
```

Edit the network interface name and slave position in `demo.py` if needed.

`release_brake()` and `enable_controller()` access the digital outputs object
(`0x60FE`, subindex 1).  According to the included ESI file the value is a
32‑bit unsigned integer, so the demo writes four bytes when toggling the
control bits.  The exact object index and bit assignments may vary, so consult
your servo's documentation if these helpers do not work out of the box.

## Files

- `ethercat_servo.py` – simple low level API for CiA&nbsp;402 EtherCAT servos
- `demo.py` – example script using `EthercatServo`
