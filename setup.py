import re
import ast

from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('src/pvc/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1))
    )

setup(
    name='pvc',
    version=version,
    description='Python vSphere Client',
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
        'humanize >= 0.5.1',
        'pythondialog >= 3.2.1',
        'pyvmomi >= 5.5.0-2014.1.1',
        'requests >= 2.6.0',
        'vconnector >= 0.3.7',
    ]
)
