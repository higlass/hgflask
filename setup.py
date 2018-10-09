from setuptools import setup, find_packages

install_requires = [
        'requests',
        'diskcache',
        'slugid',
        'sortedcontainers',
        'nose',
        'Click',
        'flask',
        'flask-cors',
        'cytoolz',
        'sh',
        'cooler',
        'fusepy',
        'hgtiles']

setup(
    name='hgflask',
    version='0.1.2',
    description='Portable higlass tile server',
    author='Nezar Abdennur, Peter Kerpedjiev',
    author_email='nabdennur@gmail.com',
    url='',
    packages=['hgflask'],
    setup_requires=['flask'],
    install_requires=install_requires
)
