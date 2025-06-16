import importlib
import sys
import types

import pytest


def get_servo_module(monkeypatch):
    """Import ethercat_servo with a stubbed pysoem module."""
    sys.modules.pop('ethercat_servo', None)
    pysoem_stub = types.SimpleNamespace()
    pysoem_stub.Master = type('Master', (), {})
    pysoem_stub.OP_STATE = 8
    monkeypatch.setitem(sys.modules, 'pysoem', pysoem_stub)
    module = importlib.import_module('ethercat_servo')
    return module


def test_write_sdo(monkeypatch):
    mod = get_servo_module(monkeypatch)

    class DummySlave:
        def __init__(self):
            self.calls = []
        def sdo_write(self, idx, subidx, buf):
            self.calls.append((idx, subidx, buf))

    servo = mod.EthercatServo(ifname='eth0')
    servo.slave = DummySlave()

    servo.write_sdo(0x1234, 0x56, 0x789A, size=2)
    assert servo.slave.calls == [(0x1234, 0x56, b"\x9a\x78")]


def test_read_sdo(monkeypatch):
    mod = get_servo_module(monkeypatch)

    class DummySlave:
        def sdo_read(self, idx, subidx):
            assert idx == 0x1234
            assert subidx == 0
            return b"\x34\x12"

    servo = mod.EthercatServo(ifname='eth0')
    servo.slave = DummySlave()
    val = servo.read_sdo(0x1234, 0, size=2)
    assert val == 0x1234


def test_enable_operation(monkeypatch):
    mod = get_servo_module(monkeypatch)
    servo = mod.EthercatServo(ifname='eth0')

    calls = []
    def fake_write_sdo(idx, subidx, val, size=2):
        calls.append((idx, subidx, val, size))
    monkeypatch.setattr(servo, 'write_sdo', fake_write_sdo)
    monkeypatch.setattr(mod.time, 'sleep', lambda x: None)

    servo.enable_operation()

    expected = [
        (mod.EthercatServo.CONTROL_WORD, 0, 0x06, 2),
        (mod.EthercatServo.CONTROL_WORD, 0, 0x07, 2),
        (mod.EthercatServo.CONTROL_WORD, 0, 0x0F, 2),
    ]
    assert calls == expected
