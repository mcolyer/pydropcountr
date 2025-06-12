"""
PyDropCountr - Python library for interacting with DropCountr.com

A clean, type-safe Python interface for accessing water usage data
from DropCountr.com water monitoring systems.
"""

from .pydropcountr import (
    DropCountrClient,
    ServiceConnection,
    UsageData,
    UsageResponse,
)

__version__ = "0.1.2"
__author__ = "Matthew Colyer"
__email__ = "matt@colyer.name"

__all__ = [
    "DropCountrClient",
    "ServiceConnection",
    "UsageData",
    "UsageResponse",
]
