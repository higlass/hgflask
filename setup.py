from setuptools import setup, find_packages

install_requires = [
        'cython',
        'numpy',
        'pysam',
        'requests',
        'h5py',
        'pandas',
        'slugid',
        'sortedcontainers',
        'nose',
        'Click',
        'flask',
        'flask-cors',
        'hgtiles']

setup(
    name='hgflask',
    version='0.1.1',
    description='Portable higlass tile server',
    author='Nezar Abdennur',
    author_email='nabdennur@gmail.com',
    url='',
    packages=['hgflask'],
    install_requires=install_requires
)
