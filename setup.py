from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


with open(path.join(here, "README.rst"), "r") as f:
    long_description = f.read()

setup(
    name="usfm_utils",
    version="1.0.6",
    description="Utilities for handling USFM files, from parsing to converting.",
    long_description=long_description,
    url="https://github.com/unfoldingWord-dev/USFM-Utils",
    author="unfoldingWord",
    author_email="ethantkoenig@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    keywords=["usfm", "html"],
    packages=find_packages(),
    install_requires=["enum34", "future", "ply"],
    test_suite="tests"
)
