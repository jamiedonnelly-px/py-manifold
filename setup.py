import setuptools
import os
import re
import sys
import platform
import subprocess
import warnings
import shutil

from distutils.version import LooseVersion
from setuptools.command.build_ext import build_ext

# constants to use 
cwd = os.path.dirname(os.path.abspath(__file__))
third_party_path = os.path.join(cwd, "third_party")

class CMakeExtension(setuptools.Extension):
    def __init__(self, name, sourcedir='', cmake_args=(), exclude_arch=False):
        setuptools.Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)
        self.cmake_args = cmake_args
        self.exclude_arch = exclude_arch

class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                             ", ".join(e.name for e in self.extensions))
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        print(f"Extension dir: {extdir}", file=sys.stderr)
        
        # Create the build directory
        os.makedirs(extdir, exist_ok=True)
        
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}'
        ]
        cmake_args.extend(ext.cmake_args)
        
        build_temp = os.path.join(self.build_temp, ext.name)
        os.makedirs(build_temp, exist_ok=True)
        
        subprocess.check_call(['cmake'] + cmake_args + [ext.sourcedir], cwd=build_temp)
        subprocess.check_call(['cmake', '--build', '.'], cwd=build_temp)
        
        # Find and copy the built extension
        for root, _, files in os.walk(build_temp):
            for file in files:
                if file.endswith('.so') and '_manifold_internal' in file:
                    src = os.path.join(root, file)
                    dst = os.path.join(extdir, file)
                    print(f"Copying {src} -> {dst}", file=sys.stderr)
                    shutil.copy(src, dst)
                    return
        
        print("Warning: Could not find built extension!", file=sys.stderr)

def main():
    # run setup 
    setuptools.setup(
        name="manifold",
        version="0.0.1",
        author="Jamie Donnelly",
        author_email="jamie.donnelly@physicsx.ai",
        description="Python bindings for the C++ library: https://github.com/hjwdzh/ManifoldPlus",
        ext_modules=[CMakeExtension("_manifold_internal")],
        ext_package="manifold",
        cmdclass=dict(build_ext=CMakeBuild),
        python_requires=">=3.10",
        install_requires=["numpy"],
        packages=["manifold"],
        package_data={"manifold":["_manifold_internal*.so"]}
    )

if __name__=="__main__":
    main()