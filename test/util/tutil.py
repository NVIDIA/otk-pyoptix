# Copyright (c) 2022 NVIDIA CORPORATION All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.



import optix
import cupy as cp

ptx_string_old = '''
//
// Generated by NVIDIA NVVM Compiler
//
// Compiler Build ID: CL-29069683
// Cuda compilation tools, release 11.1, V11.1.74
// Based on LLVM 3.4svn
//

.version 7.1
.target sm_52
.address_size 64

	// .globl	__raygen__hello
.const .align 8 .b8 params[16];

.visible .entry __raygen__hello(

)
{
	.reg .pred 	%p<4>;
	.reg .b16 	%rs<5>;
	.reg .f32 	%f<39>;
	.reg .b32 	%r<13>;
	.reg .b64 	%rd<6>;


	// inline asm
	call (%r1), _optix_get_launch_index_x, ();
	// inline asm
	// inline asm
	call (%r2), _optix_get_launch_index_y, ();
	// inline asm
	// inline asm
	call (%rd1), _optix_get_sbt_data_ptr_64, ();
	// inline asm
	ld.const.u64 	%rd2, [params];
	cvta.to.global.u64 	%rd3, %rd2;
	ld.const.u32 	%r4, [params+8];
	mad.lo.s32 	%r5, %r4, %r2, %r1;
	ld.f32 	%f1, [%rd1];
	ld.f32 	%f2, [%rd1+4];
	ld.f32 	%f3, [%rd1+8];
	mov.f32 	%f4, 0f3F800000;
	min.ftz.f32 	%f5, %f1, %f4;
	mov.f32 	%f6, 0f00000000;
	max.ftz.f32 	%f7, %f6, %f5;
	min.ftz.f32 	%f8, %f2, %f4;
	max.ftz.f32 	%f9, %f6, %f8;
	min.ftz.f32 	%f10, %f3, %f4;
	max.ftz.f32 	%f11, %f6, %f10;
	lg2.approx.ftz.f32 	%f12, %f7;
	mul.ftz.f32 	%f13, %f12, 0f3ED55555;
	ex2.approx.ftz.f32 	%f14, %f13;
	lg2.approx.ftz.f32 	%f15, %f9;
	mul.ftz.f32 	%f16, %f15, 0f3ED55555;
	ex2.approx.ftz.f32 	%f17, %f16;
	lg2.approx.ftz.f32 	%f18, %f11;
	mul.ftz.f32 	%f19, %f18, 0f3ED55555;
	ex2.approx.ftz.f32 	%f20, %f19;
	setp.lt.ftz.f32	%p1, %f7, 0f3B4D2E1C;
	mul.ftz.f32 	%f21, %f7, 0f414EB852;
	fma.rn.ftz.f32 	%f22, %f14, 0f3F870A3D, 0fBD6147AE;
	selp.f32	%f23, %f21, %f22, %p1;
	setp.lt.ftz.f32	%p2, %f9, 0f3B4D2E1C;
	mul.ftz.f32 	%f24, %f9, 0f414EB852;
	fma.rn.ftz.f32 	%f25, %f17, 0f3F870A3D, 0fBD6147AE;
	selp.f32	%f26, %f24, %f25, %p2;
	setp.lt.ftz.f32	%p3, %f11, 0f3B4D2E1C;
	mul.ftz.f32 	%f27, %f11, 0f414EB852;
	fma.rn.ftz.f32 	%f28, %f20, 0f3F870A3D, 0fBD6147AE;
	selp.f32	%f29, %f27, %f28, %p3;
	min.ftz.f32 	%f30, %f23, %f4;
	max.ftz.f32 	%f31, %f6, %f30;
	mul.ftz.f32 	%f32, %f31, 0f43800000;
	cvt.rzi.ftz.u32.f32	%r6, %f32;
	mov.u32 	%r7, 255;
	min.u32 	%r8, %r6, %r7;
	min.ftz.f32 	%f33, %f26, %f4;
	max.ftz.f32 	%f34, %f6, %f33;
	mul.ftz.f32 	%f35, %f34, 0f43800000;
	cvt.rzi.ftz.u32.f32	%r9, %f35;
	min.u32 	%r10, %r9, %r7;
	min.ftz.f32 	%f36, %f29, %f4;
	max.ftz.f32 	%f37, %f6, %f36;
	mul.ftz.f32 	%f38, %f37, 0f43800000;
	cvt.rzi.ftz.u32.f32	%r11, %f38;
	min.u32 	%r12, %r11, %r7;
	mul.wide.u32 	%rd4, %r5, 4;
	add.s64 	%rd5, %rd3, %rd4;
	cvt.u16.u32	%rs1, %r12;
	cvt.u16.u32	%rs2, %r10;
	cvt.u16.u32	%rs3, %r8;
	mov.u16 	%rs4, 255;
	st.global.v4.u8 	[%rd5], {%rs3, %rs2, %rs1, %rs4};
	ret;
}
'''

ptx_string = '''

//
// Generated by NVIDIA NVVM Compiler
//
// Compiler Build ID: CL-29373293
// Cuda compilation tools, release 11.2, V11.2.67
// Based on NVVM 7.0.1
//

.version 7.2
.target sm_60
.address_size 64

	// .globl	__raygen__hello
.visible .const .align 8 .b8 params[16];

.visible .entry __raygen__hello()
{
	.reg .pred 	%p<4>;
	.reg .b16 	%rs<5>;
	.reg .f32 	%f<39>;
	.reg .b32 	%r<12>;
	.reg .b64 	%rd<6>;
	.loc	1 39 0
Lfunc_begin0:
	.loc	1 39 0


	.loc	1 41 26
	.loc	2 5675 5, function_name Linfo_string0, inlined_at 1 41 26
	// begin inline asm
	call (%r1), _optix_get_launch_index_x, ();
	// end inline asm
	.loc	2 5676 5, function_name Linfo_string0, inlined_at 1 41 26
	// begin inline asm
	call (%r2), _optix_get_launch_index_y, ();
	// end inline asm
Ltmp0:
	.loc	1 42 39
	.loc	2 5703 5, function_name Linfo_string1, inlined_at 1 42 39
	// begin inline asm
	call (%rd1), _optix_get_sbt_data_ptr_64, ();
	// end inline asm
Ltmp1:
	.loc	1 43 5
	ld.const.u64 	%rd2, [params];
	cvta.to.global.u64 	%rd3, %rd2;
	ld.const.u32 	%r4, [params+8];
	mad.lo.s32 	%r5, %r4, %r2, %r1;
	ld.f32 	%f1, [%rd1];
	ld.f32 	%f2, [%rd1+4];
	ld.f32 	%f3, [%rd1+8];
	.loc	3 121 22
	mov.f32 	%f4, 0f3F800000;
	min.ftz.f32 	%f5, %f1, %f4;
	.loc	3 121 12
	mov.f32 	%f6, 0f00000000;
	max.ftz.f32 	%f7, %f6, %f5;
	.loc	3 121 22
	min.ftz.f32 	%f8, %f2, %f4;
	.loc	3 121 12
	max.ftz.f32 	%f9, %f6, %f8;
	.loc	3 121 22
	min.ftz.f32 	%f10, %f3, %f4;
	.loc	3 121 12
	max.ftz.f32 	%f11, %f6, %f10;
	.loc	4 38 33
	lg2.approx.ftz.f32 	%f12, %f7;
	mul.ftz.f32 	%f13, %f12, 0f3ED55555;
	ex2.approx.ftz.f32 	%f14, %f13;
	.loc	4 38 56
	lg2.approx.ftz.f32 	%f15, %f9;
	mul.ftz.f32 	%f16, %f15, 0f3ED55555;
	ex2.approx.ftz.f32 	%f17, %f16;
	.loc	4 38 79
	lg2.approx.ftz.f32 	%f18, %f11;
	mul.ftz.f32 	%f19, %f18, 0f3ED55555;
	ex2.approx.ftz.f32 	%f20, %f19;
	setp.lt.ftz.f32 	%p1, %f7, 0f3B4D2E1C;
	mul.ftz.f32 	%f21, %f7, 0f414EB852;
	fma.rn.ftz.f32 	%f22, %f14, 0f3F870A3D, 0fBD6147AE;
	selp.f32 	%f23, %f21, %f22, %p1;
	setp.lt.ftz.f32 	%p2, %f9, 0f3B4D2E1C;
	mul.ftz.f32 	%f24, %f9, 0f414EB852;
	fma.rn.ftz.f32 	%f25, %f17, 0f3F870A3D, 0fBD6147AE;
	selp.f32 	%f26, %f24, %f25, %p2;
	setp.lt.ftz.f32 	%p3, %f11, 0f3B4D2E1C;
	mul.ftz.f32 	%f27, %f11, 0f414EB852;
	fma.rn.ftz.f32 	%f28, %f20, 0f3F870A3D, 0fBD6147AE;
	selp.f32 	%f29, %f27, %f28, %p3;
Ltmp2:
	.loc	4 61 25
	.loc	3 121 22, function_name Linfo_string2, inlined_at 4 61 25
	min.ftz.f32 	%f30, %f23, %f4;
	.loc	3 121 12, function_name Linfo_string2, inlined_at 4 61 25
	max.ftz.f32 	%f31, %f6, %f30;
	.loc	4 54 5, function_name Linfo_string2, inlined_at 4 61 25
	mul.ftz.f32 	%f32, %f31, 0f43800000;
	cvt.rzi.ftz.u32.f32 	%r6, %f32;
	.loc	5 870 10, function_name Linfo_string2, inlined_at 4 61 25
	min.u32 	%r7, %r6, 255;
Ltmp3:
	.loc	4 61 58
	.loc	3 121 22, function_name Linfo_string2, inlined_at 4 61 58
	min.ftz.f32 	%f33, %f26, %f4;
	.loc	3 121 12, function_name Linfo_string2, inlined_at 4 61 58
	max.ftz.f32 	%f34, %f6, %f33;
	.loc	4 54 5, function_name Linfo_string2, inlined_at 4 61 58
	mul.ftz.f32 	%f35, %f34, 0f43800000;
	cvt.rzi.ftz.u32.f32 	%r8, %f35;
	.loc	5 870 10, function_name Linfo_string2, inlined_at 4 61 58
	min.u32 	%r9, %r8, 255;
Ltmp4:
	.loc	4 61 91
	.loc	3 121 22, function_name Linfo_string2, inlined_at 4 61 91
	min.ftz.f32 	%f36, %f29, %f4;
	.loc	3 121 12, function_name Linfo_string2, inlined_at 4 61 91
	max.ftz.f32 	%f37, %f6, %f36;
	.loc	4 54 5, function_name Linfo_string2, inlined_at 4 61 91
	mul.ftz.f32 	%f38, %f37, 0f43800000;
	cvt.rzi.ftz.u32.f32 	%r10, %f38;
	.loc	5 870 10, function_name Linfo_string2, inlined_at 4 61 91
	min.u32 	%r11, %r10, 255;
Ltmp5:
	.loc	4 61 91
	mul.wide.u32 	%rd4, %r5, 4;
	add.s64 	%rd5, %rd3, %rd4;
Ltmp6:
	.loc	5 870 10, function_name Linfo_string2, inlined_at 4 61 91
	cvt.u16.u32 	%rs1, %r11;
Ltmp7:
	.loc	5 870 10, function_name Linfo_string2, inlined_at 4 61 58
	cvt.u16.u32 	%rs2, %r9;
Ltmp8:
	.loc	5 870 10, function_name Linfo_string2, inlined_at 4 61 25
	cvt.u16.u32 	%rs3, %r7;
Ltmp9:
	.loc	4 61 91
	mov.u16 	%rs4, 255;
	st.global.v4.u8 	[%rd5], {%rs3, %rs2, %rs1, %rs4};
	.loc	1 45 1
	ret;
Ltmp10:
Lfunc_end0:

}
	// .globl	__anyhit__noop
.visible .entry __anyhit__noop()
{

	.loc	1 48 0
Lfunc_begin1:
	.loc	1 48 0


	.loc	1 48 48
	ret;
Ltmp11:
Lfunc_end1:

}
	// .globl	__closesthit__noop
.visible .entry __closesthit__noop()
{

	.loc	1 51 0
Lfunc_begin2:
	.loc	1 51 0


	.loc	1 51 52
	ret;
Ltmp12:
Lfunc_end2:

}
	// .globl	__intersection__noop
.visible .entry __intersection__noop()
{

	.loc	1 54 0
Lfunc_begin3:
	.loc	1 54 0


	.loc	1 54 55
	ret;
Ltmp13:
Lfunc_end3:

}
	// .globl	__intersect__noop
.visible .entry __intersect__noop()
{

	.loc	1 57 0
Lfunc_begin4:
	.loc	1 57 0


	.loc	1 57 52
	ret;
Ltmp14:
Lfunc_end4:

}
	// .globl	__miss__noop
.visible .entry __miss__noop()
{

	.loc	1 60 0
Lfunc_begin5:
	.loc	1 60 0


	.loc	1 60 47
	ret;
Ltmp15:
Lfunc_end5:

}
	// .globl	__direct_callable__noop
.visible .entry __direct_callable__noop()
{

	.loc	1 63 0
Lfunc_begin6:
	.loc	1 63 0


	.loc	1 63 58
	ret;
Ltmp16:
Lfunc_end6:

}
	// .globl	__continuation_callable__noop
.visible .entry __continuation_callable__noop()
{

	.loc	1 66 0
Lfunc_begin7:
	.loc	1 66 0


	.loc	1 66 64
	ret;
Ltmp17:
Lfunc_end7:

}
	.file	1 "/home/kmorley/Code/optix_sdk/samples_exp/optixHello/draw_solid_color.cu"
	.file	2 "/home/kmorley/Code/optix_sdk/include/internal/optix_7_device_impl.h"
	.file	3 "/home/kmorley/Code/optix_sdk/samples_exp/sutil/vec_math.h"
	.file	4 "/home/kmorley/Code/optix_sdk/samples_exp/cuda/helpers.h"
	.file	5 "/usr/local/cuda/include/crt/math_functions.hpp"
	.section	.debug_str
	{
Linfo_string0:
.b8 95,90,78,55,51,95,73,78,84,69,82,78,65,76,95,53,49,95,116,109,112,120,102,116,95,48,48,49,48,102,48,57,54,95,48,48,48,48,48,48
.b8 48,48,95,55,95,100,114,97,119,95,115,111,108,105,100,95,99,111,108,111,114,95,99,112,112,49,95,105,105,95,51,101,52,98,52,55,50,54,49,57
.b8 111,112,116,105,120,71,101,116,76,97,117,110,99,104,73,110,100,101,120,69,118,0
Linfo_string1:
.b8 95,90,78,55,51,95,73,78,84,69,82,78,65,76,95,53,49,95,116,109,112,120,102,116,95,48,48,49,48,102,48,57,54,95,48,48,48,48,48,48
.b8 48,48,95,55,95,100,114,97,119,95,115,111,108,105,100,95,99,111,108,111,114,95,99,112,112,49,95,105,105,95,51,101,52,98,52,55,50,54,50,50
.b8 111,112,116,105,120,71,101,116,83,98,116,68,97,116,97,80,111,105,110,116,101,114,69,118,0
Linfo_string2:
.b8 95,90,50,49,113,117,97,110,116,105,122,101,85,110,115,105,103,110,101,100,56,66,105,116,115,102,0

	}
'''

class Logger:
    def __init__( self ):
        self.num_mssgs = 0
    
    def __call__( self, level, tag, mssg ):
        print( "[{:>2}][{:>12}]: {}".format( level, tag, mssg ) )
        self.num_mssgs += 1
    

def log_callback( level, tag, mssg ):
    print( "[{:>2}][{:>12}]: {}".format( level, tag, mssg ) )


def create_default_ctx():
    ctx_options = optix.DeviceContextOptions()

    cu_ctx = 0 
    return optix.deviceContextCreate( cu_ctx, ctx_options )
        

def optix_version_gte( version ):
    if optix.version()[0] >  version[0]:
        return True
    if optix.version()[0] == version[0] and optix.version()[1] >= version[1]:
        return True
    return False


def default_debug_level():
    if optix_version_gte( (7,1) ):
        return optix.COMPILE_DEBUG_LEVEL_DEFAULT
    else: 
        return optix.COMPILE_DEBUG_LEVEL_LINEINFO 


def create_default_module():
    ctx = create_default_ctx();
    module_opts   = optix.ModuleCompileOptions()
    pipeline_opts = optix.PipelineCompileOptions()
    mod = None
    if optix_version_gte( (7, 6) ):
        mod, log = ctx.moduleCreate(
			module_opts,
			pipeline_opts,
			ptx_string,
			)
    else:
        mod, log = ctx.moduleCreateFromPTX(
			module_opts,
			pipeline_opts,
			ptx_string,
			)
    return ( ctx, mod )
