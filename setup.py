from setuptools import setup, find_packages

install_requires = [
        'requests',
        'slugid',
        'sortedcontainers',
        'dask',
        'nose',
        'Click',
        'flask',
        'flask-cors',
        'hgtiles']

setup(
    name='hgflask',
    version='0.1.1',
    description='Portable higlass tile server',
    author='Nezar Abdennur, Peter Kerpedjiev',
    author_email='nabdennur@gmail.com',
    url='',
    packages=['hgflask'],
    install_requires=install_requires
)
