# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

cmake_minimum_required(VERSION 3.17...3.31)

# Use scikit-build-core provided project name and version
project(
    ${SKBUILD_PROJECT_NAME}
    VERSION ${SKBUILD_PROJECT_VERSION}
    LANGUAGES CXX
)

#------------------------------------------------------------------------------
# Python and pybind11
#------------------------------------------------------------------------------

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

#------------------------------------------------------------------------------
# Fetch OptiX headers from NVIDIA/optix-dev repository
#------------------------------------------------------------------------------

include(FetchContent)

message(STATUS "Fetching OptiX headers from NVIDIA/optix-dev...")
FetchContent_Declare(
    optix_headers
    GIT_REPOSITORY https://github.com/NVIDIA/optix-dev
    GIT_TAG        v9.1.0
    GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(optix_headers)

# Create OptiX::OptiX interface target using fetched headers
add_library(OptiX::OptiX INTERFACE IMPORTED)
target_include_directories(OptiX::OptiX INTERFACE ${optix_headers_SOURCE_DIR}/include)

message(STATUS "Using OptiX headers from: ${optix_headers_SOURCE_DIR}/include")

# Find CUDA Toolkit (required for CUDA runtime)
if(NOT TARGET CUDA::cuda_driver)
  find_package(CUDAToolkit 10.0 REQUIRED)
endif()

#------------------------------------------------------------------------------
# Main build
#------------------------------------------------------------------------------

python_add_library(_optix MODULE src/main.cpp WITH_SOABI)

target_link_libraries(_optix PRIVATE
    OptiX::OptiX
    CUDA::cuda_driver
    CUDA::cudart
    pybind11::headers
)

target_compile_features(_optix PRIVATE cxx_std_17)

target_compile_definitions(_optix PRIVATE
    VERSION_INFO=${PROJECT_VERSION}
)

install(TARGETS _optix DESTINATION ${SKBUILD_PLATLIB_DIR}/optix)
