# PyOptiX

Python bindings for NVIDIA OptiX 7+ ray tracing SDK.

PyOptiX provides high-performance Python bindings for NVIDIA OptiX, enabling GPU-accelerated ray tracing in Python applications. OptiX is a high-performance ray tracing API designed for optimal performance on NVIDIA GPUs.

## Quick Install

```bash
# Install from PyPI (OptiX headers are bundled)
pip install pyoptix
```

**Note**: You only need CUDA Toolkit installed. OptiX headers are automatically included.

## Installation


### Dependencies

#### CUDA Toolkit
Install [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) version 10.0 or newer.

**Note**: OptiX headers are automatically fetched during build. You do NOT need to install the OptiX SDK separately.

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

### Building PyOptiX from source

If you want to build from the git repository:

```bash
git clone https://github.com/NVIDIA/otk-pyoptix
cd otk-pyoptix
pip install .
```

OptiX headers will be automatically fetched from the [NVIDIA/optix-dev](https://github.com/NVIDIA/optix-dev) repository during the build process.

**Advanced Options:**
- Additional CMake arguments can be passed via `PYOPTIX_CMAKE_ARGS` environment variable

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
