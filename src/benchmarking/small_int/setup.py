from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [
    Extension(
        "small_int_benchmark_cython",
        ["small_int_benchmark_cython.pyx"],
        extra_compile_args=["-march=native", "-O3"],
    )
]
setup(
    name="Small int benchmark",
    ext_modules=cythonize(extensions),
)
