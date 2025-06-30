# ethercat_motor_demo

This repository provides a minimal example for driving the
[IHSV60-30-40-48-EC-SC](https://www.alibaba.com/product-detail/IHSV60-30-40-48-EC-SC_1601039441757.html)
EtherCAT integrated servo motor.

## Requirements

- Python 3.11+
- [pysoem](https://github.com/bnjmnp/pysoem) (installed automatically via `pip` from `requirements.txt`)
- An Ethernet interface connected to the servo (e.g. `eth0`)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage


```bash
python demo.py [--backend {hw,sim}] [--ifname IFNAME]
```

To experiment with a simple graphical interface, launch `gui.py`. Use
`--simulate` to run against the built-in servo simulator:

```bash
python gui.py --simulate
```

By default the script uses the adapter returned by
`get_adapter_name()` from `get_adapter_name.py`.  Use the optional
`--backend` argument to select between the real servo (`hw`) and the simulator
(`sim`).  The default is `hw`.  You can override the adapter name via the
`ECAT_IFNAME` environment variable or with `--ifname IFNAME`.  Adjust the slave
position in `demo.py` if needed.
Pass ``"search"`` to ``get_adapter_name()`` to list available adapters and use
the first one found.

Use `set_target_position_after_gearbox()` when commanding positions at the
load side of a gearbox.  Pass the desired output position and the gearbox ratio
to let the helper translate it to a motor shaft position automatically.

`release_brake()` and `enable_controller()` access the digital outputs object
(`0x60FE`, subindex 1).  According to the included ESI file the value is a
32‑bit unsigned integer, so the demo writes four bytes when toggling the
control bits.  The simulator loads the same ESI description to emulate the
drive, therefore the object layout is identical when running tests.  The exact
object index and bit assignments may vary between servos, so consult your
servo's documentation if these helpers do not work out of the box.

## Files

 - `ethercat_servo.py` – simple low level API for CiA&nbsp;402 EtherCAT servos
   including `set_target_position_after_gearbox()` for gear ratios
 - `demo.py` – example script using `EthercatServo`
- `hardware_loop.py` – Python agent for hardware-in-the-loop testing

## Register Map

The demo interacts with a few CiA&nbsp;402 objects via SDO access.  The table
below summarizes the indices referenced by the code.  Names are taken from the
included `JMC_DRIVE_V1.8.xml` file.  Consult the ESI description for the full
object dictionary.

| Index (subindex) | ESI name          | Access | Purpose |
|------------------|------------------|--------|---------|
| `0x6040`         | `controlword`     | rw     | Control word used to switch states and trigger motion |
| `0x6041`         | `statusword`      | ro     | Current state of the drive |
| `0x6060`         | `op_mode`         | rw     | Selects the desired mode of operation |
| `0x6061`         | `op_mode_display` | ro     | Shows the active mode of operation |
| `0x607A`         | `target_position` | rw     | Target position command |
| `0x60FF`         | `target_velocity` | rw     | Target velocity command |
| `0x6064`         | `actual_position` | ro     | Position feedback value |
| `0x60FE:1`       | `physical_outputs`| rw     | Digital outputs for brake release and controller enable |

The graphical interface (`gui.py`) includes a *Registers* panel that shows these
values in real time when connected to a servo or the simulator.

## Hardware-in-the-Loop Automation

The `hardware_loop.py` script
automates running integration tests on a PC attached to the servo.

### Usage

1. Install Git and Python. The optional Allure CLI can be used to create HTML
   reports.
2. Run `python hardware_loop.py`. Add `-y` to run automatically.
3. The agent periodically fetches the repository. When a new commit is detected
   you will be prompted to press <kbd>Y</kbd> to execute the hardware tests.
   Use `-y` to skip the prompt and execute the tests immediately.
4. If available, an Allure report is generated and pushed to a branch named
   `results/<commit SHA>`.

The included integration tests call the Python demo script to verify that the
servo can be reached and that motion commands succeed.  Inspect the console
output and the generated Allure report when debugging problems.

### Test Layout

Tests that run purely in simulation live under `tests/software/` and are
executed automatically by CI.  Hardware integration tests reside in
`tests/hardware/` and must be run manually on a machine connected to the servo.

### Quick Logging Helper

`run_hw_tests.py` can be used to execute the hardware integration tests once and
store the console output in the `outputs/` directory.  After the tests finish
the log file is committed to the repository automatically.  Adjust the `config`
file to set your Git username and email if required.

```bash
python run_hw_tests.py
```


## Running Tests with the Servo Simulator

A lightweight servo simulator is provided for exercising the integration tests
without real hardware.  It reads the included `JMC_DRIVE_V1.8.xml` ESI file to
recreate the slave's object dictionary and behavior.  Launch the simulator in
one terminal and then execute the tests from another:

```bash
# start the simulator using the ESI description
servo-sim --esi JMC_DRIVE_V1.8.xml

# run the Python integration tests against the simulator
pytest tests/software/test_device_controller.py --alluredir TestResults
```

The ESI file describes PDO and SDO entries, so the simulator knows that the
digital output object (`0x60FE`, subindex 1) is 32 bits wide.  The Python demo
and the tests can therefore interact with the simulated slave exactly like with
the real device.
## License

This project is released under the [MIT License](LICENSE).


