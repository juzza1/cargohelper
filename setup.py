from setuptools import setup, find_packages

import nch

setup(
    name=nch.APPNAME,
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'nch = nch.ui:main',
        ],
    },
    package_data={
        '': ['*.ico'],
    },
)
