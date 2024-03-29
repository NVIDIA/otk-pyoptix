#
# Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

find_package(Python REQUIRED)

# temporary guard while awaiting 8.0 fixes
if(OPTIX_VERSION VERSION_GREATER 7.7)
    return()
endif()

file(COPY optix examples requirements.txt test DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

if(UNIX)
    add_custom_command(OUTPUT env.timestamp
        COMMAND ${Python_EXECUTABLE} -m venv env
        COMMAND bash -c "source ./env/bin/activate"
        COMMAND ./env/bin/pip install -r requirements.txt
        COMMAND ${CMAKE_COMMAND} -E touch env.timestamp
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Creating virtual environment for PyOptiX build")
else()
    add_custom_command(OUTPUT env.timestamp
        COMMAND ${Python_EXECUTABLE} -m venv env
        COMMAND powershell ./env/Scripts/Activate.ps1
        COMMAND powershell ./env/Scripts/pip.exe install -r requirements.txt
        COMMAND ${CMAKE_COMMAND} -E touch env.timestamp
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Creating virtual environment for PyOptiX build")
endif()

add_custom_target(PyOptiX ALL 
    ${CMAKE_COMMAND} -E env PYOPTIX_CMAKE_ARGS="-DOptiX_INSTALL_DIR=${OptiX_INSTALL_DIR}" 
    ${Python_EXECUTABLE} setup.py build 
    WORKING_DIRECTORY optix
    DEPENDS env.timestamp)