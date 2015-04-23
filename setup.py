from __future__ import print_function

import re
import ast
import sys

from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('src/pvc/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1))
    )

if (2, 7) <= sys.version_info < (3, 0):
    dialog_package = 'python2-pythondialog'
elif sys.version_info >= (3, 0):
    dialog_package = 'pythondialog'
else:
    print('Unsupported Python version')
    sys.exit(1)

setup(
    name='pvc',
    version=version,
    description='Python vSphere Client with a dialog(1) interface',
    long_description=open('README.rst').read(),
    author='Marin Atanasov Nikolov',
    author_email='dnaeon@gmail.com',
    license='BSD',
    url='https://github.com/dnaeon/pvc',
    download_url='https://github.com/dnaeon/pvc/releases',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    scripts=[
        'src/pvc-tui',
    ],
    install_requires=[
        '{} >= 3.2.1'.format(dialog_package),
        'humanize >= 0.5.1',
        'pyvmomi >= 5.5.0-2014.1.1',
        'requests >= 2.6.0',
        'vconnector >= 0.3.7',
    ]
)
