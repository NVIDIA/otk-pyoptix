#!/usr/bin/env python3

#
# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
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


from signal import default_int_handler
from telnetlib import DEBUGLEVEL
import optix
import os
import cupy  as cp    # CUDA bindings
import numpy as np    # Packing of structures in C-compatible format

import array
import ctypes         # C interop helpers
from PIL import Image, ImageOps # Image IO
from cuda.bindings import nvrtc

import path_util


#-------------------------------------------------------------------------------
#
# Util
#
#-------------------------------------------------------------------------------

def checkNVRTC(result):
    if result[0].value:
        raise RuntimeError("NVRTC error code={}({})".format(result[0].value, nvrtc.nvrtcGetErrorString(result[0])[1]))
    if len(result) == 1:
        return None
    elif len(result) == 2:
        return result[1]
    else:
        return result[1:]

class Logger:
    def __init__( self ):
        self.num_mssgs = 0

    def __call__( self, level, tag, mssg ):
        print( "[{:>2}][{:>12}]: {}".format( level, tag, mssg ) )
        self.num_mssgs += 1


def log_callback( level, tag, mssg ):
    print( "[{:>2}][{:>12}]: {}".format( level, tag, mssg ) )


def round_up( val, mult_of ):
    return val if val % mult_of == 0 else val + mult_of - val % mult_of


def  get_aligned_itemsize( formats, alignment ):
    names = []
    for i in range( len(formats ) ):
        names.append( 'x'+str(i) )

    temp_dtype = np.dtype( {
        'names'   : names,
        'formats' : formats,
        'align'   : True
        } )
    return round_up( temp_dtype.itemsize, alignment )


def array_to_device_memory( numpy_array, stream=cp.cuda.Stream() ):

    byte_size = numpy_array.size*numpy_array.dtype.itemsize

    h_ptr = ctypes.c_void_p( numpy_array.ctypes.data )
    d_mem = cp.cuda.memory.alloc( byte_size )
    d_mem.copy_from_async( h_ptr, byte_size, stream )
    return d_mem


def optix_version_gte( version ):
    if optix.version()[0] >  version[0]:
        return True
    if optix.version()[0] == version[0] and optix.version()[1] >= version[1]:
        return True
    return False


def compile_cuda( cuda_file ):

    compile_options = [
        b'-use_fast_math', 
        b'-lineinfo',
        b'-default-device',
        b'-std=c++11',
        b'-rdc',
        b'true',
        f'-I{path_util.include_path}'.encode(),
        f'-I{path_util.cuda_tk_path}'.encode()
    ]
    # Optix 7.0 compiles need path to system stddef.h
    # the value of optix.stddef_path is compiled in constant. When building
    # the module, the value can be specified via an environment variable, e.g.
    #   export PYOPTIX_STDDEF_DIR="/usr/include/linux"
    if not optix_version_gte( (7,1) ):
        compile_options.append( f'-I{path_util.stddef_path}' )
    print("pynvrtc compile options = {}".format(compile_options))

    with open( cuda_file, 'rb' ) as f:
        src = f.read()

    # Create program
    prog = checkNVRTC(nvrtc.nvrtcCreateProgram(src, cuda_file.encode(), 0, [], []))

    # Compile program
    checkNVRTC(nvrtc.nvrtcCompileProgram(prog, len(compile_options), compile_options))

    # Get PTX from compilation
    ptxSize = checkNVRTC(nvrtc.nvrtcGetPTXSize(prog))
    ptx = b" " * ptxSize
    checkNVRTC(nvrtc.nvrtcGetPTX(prog, ptx))
    return ptx


#-------------------------------------------------------------------------------
#
# Optix setup
#
#-------------------------------------------------------------------------------


width = 1024
height = 768


def create_ctx():
    print( "Creating optix device context ..." )

    # Note that log callback data is no longer needed.  We can
    # instead send a callable class instance as the log-function
    # which stores any data needed
    global logger
    logger = Logger()

    # OptiX param struct fields can be set with optional
    # keyword constructor arguments.
    ctx_options = optix.DeviceContextOptions(
            logCallbackFunction = logger,
            logCallbackLevel    = 4
            )

    # They can also be set and queried as properties on the struct
    if optix.version()[1] >= 2:
        ctx_options.validationMode = optix.DEVICE_CONTEXT_VALIDATION_MODE_ALL

    cu_ctx = 0
    return optix.deviceContextCreate( cu_ctx, ctx_options )
device_context = create_ctx()


def create_accel():
    accel_options = optix.AccelBuildOptions(
        buildFlags = int( optix.BUILD_FLAG_ALLOW_RANDOM_VERTEX_ACCESS),
        operation  = optix.BUILD_OPERATION_BUILD
        )

    radius = 0.4

    global vertices
    vertices = cp.array( [
        -1.5, -3.5, 0.0,
        -1.0,  0.5, 0.0,
         1.0,  0.5, 0.0,
         1.5, -3.5, 0.0
        ], dtype = 'f4' )

    global widths
    widths = cp.array( [
        0.01, radius, radius, 0.01
        ], dtype = 'f4' )

    global segment_indices
    segment_indices = cp.array( [ 0 ], dtype = 'int' )

    curve_input = optix.BuildInputCurveArray()

    curve_input.numPrimitives           = 1
    curve_input.numVertices             = len( vertices )//3
    curve_input.vertexBuffers           = [ vertices.data.ptr ]
    curve_input.widthBuffers            = [ widths.data.ptr ]
    curve_input.normalBuffers           = [ 0 ]
    curve_input.indexBuffer             = segment_indices.data.ptr
    curve_input.curveType               = optix.PRIMITIVE_TYPE_ROUND_CUBIC_BSPLINE
    curve_input.flag                    = optix.GEOMETRY_FLAG_NONE
    curve_input.primitiveIndexOffset    = 0

    gas_buffer_sizes = device_context.accelComputeMemoryUsage( [accel_options], [curve_input] )

    d_temp_buffer_gas   = cp.cuda.alloc( gas_buffer_sizes.tempSizeInBytes )
    d_gas_output_buffer = cp.cuda.alloc( gas_buffer_sizes.outputSizeInBytes )

    gas_handle = device_context.accelBuild(
        0,  # CUDA stream
        [ accel_options ],
        [ curve_input ],
        d_temp_buffer_gas.ptr,
        gas_buffer_sizes.tempSizeInBytes,
        d_gas_output_buffer.ptr,
        gas_buffer_sizes.outputSizeInBytes,
        []  # emitted properties
        )

    return ( gas_handle, d_gas_output_buffer )
gas_handle, d_gas_output_buffer = create_accel()


def set_pipeline_options():
    return optix.PipelineCompileOptions(
        usesMotionBlur                   = False,
        traversableGraphFlags            = int( optix.TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS ),
        numPayloadValues                 = 3,
        numAttributeValues               = 1,
        exceptionFlags                   = int( optix.EXCEPTION_FLAG_NONE ),
        pipelineLaunchParamsVariableName = "params",
        usesPrimitiveTypeFlags           = int( optix.PRIMITIVE_TYPE_FLAGS_ROUND_CUBIC_BSPLINE )
    )
pipeline_compile_options = set_pipeline_options()


def create_module():
    print( "Creating optix module ..." )

    module_compile_options = optix.ModuleCompileOptions(
        maxRegisterCount   = optix.COMPILE_DEFAULT_MAX_REGISTER_COUNT,
        optLevel           = optix.COMPILE_OPTIMIZATION_DEFAULT,
        debugLevel         = optix.COMPILE_DEBUG_LEVEL_DEFAULT
        )

    intersector_options = optix.BuiltinISOptions(
        builtinISModuleType = optix.PRIMITIVE_TYPE_ROUND_CUBIC_BSPLINE,
        usesMotionBlur = False
        )

    device_context.builtinISModuleGet(
        module_compile_options,
        pipeline_compile_options,
        intersector_options
        )

    curves_cu = os.path.join(os.path.dirname(__file__), 'curves.cu' )
    curves_ptx = compile_cuda( curves_cu )

    shading_module, log = device_context.moduleCreate(
        module_compile_options,
        pipeline_compile_options,
        curves_ptx
        )

    geometry_module = device_context.builtinISModuleGet(
        module_compile_options,
        pipeline_compile_options,
        intersector_options
        )

    print( "\tModule create log: <<<{}>>>".format( log ) )
    return geometry_module, shading_module
geometry_module, shading_module = create_module()


def create_program_groups():
    print( "Creating program groups ... " )

    raygen_prog_group_desc                          = optix.ProgramGroupDesc()
    raygen_prog_group_desc.raygenModule             = shading_module
    raygen_prog_group_desc.raygenEntryFunctionName  = "__raygen__rg"

    raygen_prog_groups, log = device_context.programGroupCreate(
        [ raygen_prog_group_desc ]
        )
    print( "\tProgramGroup raygen create log: <<<{}>>>".format( log ) )

    miss_prog_group_desc                        = optix.ProgramGroupDesc()
    miss_prog_group_desc.missModule             = shading_module
    miss_prog_group_desc.missEntryFunctionName  = "__miss__ms"
    miss_prog_groups, log = device_context.programGroupCreate(
            [ miss_prog_group_desc ]
            )
    print( "\tProgramGroup miss create log: <<<{}>>>".format( log ) )

    hitgroup_prog_group_desc                             = optix.ProgramGroupDesc()
    hitgroup_prog_group_desc.hitgroupModuleCH            = shading_module
    hitgroup_prog_group_desc.hitgroupEntryFunctionNameCH = "__closesthit__ch"
    hitgroup_prog_group_desc.hitgroupModuleIS            = geometry_module
    hitgroup_prog_group_desc.hitgroupEntryFunctionNameIS = "" # supplied by built-in module
    hitgroup_prog_groups, log = device_context.programGroupCreate(
            [ hitgroup_prog_group_desc ]
            )
    print( "\tProgramGroup hitgroup create log: <<<{}>>>".format( log ) )

    return [ raygen_prog_groups[0], miss_prog_groups[0], hitgroup_prog_groups[0] ]
program_groups = create_program_groups()


def create_pipeline():
    print( "Creating pipeline ... " )

    max_trace_depth = 1
    pipeline_link_options               = optix.PipelineLinkOptions()
    pipeline_link_options.maxTraceDepth = max_trace_depth

    log = ""
    pipeline = device_context.pipelineCreate(
            pipeline_compile_options,
            pipeline_link_options,
            program_groups,
            log
            )

    stack_sizes = optix.StackSizes()
    for prog_group in program_groups:
        if optix_version_gte( (7,7) ):
            optix.util.accumulateStackSizes( prog_group, stack_sizes, pipeline )
        else: 
            optix.util.accumulateStackSizes( prog_group, stack_sizes )

    ( dc_stack_size_from_trav, dc_stack_size_from_state, cc_stack_size ) = \
        optix.util.computeStackSizes(
            stack_sizes,
            max_trace_depth,
            0,  # maxCCDepth
            0,  # maxDCDepth
            )

    pipeline.setStackSize(
        dc_stack_size_from_trav,
        dc_stack_size_from_state,
        cc_stack_size,
        1   # maxTraversableDepth
    )

    return pipeline
pipeline = create_pipeline()


def create_sbt():
    print( "Creating sbt ... " )

    ( raygen_prog_group, miss_prog_group, hitgroup_prog_group ) = program_groups

    global d_raygen_sbt
    global d_miss_sbt

    header_format = '{}B'.format( optix.SBT_RECORD_HEADER_SIZE )

    #
    # raygen record
    #
    formats  = [ header_format ]
    itemsize = get_aligned_itemsize( formats, optix.SBT_RECORD_ALIGNMENT )
    dtype = np.dtype( {
        'names'   : ['header' ],
        'formats' : formats,
        'itemsize': itemsize,
        'align'   : True
        } )
    h_raygen_sbt = np.array( [ 0 ], dtype=dtype )
    optix.sbtRecordPackHeader( raygen_prog_group, h_raygen_sbt )
    global d_raygen_sbt
    d_raygen_sbt = array_to_device_memory( h_raygen_sbt )

    #
    # miss record
    #
    formats  = [ header_format, 'f4', 'f4', 'f4']
    itemsize = get_aligned_itemsize( formats, optix.SBT_RECORD_ALIGNMENT )
    dtype = np.dtype( {
        'names'   : ['header', 'r', 'g', 'b' ],
        'formats' : formats,
        'itemsize': itemsize,
        'align'   : True
        } )
    h_miss_sbt = np.array( [ (0, 0.0, 0.2, 0.6) ], dtype=dtype )
    optix.sbtRecordPackHeader( miss_prog_group, h_miss_sbt )
    global d_miss_sbt
    d_miss_sbt = array_to_device_memory( h_miss_sbt )

    #
    # hitgroup record
    #
    formats  = [ header_format ]
    itemsize = get_aligned_itemsize( formats, optix.SBT_RECORD_ALIGNMENT )
    dtype = np.dtype( {
        'names'   : ['header' ],
        'formats' : formats,
        'itemsize': itemsize,
        'align'   : True
        } )
    h_hitgroup_sbt = np.array( [ (0) ], dtype=dtype )
    optix.sbtRecordPackHeader( hitgroup_prog_group, h_hitgroup_sbt )
    global d_hitgroup_sbt
    d_hitgroup_sbt = array_to_device_memory( h_hitgroup_sbt )

    return optix.ShaderBindingTable(
        raygenRecord                = d_raygen_sbt.ptr,
        missRecordBase              = d_miss_sbt.ptr,
        missRecordStrideInBytes     = d_miss_sbt.mem.size,
        missRecordCount             = 1,
        hitgroupRecordBase          = d_hitgroup_sbt.ptr,
        hitgroupRecordStrideInBytes = d_hitgroup_sbt.mem.size,
        hitgroupRecordCount         = 1
        )
sbt = create_sbt()


def launch():
    print( "Launching ... " )

    width = 1024
    height = 768

    pix_bytes = width * height

    h_pix = np.zeros( ( width, height,4), 'B' )
    h_pix[0:width, 0:height] = [255, 128, 0, 255]
    d_pix = cp.array( h_pix )

    params = [
        ( 'u8', 'image',        d_pix.data.ptr ),
        ( 'u4', 'image_width',  width          ),
        ( 'u4', 'image_height', height         ),
        ( 'f4', 'cam_eye_x',    0              ),
        ( 'f4', 'cam_eye_y',    0              ),
        ( 'f4', 'cam_eye_z',    2.0            ),
        ( 'f4', 'cam_U_x',      1.10457        ),
        ( 'f4', 'cam_U_y',      0              ),
        ( 'f4', 'cam_U_z',      0              ),
        ( 'f4', 'cam_V_x',      0              ),
        ( 'f4', 'cam_V_y',      0.828427       ),
        ( 'f4', 'cam_V_z',      0              ),
        ( 'f4', 'cam_W_x',      0              ),
        ( 'f4', 'cam_W_y',      0              ),
        ( 'f4', 'cam_W_z',      -2.0           ),
        ( 'u8', 'trav_handle',  gas_handle     )
    ]

    formats = [ x[0] for x in params ]
    names   = [ x[1] for x in params ]
    values  = [ x[2] for x in params ]
    itemsize = get_aligned_itemsize( formats, 8 )
    params_dtype = np.dtype( {
        'names'   : names,
        'formats' : formats,
        'itemsize': itemsize,
        'align'   : True
        } )
    h_params = np.array( [ tuple(values) ], dtype=params_dtype )
    d_params = array_to_device_memory( h_params )

    stream = cp.cuda.Stream()
    optix.launch(
        pipeline,
        stream.ptr,
        d_params.ptr,
        h_params.dtype.itemsize,
        sbt,
        width,
        height,
        1 # depth
        )

    stream.synchronize()

    h_pix = cp.asnumpy( d_pix )
    return h_pix
pix = launch()


print( "Total number of log messages: {}".format( logger.num_mssgs ) )

pix = pix.reshape( ( height, width, 4 ) )     # PIL expects [ y, x ] resolution
img = ImageOps.flip( Image.fromarray( pix, 'RGBA' ) ) # PIL expects y = 0 at bottom
img.show()
img.save( 'my.png' )
