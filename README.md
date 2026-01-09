# PyOptiX

Python bindings for OptiX 7.

## Installation


### Dependencies

#### OptiX SDK
Install [OptiX SDK](https://developer.nvidia.com/designworks/optix/download) version 7.6 or newer.

#### CUDA SDK
Install [CUDA SDK](https://developer.nvidia.com/cuda-downloads) version 12.6 or newer required for examples, otherwise as required by your OptiX SDK.

#### Build system requirements:
* [cmake](https://cmake.org/)
* [pip](https://pypi.org/project/pip/)

#### Code sample dependencies
To run the PyOptiX examples or tests, the python modules specified in `PyOptiX/requirements.txt` must be installed:
* pytest
* cupy
* numpy
* Pillow
* cuda-python 

### Virtual Environment
In most cases, it makes sense to setup a python environment.  Below are examples of how to setup your environment via either`Conda` or `venv`.

#### `venv` Virtual Environment
Create and activate a new virtual environment:
```
python3 -m venv env
source env/bin/activate
```
Install all dependencies:
```
pip install -r requirements.txt
```

#### Conda Environment
Create an environment containing pre-requisites:
```
conda create -n pyoptix python numpy conda-forge::cupy pillow pytest
```
Activate the environment:
```
conda activate pyoptix
```

### Building and installing the `optix` Python module
Point `setuptools/CMake` to OptiX by setting the `OptiX_INSTALL_DIR` environment variable.

Linux:
```bash
export OptiX_INSTALL_DIR=/path/to/OptiX-SDK
cd optix
pip install .
```

Windows (PowerShell):
```powershell
$env:OptiX_INSTALL_DIR = 'C:\ProgramData\NVIDIA Corporation\OptiX SDK 9.0.0'
cd optix
pip install .
```

Windows (cmd):
```cmd
set OptiX_INSTALL_DIR=C:\ProgramData\NVIDIA Corporation\OptiX SDK 9.0.0
cd optix
pip install .
```

For advanced use cases, additional CMake arguments can be passed via `PYOPTIX_CMAKE_ARGS`.

When compiling against an OptiX 7.0 SDK an additional environment variable needs to be set
containing a path to the system's stddef.h location. E.g.
```
export PYOPTIX_STDDEF_DIR="/usr/include/linux"
```

### Windows: CUDA DLL Loading (Python 3.8+)

Python 3.8+ on Windows no longer uses `PATH` to find DLLs. PyOptiX will auto-detect
CUDA from the `CUDA_PATH` environment variable. If auto-detection fails, set `CUDA_BIN_DIR`:

```powershell
$env:CUDA_BIN_DIR = 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.9\bin'
```

## Running the Examples

Run the `hello` sample:
```
cd examples
python hello.py
```
If the example runs successfully, a green square will be rendered.

## Running the Test Suite

Test tests are using `pytest` and can be run from the test directory like this:
```
cd test
python -m pytest
```
