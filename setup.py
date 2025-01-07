import os
import subprocess
import sys

import setuptools
from setuptools.command.build_ext import build_ext

# constants to use 
cwd = os.path.dirname(os.path.abspath(__file__))

class CMakeExtension(setuptools.Extension):
    def __init__(self, name, sourcedir='', cmake_args=(), exclude_arch=False):
        setuptools.Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)
        self.cmake_args = cmake_args
        self.exclude_arch = exclude_arch

class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(['cmake', '--version'])
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

def clone_submodule():
    """ Clones the git submodules found .gitmodules in project directory. """
    subprocess.check_call(["git", "submodule", "update", "--init", "--recursive"], cwd=cwd)

def main():
    # clone submodule
    clone_submodule()
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
        install_requires=["numpy", "pyvista"],
        packages=["manifold"],
        package_data={"manifold":["_manifold_internal*.so", "*.pyi"]}
    )

if __name__=="__main__":
    main()