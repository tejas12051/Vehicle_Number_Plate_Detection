import setuptools

VERSION = '0.0.1'
PROJECT_NAME = 'Vehicle Number Plate Detection'
AUTHOR_NAME = 'Tejas Patil'
DESCRIPTION = ' This is a Vehicle Number Plate Detection'

setuptools.setup(
    version=VERSION,
    PROJECT_NAME = PROJECT_NAME,
    author= AUTHOR_NAME,
    description= DESCRIPTION,
    package_dir= {"":"vnpd"},
    packages= setuptools.find_packages(where='vnpd')
)