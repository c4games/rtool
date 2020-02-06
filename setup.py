#coding=utf-8

from setuptools import setup, find_packages

setup(
    name='rtool',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'PyYAML',
        'xlrd',
        'PyMySQL',
        'Pillow',
        'openpyxl<=2.5.12',
        'requests',
        'pathlib',
        'sh',
        'ply',
        "xxtea-py",
    ],
    entry_points='''
        [console_scripts]
        rtl=rtool.cmd:main
    ''',
)
