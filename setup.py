#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="delcom904x",
    version="0.2.1",
    description="A python class to control Delcom USBLMP Products 904x multi-color, USB, visual signal indicators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aaron Linville",
    author_email="aaron@linville.org",
    url="https://github.com/linville/delcom904x",
    py_modules=["delcom904x"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: ISC License (ISCL)",
    ],
    license="ISC",
    install_requires=["hidapi"],
    python_requires=">=3.5",
    setup_requires=["wheel"],
    scripts=['control_delcom904x.py'],
)
