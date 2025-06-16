import asyncio
import os
import re
import pytest

from device_controller import DeviceController


@pytest.fixture(autouse=True)
def _simulation_env(monkeypatch):
    monkeypatch.setenv("SIMULATION", "1")


@pytest.fixture
def device():
    dc = DeviceController()
    asyncio.run(dc.connect())
    yield dc
    dc.close()


def test_self_test_should_pass(device):
    result = asyncio.run(device.run_self_test())
    assert result == "OK"


def test_demo_script_reports_position(device):
    pos = asyncio.run(device.run_demo())
    assert pos >= 0
