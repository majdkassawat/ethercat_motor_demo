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
- `CodexHardwareLoop` – .NET solution for hardware-in-the-loop testing

## Hardware-in-the-Loop Automation

The `CodexHardwareLoop` directory contains a Visual Studio solution that
automates running integration tests on a Windows PC attached to the servo.

### Usage

1. Install the .NET 8 SDK, Git and the GitHub CLI (`gh`).
2. Open `CodexHardwareLoop.sln` in Visual Studio and run the `LocalAgent` project,
   or execute `dotnet run --project CodexHardwareLoop/src/LocalAgent` from a
   command prompt.
3. The agent periodically fetches the repository. When a new commit is detected
   you will be prompted to press <kbd>Y</kbd> to deploy and execute the
   hardware‑in‑the‑loop tests.
4. Test results are converted into an Allure report and pushed to a branch named
   `results/<commit SHA>`.

The included integration tests call the Python demo script to verify that the
servo can be reached and that motion commands succeed.  Inspect the console
output and the generated Allure report when debugging problems.

## Running Tests with the Servo Simulator

A lightweight servo simulator is provided for exercising the integration tests
without real hardware.  It reads the included `JMC_DRIVE_V1.8.xml` ESI file to
recreate the slave's object dictionary and behavior.  Launch the simulator in
one terminal and then execute the tests from another:

```bash
# start the simulator using the ESI description
servo-sim --esi JMC_DRIVE_V1.8.xml

# run the .NET integration tests against the simulator
dotnet test CodexHardwareLoop/src/IntegrationTests/IntegrationTests.csproj \
    --configuration Release --no-build
```

The ESI file describes PDO and SDO entries, so the simulator knows that the
digital output object (`0x60FE`, subindex 1) is 32 bits wide.  The Python demo
and the tests can therefore interact with the simulated slave exactly like with
the real device.
