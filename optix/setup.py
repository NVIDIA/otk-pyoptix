# Copyright (c) 2022 NVIDIA CORPORATION All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import os
import re
import sys
import platform
import shlex
import subprocess

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion
import shutil


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        # required for auto-detection of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        # Copy __init__.py to the package directory
        init_src = os.path.join(os.path.dirname(__file__), 'optix_pkg', '__init__.py')
        init_dst = os.path.join(extdir, '__init__.py')
        os.makedirs(extdir, exist_ok=True)
        shutil.copy2(init_src, init_dst)

        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        # Dedicated variable for OptiX path - handles spaces without quoting issues
        if "OPTIX_INSTALL_DIR" in os.environ:
            cmake_args += ["-DOptiX_INSTALL_DIR=" + os.environ['OPTIX_INSTALL_DIR']]

        if "PYOPTIX_CMAKE_ARGS" in os.environ:
            cmake_args += shlex.split(os.environ[ 'PYOPTIX_CMAKE_ARGS' ])

        # the following is only needed for 7.0 compiles, because the optix device header of that
        # first version included stddef.h.
        if "PYOPTIX_STDDEF_DIR" in os.environ:
            cmake_args += [ "-DOptiX_STDDEF_DIR={}".format(os.environ[ 'PYOPTIX_STDDEF_DIR' ]) ]

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        print( "CMAKE CMD: <<<{}>>>".format( ' '.join( ['cmake', ext.sourcedir] + cmake_args ) ) )
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)



setup(
    name='optix',
    version='0.0.1',
    author='Keith Morley',
    author_email='kmorley@nvidia.com',
    description='Python bindings for NVIDIA OptiX',
    long_description='',
    ext_modules=[CMakeExtension('optix._optix')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)
