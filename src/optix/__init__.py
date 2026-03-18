# Copyright (c) 2022 NVIDIA CORPORATION All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""
PyOptiX: Python bindings for NVIDIA OptiX ray tracing SDK.

This package provides Python bindings for NVIDIA OptiX 7+, a high-performance
ray tracing API. OptiX is designed for optimal performance on NVIDIA GPUs.

Requirements:
    - OptiX SDK 7.6+ (must be installed separately)
    - CUDA Toolkit 10.0+ (must be installed separately)
    - NVIDIA GPU with ray tracing support

For installation instructions and documentation, visit:
https://github.com/NVIDIA/otk-pyoptix
"""

__version__ = "0.1.0"
__author__ = "Keith Morley"
__license__ = "BSD-3-Clause"

# Import everything from the native module
from ._optix import *

# Export all public symbols from _optix
__all__ = [name for name in dir() if not name.startswith('_')]
