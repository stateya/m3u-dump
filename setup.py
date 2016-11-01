#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
]

test_requirements = [
    # TODO: put package test requirements here
]
from setuptools.command.install import install as _install
class install(_install):
    def run(self):
        _install.run(self)
        print('hello')

setup(
    name='m3u_dump',
    version='1.0.0',
    description="Tool to dump music playlist and music in playlist",
    long_description=readme + '\n\n' + history,
    author="Shuuhei Tateya",
    author_email='stateya@gmail.com',
    url='https://github.com/stateya/m3u_dump',
    packages=[
        'm3u_dump',
    ],
    package_dir={'m3u_dump':
                 'm3u_dump'},
    entry_points={
        'console_scripts': [
            'm3u-dump=m3u_dump.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='m3u_dump',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    cmdclass={'install': install},
    tests_require=test_requirements
)
