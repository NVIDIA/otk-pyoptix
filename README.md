# PyOptiX

Python bindings for NVIDIA OptiX ray tracing SDK.

PyOptiX provides high-performance Python bindings for NVIDIA OptiX, enabling GPU-accelerated ray tracing in Python applications. OptiX is a high-performance ray tracing API designed for optimal performance on NVIDIA GPUs.

---
## Quick Installation

Installation of the OptiX 9.1 Python bindings can be performed directly via [pip](https://pypi.org/project/pip/).
 
```bash
pip install pyoptix
```
---
## Source Installation

For a local build and installation from source, including building against legacy OptiX releases, first clone this repository.  Then follow instructions below.
```
git clone https://github.com/NVIDIA/otk-pyoptix
```

### Dependencies

#### Python
Python versions 3.9+ are supported.

#### CUDA Toolkit
Install [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) version 10.0 or newer.

**Note**: OptiX headers are automatically fetched during build. You do NOT need to install the OptiX SDK separately to build the `optix` Python module.  However, the SDK will need to be installed to run the examples.

#### Build system requirements:
* [cmake](https://cmake.org/)
* [pip](https://pypi.org/project/pip/)


### Building PyOptiX from source

Once the otk-pyoptix repository has been cloned and all dependencies satisfied:

```bash
cd otk-pyoptix
pip install .
```

**Advanced Options:**
- Additional CMake arguments can be passed via `PYOPTIX_CMAKE_ARGS` environment variable

---
## Examples programs

Several example programs are included in the github repository to allow testing of the API and a starting point for user applications.

### Dependencies

To run the PyOptiX examples or tests, the python modules specified in `otk-pyoptix/requirements.txt` must be installed:
* pytest
* cupy
* numpy
* Pillow
* cuda-python (12.0 or newer recommended for OptiX 9.1)

In addition, the [OptiX SDK](https://developer.nvidia.com/designworks/optix/download) must be installed to allow JIT compilation of the example shaders.

### Virtual Environment
In most cases, it makes sense to setup a python environment.  Below are examples of how to setup your environment with required example dependencies via either`Conda` or `venv`.

#### `venv` Virtual Environment
Create and activate a new virtual environment, then install pre-requisites:
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

#### Conda Environment
Create and activate an environment containing pre-requisites:
```
conda create -n pyoptix python pytest conda-forge::cupy numpy pillow cuda-python
conda activate pyoptix
```

### Running the example programs

Run the `hello` sample:
```
cd otk-pyoptix/examples
python hello.py
```
If the example runs successfully, a green square will be rendered.

---
## Running the Test Suite

Test tests are using `pytest` and can be run from the test directory like this:
```
cd test
python -m pytest
```
