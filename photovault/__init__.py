"""
PhotoVault - Sequential Image Steganography Library
Hide secrets sequentially across your own cover images.
"""

from .core import (
    hide_secret,
    reveal_secret,
    PhotoVaultError,
    CompressionError,
    CapacityError,
)

__all__ = [
    "hide_secret",
    "reveal_secret",
    "PhotoVaultError",
    "CompressionError",
    "CapacityError",
]
__version__ = "1.0.0"
