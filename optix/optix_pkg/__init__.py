# Copyright (c) 2022 NVIDIA CORPORATION All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""
Python bindings for NVIDIA OptiX.

On Windows with Python 3.8+, this module handles DLL loading for CUDA libraries.
Set the CUDA_BIN_DIR environment variable to your CUDA bin directory if needed,
or it will attempt to auto-detect from CUDA_PATH.
"""

import os
import sys

def _add_dll_directories():
    """Add CUDA DLL directories for Windows Python 3.8+."""
    if sys.platform != 'win32' or not hasattr(os, 'add_dll_directory'):
        return
    
    # Check for explicit CUDA_BIN_DIR first
    cuda_bin = os.environ.get('CUDA_BIN_DIR')
    if cuda_bin and os.path.isdir(cuda_bin):
        os.add_dll_directory(cuda_bin)
        return
    
    # Try to auto-detect from CUDA_PATH
    cuda_path = os.environ.get('CUDA_PATH')
    if cuda_path:
        cuda_bin = os.path.join(cuda_path, 'bin')
        if os.path.isdir(cuda_bin):
            os.add_dll_directory(cuda_bin)
            return
    
    # Try common CUDA installation locations
    for version in ['v12.9', 'v12.8', 'v12.6', 'v12.5', 'v12.4', 'v12.3', 'v12.2', 'v12.1', 'v12.0', 'v11.8']:
        cuda_bin = rf'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\{version}\bin'
        if os.path.isdir(cuda_bin):
            os.add_dll_directory(cuda_bin)
            return

_add_dll_directories()

# Import everything from the native module
from ._optix import *

