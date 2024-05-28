from glob import glob
from os.path import basename, splitext
from setuptools import find_packages, setup

install_requires = [
    'pandas',
    'numpy',
    ]



setup (
    name             = 'toy', 
    packages=find_packages(where='src'),
    version          = '1.0.0',
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    install_requires = install_requires,
    author           = 'jhahn',
    author_email     = 'jhahncs@gmail.com',
    description      = 'Desc'
)