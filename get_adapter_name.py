# get_adapter_name.py
"""
List available network adapters detected by PySOEM and
return one you can pass to EthercatServo(ifname=...).

Works with both PySOEM ≥1.0 (str fields) and earlier versions (bytes fields).
"""

from __future__ import annotations
import pysoem

# Default adapter name used when no search is performed
IFNAME = r"\Device\NPF_{99F254B6-0FBF-4B4D-B9DB-F9CA300B4CCF}"


def _to_str(value: str | bytes) -> str:
    """Convert bytes → str if needed (PySOEM ≤0.3) else return unchanged."""
    return value.decode() if isinstance(value, bytes) else value


def list_adapters() -> None:
    """Print all adapters (name – description)."""
    for ad in pysoem.find_adapters():
        name = _to_str(ad.name)
        desc = _to_str(ad.desc)
        print(f"{name}  —  {desc}")


def get_adapter_name(search: str = "default") -> str:
    """Return the adapter name.

    Parameters
    ----------
    search : str
        Pass ``"search"`` to print all available adapters and return the
        first suitable adapter.  Any other value (including ``"default"``)
        returns :data:`IFNAME`.
    """
    if search == "search":
        list_adapters()
        try:
            return get_first_adapter()
        except RuntimeError:
            return IFNAME
    return IFNAME


def get_first_adapter(exclude_loopback: bool = True) -> str:
    """
    Return the first suitable adapter name.

    Parameters
    ----------
    exclude_loopback : bool
        Skip adapters whose name contains 'loopback' (case-insensitive).

    Raises
    ------
    RuntimeError
        If no suitable adapter is found.
    """
    for ad in pysoem.find_adapters():
        name = _to_str(ad.name)
        if exclude_loopback and "loopback" in name.lower():
            continue
        return name
    raise RuntimeError("No suitable Ethernet adapter found.")


if __name__ == "__main__":
    list_adapters()
