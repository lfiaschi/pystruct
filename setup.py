from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import numpy as np
import glob
import sys


pyxfolder='problems/'
standard='include'
others=["/home/lfiaschi/include"]



ext_modules = cythonize([
                                         Extension(
                         "utils",
                          [pyxfolder+"utils.pyx"],
                          include_dirs=[np.get_include(),standard]+others,
                          language="c++",
                          extra_compile_args=[],#['-O3'],
                          extra_link_args=[]#['-fopenmp']
                          ),
                                       
#               Extension(
#                         "_flow_graph",
#                          [pyxfolder+"_flow_graph.pyx"],
#                          include_dirs=[np.get_include(),standard]+others,
#                          language="c++",
#                          extra_compile_args=[],#['-O3'],
#                          extra_link_args=[]#['-fopenmp']
#                          ),
#               
#                Extension(
#                         "_superpixel_graph",
#                          [pyxfolder+"_superpixel_graph.pyx"],
#                          include_dirs=[np.get_include(),standard]+others,
#                          language="c++",
#                          extra_compile_args=[],#['-O3'],
#                          extra_link_args=[]#['-fopenmp']
#                          ),
               ])



    
setup(
  name="extmodule",
  ext_modules = ext_modules
)