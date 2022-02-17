"""
licht - setup

@author: phdenzel
"""
import os
from setuptools import setup
from setuptools import find_packages

ld = {}
if os.path.exists("README.md"):
    ld['filename'] = "README.md"
    ld['content_type'] = "text/markdown"
elif os.path.exists("readme_src.org"):
    ld['filename'] = "readme_src.org"
    ld['content_type'] = "text/plain"

with open(file=ld['filename'], mode="r") as readme_f:
    ld['data'] = readme_f.read()

setup(
    # Metadata
    name="licht",
    author="Philipp Denzel",
    author_email="phdenzel@gmail.com",
    version="0.1.dev0",
    description=("A simple controller applet for Hue lights!"),
    long_description=ld['data'],
    long_description_content_type=ld['content_type'],
    license='GNU General Public License v3.0',
    url="https://github.com/phdenzel/licht",
    # keywords="",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],

    # Package
    install_requires=['requests',
                      'pyyaml',
                      'pycairo',
                      'pygobject',
                      ],
    packages=['licht'],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'licht = licht.__main__:main',
        ],
    },
    data_files=[
        ('assets', ['assets/icon.svg', 'assets/icon_dark.svg'])
    ],
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest'],
    # test_suite='tests'

)
